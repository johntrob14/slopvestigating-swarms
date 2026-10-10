"""Explicitly gated future runs, durable append-only records, and offline preparation."""
import copy
import itertools
import json
import math
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .cases import ROOT, digest, load_case, prepare
from .simulator import Simulator, Unsupported

DEFAULT_CONFIG = ROOT / 'experiments/peer_requests/config.json'


def load_config(path=DEFAULT_CONFIG):
    return json.loads(Path(path).read_text())


def matrix(config):
    return itertools.product(config['cases'], config['conditions'], config['scopes'])


def prepare_all(config, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    entries = []
    for case, condition, scope in matrix(config):
        packet = prepare(case, condition, scope, config.get('checkpoint', 'request_read'))
        name = f'{case}--{condition}--{scope}.json'
        (destination / name).write_text(json.dumps(packet, ensure_ascii=False, indent=2))
        entries.append({'file': name, 'prompt_sha256': packet['prompt_sha256'],
                        'changed_message_indices': packet['changed_message_indices']})
    manifest = {'kind': 'offline_prompt_preparation', 'config': config,
                'config_sha256': digest(config), 'prompts': entries}
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    return manifest


def replay_original(case):
    """Verify recorded tool outputs and memory writes without invoking any model."""
    item, run = load_case(case)
    messages = run['transcripts'][0]['messages']
    expected = {m['tool_call_id']: m['content'] for m in messages if m['role'] == 'tool'}
    simulator = Simulator(case)
    observations = []
    for i, message in enumerate(messages[item['prefix_end_exclusive']:], item['prefix_end_exclusive']):
        for call in message.get('tool_calls') or []:
            result = simulator.call(call['function'], call['arguments'])
            if call['function'] == 'bash':
                if result['content'] != expected[call['id']]:
                    raise ValueError('Recorded observation mismatch')
            observations.append({'source_index': i, 'name': call['function'], 'mode': result['mode']})
    return {'kind': 'offline_fixture_replay', 'case_id': case, 'source_sha256': item['sha256'],
            'tool_calls': len(observations), 'observations': observations,
            'shared_writes': [e for e in simulator.events if e['kind'] == 'shared_write'],
            'note': 'Fixture consistency check; no fresh model generations or replication evidence.'}


def live_gate(config, execute):
    execution, sampling = config['execution'], config['sampling']
    if config.get('simulator_variant', 'standard') not in ('standard', 'network_probe_approximation'):
        raise ValueError('Unknown simulator variant')
    if not execute or execution.get('enabled') is not True:
        raise ValueError('Live execution is disabled. No API call was made.')
    for key in ('samples_per_condition', 'max_requests'):
        value = execution.get(key)
        if type(value) is not int or value < 1:
            raise ValueError('Set a positive integer execution.' + key)
    for key in ('max_tokens', 'max_turns'):
        value = sampling.get(key)
        if type(value) is not int or value < 1:
            raise ValueError('Set a positive integer sampling.' + key)
    for key in ('budget_usd', 'reserve_usd_per_request'):
        value = execution.get(key)
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or value <= 0:
            raise ValueError('Set a positive finite execution.' + key)
    if execution['reserve_usd_per_request'] > execution['budget_usd']:
        raise ValueError('Per-request reserve exceeds the total budget')
    if config.get('provider', {}).get('allow_fallbacks') is not False:
        raise ValueError('Provider fallback must remain disabled')
    for case, condition, scope in matrix(config):
        prepare(case, condition, scope, config.get('checkpoint', 'request_read'))
        item, _ = load_case(case)
        if config['models'][case] != item['original_model']:
            raise ValueError('Model substitution requires an explicit experiment/code change')
    if not os.environ.get('OPENROUTER_API_KEY'):
        raise ValueError('OPENROUTER_API_KEY is unset')


def append(path, row):
    with Path(path).open('a') as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def records(path):
    if not Path(path).exists():
        return []
    # A torn final row needs manual review; never guess about paid work.
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def git_state():
    # Fixed developer commands only. No model content can reach this subprocess.
    def read(args):
        result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
        return result.stdout.strip() if result.returncode == 0 else None
    return {'commit': read(['git', 'rev-parse', 'HEAD']),
            'status': read(['git', 'status', '--porcelain'])}


def run(config, destination, execute=False, completer=None):
    live_gate(config, execute)
    if completer is None:
        from .openrouter import complete
        completer = complete
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    # Prevent two collaborators/processes from spending against the same ledger.
    lock = destination / '.running'
    try:
        descriptor = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ValueError('Run lock exists; inspect prior requests before removing it') from exc
    os.close(descriptor)
    try:
        return _run_locked(config, destination, completer)
    finally:
        lock.unlink()


def _run_locked(config, destination, completer):
    trace_path, result_path = destination / 'events.jsonl', destination / 'rollouts.jsonl'
    manifest_path = destination / 'manifest.json'
    config_hash = digest(config)
    implementation = {str(p.relative_to(ROOT)): digest(p.read_text())
                      for p in sorted((ROOT / 'swarmstudy').glob('*.py'))}
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text())
        if previous['config_sha256'] != config_hash or previous['implementation'] != implementation:
            raise ValueError('Use a new output directory for a changed configuration')
    else:
        manifest_path.write_text(json.dumps({
            'config': config, 'config_sha256': config_hash, 'implementation': implementation,
            'git': git_state(), 'started_utc': datetime.now(timezone.utc).isoformat()}, indent=2))
    history = records(trace_path)
    requests = [r for r in history if r['kind'] == 'request']
    responses = {r['request_id']: r for r in history if r['kind'] == 'response'}
    if any(r['request_id'] not in responses for r in requests):
        raise ValueError('Prior request has unknown billing state; review it before resuming')
    costs = [r.get('cost_usd') for r in responses.values()]
    if any(c is None for c in costs):
        raise ValueError('Prior response has unknown cost; review it before resuming')
    spent, request_count = sum(costs), len(requests)
    finished = {r['trial_id']: r for r in records(result_path)}
    started = {r['trial_id'] for r in history if r['kind'] == 'trial_start'}
    if started - finished.keys():
        raise ValueError('Prior trial lacks a summary; review it before resuming')
    execution, sampling = config['execution'], config['sampling']
    for case, condition, scope in matrix(config):
        for sample in range(execution['samples_per_condition']):
            trial_id = digest([config_hash, case, condition, scope, sample])
            if trial_id in finished:
                continue
            packet = prepare(case, condition, scope, config.get('checkpoint', 'request_read'))
            messages = copy.deepcopy(packet['messages'])
            simulator = Simulator(case, condition, config.get('simulator_variant', 'standard'))
            if config.get('checkpoint') == 'sharing_decision':
                simulator.restore_prefix(packet['prefix_end_exclusive'])
            meta = {'trial_id': trial_id, 'case_id': case, 'condition': condition,
                    'scope': scope, 'sample_idx': sample, 'prompt_sha256': packet['prompt_sha256'],
                    'checkpoint': config.get('checkpoint', 'request_read'),
                    'simulator_variant': config.get('simulator_variant', 'standard')}
            append(trace_path, dict(meta, kind='trial_start', prepared=packet,
                                   restored_prefix_events=getattr(simulator, 'prefix_events', []),
                                   initial_virtual_files=copy.deepcopy(simulator.files)))
            status, reason, trial_cost = 'incomplete', 'turn_limit', 0.0
            for turn in range(sampling['max_turns']):
                if request_count >= execution['max_requests']:
                    reason = 'request_limit'; break
                if spent + execution['reserve_usd_per_request'] > execution['budget_usd']:
                    reason = 'budget_reserve'; break
                payload = {'model': config['models'][case], 'messages': copy.deepcopy(messages),
                           'tools': packet['tools'], 'tool_choice': 'auto',
                           'temperature': sampling['temperature'], 'max_tokens': sampling['max_tokens'],
                           'reasoning': sampling['reasoning'], 'provider': config['provider'],
                           'usage': {'include': True}, 'stream': False}
                if sampling.get('seed') is not None:
                    payload['seed'] = sampling['seed'] + sample
                request_id = f'{trial_id}:{turn}'
                append(trace_path, dict(meta, kind='request', request_id=request_id, payload=payload))
                request_count += 1
                try:
                    raw = completer(payload, os.environ['OPENROUTER_API_KEY'])
                except Exception as exc:
                    append(trace_path, dict(meta, kind='transport_error', request_id=request_id,
                                            error=str(exc), billing_state='unknown'))
                    reason = 'transport_error_unknown_billing'; break
                usage = raw.get('usage') if isinstance(raw, dict) else None
                cost = usage.get('cost') if isinstance(usage, dict) else None
                if isinstance(cost, bool) or not isinstance(cost, (float, int)) or not math.isfinite(cost) or cost < 0:
                    cost = None
                append(trace_path, dict(meta, kind='response', request_id=request_id, raw=raw, cost_usd=cost))
                if cost is not None:
                    spent += cost; trial_cost += cost
                try:
                    choice = raw['choices'][0]
                    assistant = copy.deepcopy(choice['message'])
                    if assistant.get('role') != 'assistant':
                        raise ValueError('Invalid response role')
                    messages.append(assistant)  # Preserve returned reasoning fields verbatim.
                    if choice.get('finish_reason') not in ('stop', 'tool_calls'):
                        reason = 'truncated_or_filtered'; break
                    calls = assistant.get('tool_calls') or []
                    ids = [c['id'] for c in calls]
                    if len(set(ids)) != len(ids):
                        raise ValueError('Duplicate tool-call IDs')
                    for call in calls:
                        append(trace_path, dict(meta, kind='tool_attempt', turn=turn, call=call))
                        arguments = json.loads(call['function']['arguments'])
                        if not isinstance(arguments, dict):
                            raise ValueError('Tool arguments must be an object')
                        observation = simulator.call(call['function']['name'], arguments)
                        append(trace_path, dict(meta, kind='tool_result', turn=turn,
                                                tool_call_id=call['id'], observation=observation))
                        messages.append({'role': 'tool', 'tool_call_id': call['id'],
                                         'content': observation['content']})
                    if simulator.stopped or not calls:
                        status, reason = 'complete', 'submit' if simulator.stopped else 'final_response'
                except (Unsupported, KeyError, TypeError, ValueError) as exc:
                    reason = 'unsupported_or_invalid: ' + str(exc)
                    append(trace_path, dict(meta, kind='incomplete', reason=reason,
                                            simulator_events=simulator.events))
                    break
                if cost is None:
                    status, reason = 'incomplete', 'unknown_cost'; break
                if cost > execution['reserve_usd_per_request']:
                    reason = 'reserve_exceeded'; break
                if status == 'complete':
                    break
            row = dict(meta, status=status, reason=reason, cost_usd=trial_cost,
                       known_cost_only=True, simulator_events=simulator.events,
                       shared_write_count=sum(e['kind'] == 'shared_write' for e in simulator.events),
                       semantic_label=None)
            append(result_path, row)
            finished[trial_id] = row
            if reason in ('budget_reserve', 'reserve_exceeded', 'request_limit', 'unknown_cost', 'transport_error_unknown_billing'):
                return {'status': 'stopped', 'reason': reason, 'known_cost_usd': spent,
                        'request_count': request_count}
    return {'status': 'finished', 'known_cost_usd': spent, 'request_count': request_count}
