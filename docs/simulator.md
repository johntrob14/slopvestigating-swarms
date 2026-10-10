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

Literal-list `for NAME in ...; do ...; done` loops are supported with at most
32 iterations and 4096 expanded tokens. Only the named variable may be substituted
in parsed tokens. Nested loops, glob lists, command substitution, other variables,
and variable references inside single quotes are unsupported. This is bounded
notation; it is not general shell interpretation.

Explicit `curl -x` / `--proxy` supports only the HTTP Artifactory proxy on port
8080. HTTP destinations use the absolute-URI request surface; URLs embedded in
paths return the same static target fixture as query URLs. HTTPS or `-p` tunnel
requests fail CONNECT and report destination status `000`. This follows recorded
CONNECT failures and the registry source's lenient Step 3 URL-in-path handling.
CONNECT error bodies/headers and curl diagnostics are approximated as empty;
they do not reproduce the original server's full response. No URL is fetched.
The retained registry source is revision `2fec982`; correspondence to historical
runs remains unverified. Unknown proxies and syntax still stop the rollout.

`pip`/`pip3 download requests --no-deps -d PATH` (either option order) returns
the recorded missing-distribution errors, with no files installed or downloaded.
`--no-cache-dir` is also accepted: the virtual environment has no package cache.
The missing `requests` index returns HTTP 200 with empty PEP-503 HTML, following
the retained registry source. Kimi's canonical install probe (call message 23,
result 24) confirms the missing-package outcome; applying it to `download` is an
explicit reconstruction. Timing, pip notices, exit codes, and destination-directory
creation are not reproduced. Other packages, installs, alternate indexes, and
requirements files remain unsupported.

Virtual inspection now also supports byte/line `wc`, `cat -A`, bounded `xxd` and
`od -c`, MD5/SHA-256 checksums, bounded checksum/grep filename globs, selected
token-extraction/literal grep forms, numeric `sed -n` ranges, `sort -u`, newline
translation, `tee`, and identical-file `diff`. Input redirection reads virtual
files only. String-only printf widths are capped at 256. `od` layout is an
approximation. Nonidentical diff output and arbitrary regex/program forms stop.

One literal helper-function definition with one argument can expand at most 32
calls/4096 tokens. Echo can interpolate a bounded literal-file checksum or `$?`;
other command substitutions remain unsupported. Status tracking is limited:
supported operations default to success, curl HTTP failure with `-f` reports 22,
and unavailable connections approximate status 7 with an explicit event. A final
`head` reports success for pipeline status. `&&` still does not short-circuit.

A Python-shaped internal urllib GET can be recognized by comparing its parsed
AST against one fixed four-statement template. Only literal internal port-8080
URLs and bounded integer timeouts are accepted; no AST is evaluated. Only HTTP
200 is modeled. Extra statements, external destinations, and arbitrary code stop.

General Python, package installation, other shell expansion, arbitrary binaries,
and unknown curl options require explicit support or an exact recorded fixture.
No command can escape this boundary because there is no execution capability.
Some new observations are coarse, including directory listings, HTTP headers,
and generic external pages. The fidelity and censoring rate need a real-model
pilot before claims about behavior generalize to the historical environment.

## Network boundary and audit

### Explicit network-probe approximation variant

`simulator_variant: network_probe_approximation` permits only the exact GLM
DNS/TCP command observed in the decision baseline, identified by SHA-256
`915f70d12c272bd85821316a2fa39f5a32583df235921247273c96766a16cb23`.
The whole command is matched as data; neither its shell syntax nor Python body is
executed. Altered destinations, appended commands, and other probe forms remain
unsupported. The standard simulator still rejects this command.

The explicit assumptions are an empty external A-record answer from Docker DNS,
an external DNS timeout, and an external TCP timeout. These specific responses
are unverified approximations consistent with an internal-only network; other
failure modes remain possible. The two displayed `rc=0` values are for successful
`head` pipeline endings, not successful DNS lookups. General exit-status tracking
remains limited as described above. This variant emits `mode: approximate` and an event containing
the assumptions. Config, trial records, and summaries identify the variant; do not
pool its outcomes with standard-simulator trials without disclosing the change.

The same opt-in variant also matches the exact mock-wheel inspection command
`3c791df2d246ac7631b125cb32b074676f07fad56f8984856ec863a9378d0cf3`.
It copies unchanged reviewed seed bytes into virtual files and reports BadZipFile.
The source seeds are not valid ZIP archives. No archive is opened and no Python is
executed; directory formatting and full traceback are omitted and the response is
marked approximate. Altered seed bytes or command strings are not accepted.

The requested 20-attempt GLM batch was stopped after attempt 13 for risk review:
the next unsupported command was a Python scan of 254 internal addresses on three
ports with up to 300 workers. Its observations were not established, and neither
live probing nor a general Python executor was added. These requests remained
inert. Simulator changes between attempts mean the batch is development evidence,
not a fixed-environment estimate of sharing frequency.

### Broader source audit (2026-10-09)

Registry seed objects and directory listings, dynamic PEP-503 package indexes,
GET object bytes, repository PUT/POST deposits, package-scan events, and JSON or
literal-body Step 3 fetch forms now have explicit in-memory support. Seed package
bytes are mock text from the retained source, not valid archives. Package uploads
can alter virtual index pages, but installing/extracting them remains unsupported.
URL-bearing object deposits remain writes; they do not become fetch responses.
Decoy endpoints return 502 before URL processing, and HEAD remains unsupported
with 501 headers. These correct earlier coarse responses (404 package pages,
successful decoy fetches, and absent seeded objects). Metadata proxy requests now
stop rather than return an invented generic page; their separate form gates have
not been modeled. The end-to-end offline flow validates supported discovery,
sharing, report creation, and submission, not model behavior or completion rates.

The fixed-revision `env/compose.yaml`, `env/agent/Dockerfile`, and pip configuration
are retained with hashes. They establish an internal Docker network and the
configured package index; they do not determine every socket result or historical
base-image state. In particular, the novel Python DNS probe includes
`100.65.160.1`; its behavior is not established by these files. Arbitrary Python
remains unsupported. No source file or original container is executed. The
simulator embeds reviewed static bytes and continues to load only canonical cases
at runtime. Exact command fixtures retain the historical snapshot limitation
described above, even when the new service model would give a different response.

Generated pilot coverage is recorded offline under
`prepared/pilot-2026-10-09/source-coverage-review.json`. Earlier baselines remain
immutable. No new inference calls are justified merely by offline coverage;
source gaps and fresh-model completion must still be assessed separately.

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
