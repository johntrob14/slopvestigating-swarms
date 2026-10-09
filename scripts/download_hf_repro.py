"""Download GLM 5.3 and Kimi K3 agent runs from the OpenAI-HuggingFace reproduction
(LessWrong post fMnC6ZD37qrnZAFYz) Docent collections, one JSON file per run."""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from docent import Docent

COLLECTIONS = {
    ("glm-5.3", "step1"): "f70a00bd-e872-4e7e-a5ba-05a10f0abb57",
    ("kimi-k3", "step1"): "04a0ae1c-9f16-4c2b-8706-69b27cc65da4",
    ("glm-5.3", "step2_orig"): "cc632b6b-1e0c-4469-9338-de52cb750829",
    ("kimi-k3", "step2_orig"): "4531575c-a773-4382-9813-7c2e9e916535",
    ("glm-5.3", "step2_collab"): "b302a291-a6bc-4de6-8669-f4da1277d248",
    ("kimi-k3", "step2_collab"): "27000dca-35dc-450b-8756-92ca0aa20210",
    ("glm-5.3", "step3"): "590eccfa-f1e8-49f6-8b98-aec80d0ba83b",
    ("kimi-k3", "step3"): "ca5aa7e4-8f59-4a81-a399-01673f551e86",
    ("glm-5.3", "step4"): "b808f3d1-b391-42ca-8964-8583b82e3421",
    ("kimi-k3", "step4"): "b4390869-3568-4e6e-88a1-14110f2f2ff9",
}

def fetch(args):
    client, out_dir, cid, rid = args
    path = out_dir / f"{rid}.json"
    if path.exists():
        return
    run = client.get_agent_run(cid, rid)
    path.write_text(run.model_dump_json())


if __name__ == '__main__':
    out_root = Path(sys.argv[1])
    client = Docent()
    for (model, step), cid in COLLECTIONS.items():
        out_dir = out_root / step / model
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "_collection.json").write_text(json.dumps({"collection_id": cid}))
        ids = client.list_agent_run_ids(cid)
        with ThreadPoolExecutor(8) as ex:
            list(ex.map(fetch, [(client, out_dir, cid, r) for r in ids]))
        print(step, model, len(ids), flush=True)
