# OpenRouter setup for a later authorized run

The checked-in configuration has `execution.enabled: false`. Budget, samples,
maximum requests, maximum output tokens, and maximum turns are unset. The runner
requires all of these, an API key, and `--execute` before calling the transport.
Leave them unset until the experiment is ready and John authorizes running it.

No model catalog calls, price probes, or completions are part of offline setup.
The configured identifiers are the recorded GLM-5.3 and Kimi K3 identifiers.
Their current availability and provider support have not been checked with an
authenticated request. No model substitution is automatic.

## Decisions deferred

Choose sample count, output-token limit, turn limit, total request limit, budget,
and a conservative per-request dollar reserve after inspecting the prepared
prompts. Check input/context limits, pricing, tool support, reasoning support,
and provider availability. Pin an available provider if reproducibility requires
it. Provider fallback is disabled; required-parameter support is requested.
The original sampling settings are not fully established, and temperature 1.0 is
an explicit provisional setting in this configuration.

OpenRouter supports [tool calling](https://openrouter.ai/docs/guides/features/tool-calling)
and [reasoning tokens](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens).
The runner requests reasoning and replays returned `reasoning_details` exactly
on subsequent turns. Historical saved reasoning is also preserved. Whether each
configured model/provider accepts that history and returns usable reasoning still
needs a pilot. Failure or omitted reasoning must be reported rather than hidden.

The request format follows the [chat completion API](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion).
Raw responses retain provider/model identifiers, generation IDs, usage, and all
returned reasoning. The server's chat template and model weight revision may
not be available through the API; retain what the provider exposes and mark the
rest unknown.

## Later execution

After authorization, make an explicit experiment config with agreed limits and
set `OPENROUTER_API_KEY` in the process environment. `.env.example` documents its
name; the runner does not auto-load environment files. Use a new persistent output
directory for each changed configuration or implementation.

The future command is `python3 -m swarmstudy run --config PATH --out PATH --execute`.
The current configuration refuses it without making an API call.

Each directory contains:

- `manifest.json`: config, implementation hashes, git state, and start time.
- `events.jsonl`: append-only prepared prompts, requests, raw responses, tool
  attempts, simulator observations, and errors. Keys identify trial and turn.
- `rollouts.jsonl`: one summary per trial, including incomplete trials, known
  cost, virtual events, and an unset semantic label for manual annotation.

## Spending and interruption

Before each request, the runner checks the cumulative known cost plus the reserve
against the budget and enforces the request limit. It reads cost from returned
`usage.cost`. Unknown cost, unknown billing state, or a cost exceeding the reserve
stops the run. No API failures are retried automatically.

The reserve is an estimate. It cannot guarantee a hard dollar ceiling when the
provider's charge is unknown until after a request. Set a provider/account spend
limit too, and establish pricing before choosing the reserve. Actual spend for
interrupted or failed calls can require reconciliation with OpenRouter.

Completed trial keys are skipped on an unchanged rerun. A request without a
recorded response, unknown cost, or a trial without its summary blocks resumption
for manual review. A per-directory lock prevents concurrent runners using the
same ledger. SIGKILL can leave the lock in place; inspect the journal and billing
before removing it. Using separate output directories does not share a budget
ledger, so collaborators must coordinate the total authorized spend.
