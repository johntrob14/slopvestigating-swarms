"""Independent, offline checks using raw JSON rather than experiment helpers."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'data/cases/manifest.json').read_text())
    prepared = ROOT / 'prepared/peer_requests'
    packets = sorted(p for p in prepared.glob('*.json') if p.name != 'manifest.json')
    assert len(packets) == 16
    report = {'kind': 'independent_offline_audit', 'prepared_prompt_count': len(packets), 'cases': []}
    replays = {r['case_id']: r for r in json.loads((ROOT / 'prepared/fixture_verification.json').read_text())}
    for item in manifest:
        case = item['case_id']
        contents = (ROOT / item['path']).read_bytes()
        assert hashlib.sha256(contents).hexdigest() == item['sha256']
        raw = json.loads(contents)
        messages = raw['transcripts'][0]['messages']
        base = json.loads((prepared / f'{case}--original--original.json').read_text())
        assert len(base['messages']) == 20
        for index, converted in enumerate(base['messages']):
            source = messages[index]
            assert converted['role'] == source['role']
            text = source['content'] if isinstance(source['content'], str) else '\n'.join(
                block.get('text') or '' for block in source['content'] if block['type'] == 'text')
            assert converted['content'] == text
        for condition in ('original', 'no_request', 'agent', 'human'):
            for scope in ('original', 'no_sharing'):
                packet = json.loads((prepared / f'{case}--{condition}--{scope}.json').read_text())
                assert len(packet['messages']) == 20
                diff = [i for i, pair in enumerate(zip(base['messages'], packet['messages'])) if pair[0] != pair[1]]
                expected = ([0] if scope == 'no_sharing' else []) + ([18] if condition != 'original' else [])
                assert diff == expected
                if scope == 'no_sharing':
                    assert packet['messages'][0]['content'].startswith(base['messages'][0]['content'])
                if condition == 'no_request':
                    assert 'Post the method' not in packet['messages'][18]['content']
        agent = json.loads((prepared / f'{case}--agent--original.json').read_text())['messages']
        human = json.loads((prepared / f'{case}--human--original.json').read_text())['messages']
        agent[18]['content'] = agent[18]['content'].replace('an autonomous agent', 'a human researcher')
        assert agent == human
        action = messages[item['action_message_index']]
        confirmation = messages[item['confirmation_message_index']]
        ids = [c['id'] for c in action['tool_calls']]
        assert confirmation['tool_call_id'] in ids
        assert '"stored": "/agent-scratch/ANSWER_' in confirmation['content']
        # Extract the actual JSON confirmation, not a metadata label.
        stored = next(json.loads(line) for line in confirmation['content'].splitlines() if line.startswith('{"stored":'))
        original_calls = sum(len(m.get('tool_calls') or []) for m in messages[20:])
        replay = replays[case]
        assert replay['tool_calls'] == original_calls
        simulated_answer = next(e for e in replay['shared_writes'] if e['path'] == stored['stored'])
        assert len(simulated_answer['body'].encode()) == stored['bytes']
        report['cases'].append({'case_id': case, 'sha256_verified': True,
                                'primary_messages': len(messages), 'checkpoint_messages': len(base['messages']),
                                'confirmed_path': stored['stored'], 'confirmed_bytes': stored['bytes'],
                                'action_result_link_verified': True, 'offline_replayed_tool_calls': original_calls,
                                'virtual_answer_byte_count_matches': True})
    path = ROOT / 'notes/offline_audit.json'
    path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
