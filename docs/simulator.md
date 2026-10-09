# Inert tool environment

The recipient sees reconstructed `bash` and `submit` tools. Its tool arguments
are parsed as data in `swarmstudy/simulator.py`. They never reach a shell,
Python evaluator, container, socket, browser, or network client. The original
environment is never started. Addresses and commands from the transcripts
remain strings.

The simulator reads only the fixed canonical case files through the case loader.
Generated paths address a Python dictionary. Even `echo ... > /etc/hosts` or
`curl --data-binary @/etc/passwd` can only affect or read virtual files. Reading an
unknown upload file stops the rollout. Virtual HTTP requests are local function
calls. External direct access returns a blocked observation; query-based proxy
requests return static fixture text. The exercise token is a public recorded
fixture, never a credential to a running service.

## Observation sources

1. An exact original command string can reuse its recorded observation, labeled
   `recorded_fixture` with the original message index. Recognized method uploads,
   probe uploads, and report heredocs also update virtual state.
2. A new supported command receives an observation from the in-memory service
   model, labeled `simulated`.
3. Unsupported syntax or tools terminate the rollout as incomplete. No fallback
   executes the command or silently supplies an empty response.

Recorded observations are historical snapshots. They do not fully adapt to
changed state or timing. Exact original loops and Python probes can be replayed
as opaque observations; their internal filesystem effects are not all reconstructed.
Only recognized writes are applied. This is a deliberate fidelity limitation,
and a novel command that depends on an absent virtual file may be censored.
Read-only commands naming the local report directory or shared answer paths use
virtual state even when they match a fixture. This prevents a historical report
from appearing in a branch that did not write it. Inspect fixture use in each
rollout before interpreting its final narrative.

## Supported new command notation

- Literal `cat` heredocs for virtual files; `echo` and one-argument `printf`.
- `cd`, `mkdir -p`, `cat`, `head`, `tail`, `ls`, and basic `wc`.
- Simple sequences with `;` or `&&`, pipelines, `timeout`, and common stderr
  redirections. These are approximate observations, not full shell semantics.
  `&&` does not model process exit status; do not use it to infer real failures.
- A bounded subset of curl options for method, body, upload file, headers, output
  file, and status formatting. Shared-board PUT/POST writes remain in memory.
- The virtual artifact service, shared notes, and static external target body.

General Python, package installation, shell expansion, loops, arbitrary binaries,
and unknown curl options require explicit support or an exact recorded fixture.
No command can escape this boundary because there is no execution capability.
Some new observations are coarse, including directory listings, HTTP headers,
and generic external pages. The fidelity and censoring rate need a real-model
pilot before claims about behavior generalize to the historical environment.

## Network boundary and audit

`swarmstudy/openrouter.py` is the sole inference transport. It always connects
to `openrouter.ai` at `/api/v1/chat/completions`. It accepts no destination URL
and follows no redirects. Generated URLs appear inside prompt data sent to
OpenRouter and in local records; they are never used as network destinations.
The host runner writes logs and invokes fixed git metadata commands only.

Tests replace network and process primitives with failures while submitting
generated commands, verify that virtual paths create no host files, exercise
literal malicious-looking heredoc bodies, and mock the OpenRouter transport.
This is an application-level safety boundary, not an OS sandbox for arbitrary
untrusted code. Future changes must retain the absence of execution capabilities
inside the simulator.
