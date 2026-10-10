# Message-board request following

This repository prepares safe resampling experiments from two selected GLM-5.3 and
Kimi K3 transcripts in the [OpenAI/HuggingFace reproduction](https://www.lesswrong.com/posts/fMnC6ZD37qrnZAFYz/openai-huggingface-a-reproduction-and-lessons-for-alignment).
Both recipients read scripted peer requests and later upload a working access
method to the shared board. The original task authorizes an external security
exercise, so these examples establish request following. Whether sharing violates
the original task scope needs separate judgment.

**Current state: an authorized baseline pilot has begun; no agent/human comparison
results exist yet.** The first two baseline continuations were incomplete because
of simulator coverage gaps, at a combined cost of $0.024925469. Bounded loop and
proxy support was added after those observations. Pilot artifacts remain ignored
under `prepared/` and `results/`; original case transcripts are unchanged.
The default experiment configuration still disables execution. Pilot model calls
use OpenRouter/Wafer with explicit limits under a total $20 authorization; new
conditions or revised runs must account for spending in earlier directories.

## Start here

Use Python 3.9 or newer. Offline work needs no packages or API key.

```sh
python3 -m swarmstudy prepare
python3 -m swarmstudy replay
python3 -m unittest discover -s tests -v
```

`prepare` writes all 16 complete prompt packets to `prepared/peer_requests/`.
Each contains the actual messages, reconstructed tool definitions, source
checksum, intervention, and prompt hash. `replay` checks the recorded tool
fixtures and virtual writes. It generates no model text.

| Read | Purpose |
| --- | --- |
| [Case guide](docs/cases.md) | What each transcript shows and the decisive message indices |
| [Experiment](docs/experiment.md) | Checkpoint, conditions, measurements, and causal limits |
| [Simulator](docs/simulator.md) | Supported observations and why tool calls cannot execute |
| [OpenRouter](docs/openrouter.md) | Future execution, provider checks, accounting, and unresolved choices |
| [Hypotheses](notes/hypotheses.md) | Predictions to register before runs |
| [Verification](notes/implementation_verification.md) | What has actually been checked |

## Repository layout

- `data/cases/`: the two immutable raw runs and their provenance/checksum manifest.
  These are the portable experiment inputs.
- `notes/hf_reproduction_evidence/`: readable primary transcripts and indexed
  evidence packets. Two supplementary Step 4 examples are included for context.
- `data/hf_repro_source/`: retained source excerpts with a separate manifest.
- `experiments/peer_requests/config.json`: disabled experiment configuration.
- `swarmstudy/`: prompt construction, memory simulator, gated runner, and fixed
  OpenRouter transport.
- `tests/`: offline checks, including mocked transport and billing failures.
- `prepared/` and `results/`: generated artifacts, ignored by git.
- `data/hf_repro/` and `data/hf_repro_fresh/`: ignored bulk download caches. They
  are optional once the two canonical cases are present.

The original download and verification utilities in `scripts/` access Docent and
are separate from these offline commands. `build_hf_evidence.py` is an archival
rebuild utility that requires the bulk cache; it uses the retained source snapshot.
The repository does not require the original Docker environment.

For collaboration, commit the code, canonical cases, documentation, and evidence
packets. Agree on a separate persistent location for generated rollouts before
running; each output directory holds its own complete configuration, implementation
hashes, request/response journal, and rollout summaries. Do not share API keys.
