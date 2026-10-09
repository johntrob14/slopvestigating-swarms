import argparse
import json
from pathlib import Path

from .runner import DEFAULT_CONFIG, load_config, prepare_all, replay_original, run


def main():
    parser = argparse.ArgumentParser(description='Prepare and study inert transcript continuations.')
    sub = parser.add_subparsers(dest='command', required=True)
    prep = sub.add_parser('prepare', help='Write complete prompt packets offline')
    prep.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    prep.add_argument('--out', type=Path, default=Path('prepared/peer_requests'))
    replay = sub.add_parser('replay', help='Replay original tool fixtures offline, no model')
    replay.add_argument('--out', type=Path, default=Path('prepared/fixture_verification.json'))
    live = sub.add_parser('run', help='Future paid execution; disabled in the checked-in config')
    live.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    live.add_argument('--out', type=Path, default=Path('results/peer_requests'))
    live.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            result = prepare_all(load_config(args.config), args.out)
            print(f"Prepared {len(result['prompts'])} prompts offline in {args.out}")
        elif args.command == 'replay':
            results = [replay_original(case) for case in ('glm53', 'kimi')]
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(results, ensure_ascii=False, indent=2))
            print(f'Offline fixture checks passed: {args.out}')
        else:
            print(json.dumps(run(load_config(args.config), args.out, args.execute), indent=2))
    except (ValueError, RuntimeError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
