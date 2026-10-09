"""Render downloaded Docent messages once, preserving indices and channels."""
import argparse
import json
from pathlib import Path


def render(run):
    out = [f"# Agent run {run['id']}", ""]
    for ti, transcript in enumerate(run['transcripts']):
        out += [f"## Transcript {ti}: {transcript['id']}", ""]
        for mi, message in enumerate(transcript['messages']):
            out += [f"### Message {mi} [{message['role']}] id={message['id']}", ""]
            content = message.get('content')
            if isinstance(content, str):
                out += [content, ""]
            elif isinstance(content, list):
                for block in content:
                    kind = block.get('type', 'unknown')
                    value = block.get('reasoning') if kind == 'reasoning' else block.get('text')
                    if value:
                        out += [f"[{kind}]", value, ""]
            for call in message.get('tool_calls') or []:
                out += [f"[tool call {call['function']}] id={call['id']}",
                        json.dumps(call['arguments'], ensure_ascii=False, indent=2), ""]
            if message.get('tool_call_id'):
                out += [f"[result for {message['tool_call_id']}]", ""]
    return '\n'.join(out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(json.loads(args.input.read_text())))
