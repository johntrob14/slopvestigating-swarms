# Implementation verification

The experiment is prepared for offline inspection. No new model generations,
OpenRouter catalog checks, price probes, or paid calls were made. This note
records software checks and selected historical evidence, not a replication
result.

## Verified

- Both canonical runs pass their byte-level SHA-256 checks. A separate audit
  script reads raw JSON directly, checks the action/result tool-call links, and
  extracts the historical upload confirmations: GLM 852 bytes, Kimi 187 bytes.
- Preparation writes 16 complete prompt packets. All retain exactly the first
  20 messages. Intervention differences are limited to message 18 and, in the
  prohibition condition, an appended instruction in system message 0. Matched
  agent/human prompts differ only in their claimed author phrase.
- Offline continuation replay covers GLM's 25 and Kimi's 9 historical tool calls
  after the checkpoint. All bash observations match the saved originals. Method
  uploads update in-memory state with the recorded byte counts. This mainly tests
  fixture consistency, not a general recreation of the shell or environment.
- The checked-in configuration blocks execution before creating result files or
  calling a completer. Every required unset sampling and budget limit is tested.
- The offline suite passes 26 tests, including simulator isolation, request
  interventions, exact reasoning-detail preservation, generated report reads,
  unknown-operation censoring, fixed transport destination, redirect rejection,
  missing-cost stops, no automatic billing retries, limits, and safe resumption.

Recorded outputs: [independent audit](offline_audit.json) and
[test log](offline_tests.txt). The audit code is
[audit_preparation.py](../scripts/audit_preparation.py). Prepared full prompts and
fixture replay observations are generated under `prepared/` and ignored by git.

## Limits and simplest alternative explanations

Fresh behavior, model availability, original sampling settings, provider history
acceptance, chat templates, reasoning visibility, and real-model simulator
coverage are unverified. No behavior rates or causal effects have been measured.
An exact historical fixture match cannot establish that a new model would select
that command, nor that approximate new observations preserve the same behavior.

Historical examples were selected for existence evidence. The peer notes were
scripted. Original scope permits an external exercise and leaves cooperation
ambiguous. Prior reasoning already infers other agents, so the human-attribution
condition has a contextual prior to overcome. The explicit prohibition creates
a new, clearer scope test and must be analyzed separately.

The transport tests use mocks. The simulator tests intercept network/process
primitives and check that generated paths create no host files; they also cover
known recorded uploads. The boundary depends on retaining this architecture in
future edits. No operating-system sandbox or original Docker workload was tested.

## Reproduce these offline checks

```sh
python3 -m swarmstudy prepare
python3 -m swarmstudy replay
python3 scripts/audit_preparation.py
python3 -m unittest discover -s tests -v
```

The next empirical step requires a separately authorized baseline pilot with
agreed budget, sample count, and generation limits. None has been run.
