"""Verify cached run IDs against Docent and freshly download selected evidence."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from docent import Docent

from download_hf_repro import COLLECTIONS


client = Docent()
root = Path('data/hf_repro')
report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'collections': [], 'fresh_runs': []}
selected = {
    ('glm-5.3', 'step3'): ['be762f77-6115-4d65-bd9a-4bd6bcb45aaa'],
    ('kimi-k3', 'step3'): ['c43286e2-313a-4c20-a948-c2f077c3991c'],
    ('glm-5.3', 'step4'): ['01a4fb4d-8e90-43b1-aaae-4e43226da8c9'],
    ('kimi-k3', 'step4'): ['0db06c07-4a49-4ecc-b836-940e011c4854'],
}
for (model, step), cid in COLLECTIONS.items():
    directory = root / step / model
    remote_ids = set(client.list_agent_run_ids(cid))
    local_ids = set(p.stem for p in directory.glob('*.json') if not p.name.startswith('_'))
    assert remote_ids == local_ids, (step, model, remote_ids - local_ids, local_ids - remote_ids)
    for rid in local_ids:
        run = json.loads((directory / f'{rid}.json').read_text())
        assert run['id'] == rid and run['transcripts']
    report['collections'].append({'model': model, 'step': step, 'collection_id': cid,
                                  'remote_count': len(remote_ids), 'local_count': len(local_ids),
                                  'ids_match': True})
    for rid in selected.get((model, step), []):
        fresh = client.get_agent_run(cid, rid)
        assert fresh is not None
        dump = fresh.model_dump(mode='json')
        previous = json.loads((directory / f'{rid}.json').read_text())
        assert dump == previous, (step, model, rid, 'cached and fresh JSON differ')
        dest = Path('data/hf_repro_fresh') / step / model / f'{rid}.json'
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(fresh.model_dump_json())
        report['fresh_runs'].append({'path': str(dest), 'matches_cache': True,
                                    'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()})
    print(step, model, len(remote_ids), 'IDs verified', flush=True)
Path('data/hf_repro/download_verification.json').write_text(json.dumps(report, indent=2))
