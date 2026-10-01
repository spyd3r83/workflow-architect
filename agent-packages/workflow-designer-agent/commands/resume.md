Resume an explicitly bound workflow run.

Usage: /resume <canonical-workspace> <run_id> <session_id>

## Instructions

Follow `run-binding.md`. Require the persisted session binding to match the supplied workspace and run_id. Read the exact owner, owner_epoch and state_version; carry that expected tuple into each authorized transition. Missing/corrupt/unsupported binding denies mutation. Do not infer progress from files, a singleton, a parent workspace or the active pointer.

### Arguments

$ARGUMENTS

### Steps

1. Validate the exact workspace/run/session binding through the package-local enforcement API.
2. Read current phase, effects, owner and gates from that run. Unresolved effects require inspection, not takeover.
3. Retain required authorization, scope, specialist receipts and independent-review gates.
4. Coordinator dispatch uses task() only; missing capability stops dispatch. Assigned leaves with task:false continue bounded work and return delegation needs.
5. Resume only within the existing authority. Do not initialize, migrate, retarget or approve actions implicitly.
