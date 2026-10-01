# Explicit Run Binding

Every command, handoff, callback and resume identifies the exact canonical absolute workspace, run_id, session_id, owner, owner_epoch and expected state_version. A session's durable binding is immutable. The active pointer is discovery metadata, never permission to retarget a session. Missing, malformed, unsupported or ambiguous identity denies mutation; never infer a run from a parent directory, recent files, dates or latest pointer.

## Coordinator and leaf boundary

Only the coordinator dispatches task(). Missing coordinator dispatch capability returns TASK_DISPATCH_UNAVAILABLE; no fallback dispatch or coordinator specialist self-work. A leaf with task:false executes its assigned handoff using allowed non-delegation tools and phase scope. It returns delegation or expanded-scope needs to the coordinator. This grants no approval, infrastructure or release authority.

## Operator enrollment precondition

The shell accepts only JSON on stdin; old init/recover/approve/enter_revision forms are disabled. Initialization, policy pinning, actor capability/phase/tool assignment and session enrollment require a separately authorized operator using the storage API. Enrollment pins policy_config in the run's domain payload. No plugin or hook automatically enrolls or migrates state. The legacy singleton remains untouched. Deployment first requires local single-host filesystem support and quiescence of all legacy writers.

## Requests and callbacks

Execute scripts/enforcement/workflow-enforce.sh from the exact package root. Fields: workspace, session_id, run_id, expected `[owner, owner_epoch, state_version]`, action. The read-only bound action looks up session identity; no fallback. Status and compaction retain explicit identity. Stale transitions return nonzero; never retry against latest state.

Task/tool start registers an effect and returns the exact token for its end callback. Keep that workspace, run, session, token and dispatch ID unchanged after delay. Stale/lost callbacks leave effects unresolved, blocking ownership transfer. Handoffs additionally name agent, phase, scope and evidence path. Nested packages require separate explicit enrollment.

Typed effect records persist origin session/call, kind/tool, run/workspace/owner/epoch, phase attempt, agent, child-session registrations, parent effect, scope and authorization digests, start token/version, random effect token, and immutable identity digest. `effect-status` looks up only the exact origin session/call after restart. Unknown effects remain protected.

Normal stale callbacks still fail without mutation. A distinct `reconcile-effect` request is permitted only for an explicitly enrolled reconciler. It supplies the original effect token/identity digest, authenticated completion-proof digest, a fresh explicitly supplied owner/epoch/version tuple, reason, and reason_provenance referencing that proof. The core never substitutes latest state for the supplied tuple. It verifies unchanged authorization, scope, owner/epoch and phase attempt, an allowed producer's operator-attested completion, and terminal registered children. One successful reconciliation increments state_version once, not revision_count. Exact replay is a no-op; conflicting replay denies. Reopen/failure advances the phase attempt and invalidates old specialist receipts and deliverable digests.

## Operator lifecycle boundary

The separate `scripts/enforcement/operator_cli.py` reads a 32-byte capability from a dedicated inherited descriptor identified by WORKFLOW_OPERATOR_FD, never from request text or logged command arguments. Explicit operator bootstrap stores a private local verifier key; possession authenticates a trusted local operator, not an independently verified human identity. This key and all enforcement files must be protected by the pending file-target controls before activation. Nothing here grants model tools operator authority.

Authenticated operations are create-run, inspect-run, enroll, close-child, attest-completion, import-human-approval and recover-attempt. Create pins validated policy and actor profiles; enrollment cannot silently replace an actor or session binding. Completion attestation signs exact evidence and deliverable digests for an allowed producer after child quiescence. Human approval import validates a locally signed declaration with exact run/workspace, action, target, scope, subject hash, human identity, reason and expiry; external proof of human authorization remains the operator's responsibility. Recovery cannot clear in-flight effects, change owner or skip phases. Model-facing init/approve stay denied.

The candidate native OpenCode adapter implements this typed contract, including full argument mediation, durable callbacks and authenticated host observations. Host reconciliation requires an explicit operator-pinned grant and records its reason and expected tuple. This is fixture-verified workflow-layer behavior, not live activation approval or certification of replacement task providers.

Native OpenCode success and error handlers attest actual tool arguments and host outcomes; model-written metadata.workflow_receipt is not trusted proof. Task children use the version-checked task_id/sessionId contract. Missing or foreign child identity leaves the effect protected. OMO and other replacement task providers remain uncertified. Network gates additionally check package-local agent, run, phase attempt, deliverable, dispatch ID, timestamp and evidence.

Claude file hooks use registered PreToolUse, PostToolUse and PostToolUseFailure events with exact cwd/session/tool_use_id and durable lookup, not invented echoed context. Native host permissions still apply. Claude Task/Agent and exact-action tool adapters are explicitly unsupported; unknown subagent bindings never inherit parent authority. PreCompact returns the bound status envelope. Hooks never initialize state.

Opaque bash/exec is denied. Use workflow_action only for an operator-pinned argv definition with executable/input hashes and explicit target scope. Mutation actions additionally require active phase/revision/domain authority and an unexpired, unrevoked exact human receipt bound to run, owner epoch, phase attempt and action subject hash. Timeout does not approve or replay an action. Do not translate a denied consequential command into another tool.

Path checks and cooperative target leases are not an OS sandbox. A hostile same-UID process swapping a path after admission is outside this workflow-layer guarantee. Require exclusive workspace/control-file ownership and reviewed pinned action code; stronger isolation needs host-level execution controls. Human approvals, reviewer independence and network safety gates remain in force.

## Retention and admission bound

Active effect indexes and typed records must agree on every authorization read and mutation. Corrupt or orphaned indexes are denied, never repaired implicitly. Native and exact-action leases share canonical workspace-relative paths, independent of the signed action definition's spelling. Network gate receipts must resolve to the authoritative completed effect and authenticated current-authority proof, not merely contain a proof reference.

Escalation and revocation block new dispatch and successful phase progression. Inspection and narrowly bounded failure handling do not clear these holds. The authenticated operator-only clear-hold action requires quiescence, exact CAS and a signed audit reason; a revision extension is bounded and preserves revision_count history. Revocation clearance changes authorization identity and invalidates the current phase attempt. Model-facing hold clearance is not supported.

The immutable store capacity bounds retained full runs. Lifetime admission additionally refuses when the combined full-run and retirement-marker count reaches four times that capacity. Retirement fences are never silently removed or run IDs reused. Interrupted retirement may conservatively count both files and refuse sooner. Exhaustion requires an explicit operator decision about a new store/workspace; generation, resume and model tools cannot erase the history or increase the cap. This bounds retirement metadata; it is not a byte quota for all possible evidence payloads.
