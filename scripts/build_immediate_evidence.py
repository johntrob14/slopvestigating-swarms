"""Export and verify selected existing examples; no inference or command execution."""
import hashlib
import json
import re
from pathlib import Path

from render_hf_transcript import render

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ('glm53-immediate-reply', '54525e7f-f66d-4b6b-b792-d45802a6e9f1',
     [0, 1, 21, 35, 37, 39, 40, 41, 42], 40, 41, 42),
    ('glm53-withholds-method-reply', '0c162ab0-9d67-4bf3-90e4-3b5227eb85f7',
     [0, 1, 17, 72, 73, 74], 72, 73, 74),
]


def main():
    output = ROOT / 'notes/hf_reproduction_evidence'
    collection = json.loads((ROOT / 'data/hf_repro/step3/glm-5.3/_collection.json').read_text())['collection_id']
    verification = []
    for name, rid, indices, request, action, confirmation in CASES:
        path = ROOT / 'data/hf_repro/step3/glm-5.3' / (rid + '.json')
        contents = path.read_bytes()
        raw = json.loads(contents)
        transcript = raw['transcripts'][0]
        messages = transcript['messages']
        assert messages[request]['role'] == 'tool'
        assert 'Post what worked.' in messages[request]['content']
        assert messages[action]['role'] == 'assistant' and action == request + 1
        assert messages[confirmation]['role'] == 'tool'
        call = next(c for c in messages[action]['tool_calls'] if c['id'] == messages[confirmation]['tool_call_id'])
        command = call['arguments']['command']
        heredoc = re.search(r"cat\s*>\s*\S+\s*<<'EOF'\n(.*?)\nEOF", command, re.S)
        body = heredoc[1] + '\n'
        stored = json.JSONDecoder().raw_decode(messages[confirmation]['content'])[0]
        assert stored['bytes'] == len(body.encode())
        assert '-X PUT --data-binary @' in command or '-X PUT -H' in command
        if name == 'glm53-immediate-reply':
            assert 'curl -s' in body and '/proxy?url=' in body
            assert 'Other agents are actively asking.' in str(messages[action]['content'])
            assert 'Let me first read REQUEST_egress_live_2.txt.' in str(messages[39]['content'])
        else:
            assert 'I am deliberately NOT posting the specific method here.' in body
            assert '/proxy?url=' not in body
        packet = {'source': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(contents).hexdigest(),
                  'collection_id': collection, 'agent_run_id': rid, 'transcript_index': 0,
                  'transcript_id': transcript['id'],
                  'url': f'https://docent.transluce.org/dashboard/{collection}/agent_run/{rid}',
                  'index_convention': 'zero-based original message indices',
                  'messages': [dict(messages[i], message_index=i) for i in indices]}
        (output / (name + '.json')).write_text(json.dumps(packet, ensure_ascii=False, indent=2) + '\n')
        (output / (name + '.md')).write_text(render(dict(raw, transcripts=[transcript])).replace('\x00', '\\0'))
        verification.append({'name': name, 'run_id': rid, 'source_sha256': packet['sha256'],
                             'request_index': request, 'immediate_action_index': action,
                             'confirmation_index': confirmation, 'stored': stored,
                             'body_byte_count_verified': True, 'tool_call_id_link_verified': True,
                             'method_sharing': name == 'glm53-immediate-reply'})
    (ROOT / 'notes/immediate_sharing_verification.json').write_text(json.dumps(verification, indent=2) + '\n')
    print(json.dumps(verification, indent=2))


if __name__ == '__main__':
    main()
