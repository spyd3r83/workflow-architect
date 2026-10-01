# Run-scoped handoff repair — authoritative progress record

## Contract and checkpoint 1

Authorized outcome now: baseline inspection, one isolated worktree, provenance snapshot, RED reproductions and design mapping only. Subsequent repair requires the next controller checkpoint. No delegation, install, staging, commit, push, merge, restart, deployment, activation, original session prompt access, or Outline index edit occurred. Product engineering is a read-only wording reference, never a propagation target.

[VERIFIED] Main HEAD and candidate base: `57fe1421573d0e3fa2aea404db15e1ba3db7c32d`. Main branch: `feat/harness-matrix`; candidate branch: `fix/run-scoped-workflow-handoff`. Candidate: `/home/jfi/GitHub/workflow-architect-run-scoped-handoff`. Worktree creation necessarily adds Git worktree/branch metadata; the unchanged claim concerns main working files, index status and HEAD, not shared Git metadata.

Routing receipt: routing registry revision 80 fetched live on 2026-10-01 in this checkpoint; workspace is the isolated candidate for controller-owned `/update`, orchestrator remains `workflow-orchestrator`, assigned leaf remains sole writer. Exact fetch clock time was not exposed; snapshot capture timestamp is retained separately. Controller handoff supplies Single-Shot revision 11 and MSES revision 6 retrieved 2026-10-01; reused, not independently refreshed here. URLs: https://outline.docs.internal.jfi-research.com/doc/workflow-designer-agent-agent-roster-and-dispatch-routing-for-codex-4P0FG1R3vZ ; https://outline.docs.internal.jfi-research.com/doc/single-shot-delivery-frame-from-instruction-to-verified-outcome-P8aPdVCmiQ ; https://outline.docs.internal.jfi-research.com/doc/documentation-standards-modern-software-engineering-standard-v20-development-guidance-jUIeIe9CIE .

User-supplied provenance only: standalone Oracle `ses_f094ef58bffeKRkPLEWO3AXySZ`, verdict REVISE with permission to proceed after mandatory corrections. Not independently retrieved; not a candidate approval. Broken reviewer not rerun. T2/T3 independent exact-candidate QC/red-team remains required; review grants no release authority.

## Evidence inventory and changed-file baseline

- `checkpoint1-evidence/main-status-before.txt`: exact original main porcelain status, including all visible untracked paths.
- `checkpoint1-evidence/main-inventory-before.json`: 1,152 source file/link hashes, including network and product ignored trees and root state where present.
- `checkpoint1-evidence/snapshot-manifest.json`: per-path hashes and import reasons; 626 network files/links plus nine existing enforcement dependencies. Network cache directories excluded; original caches still hashed in source inventory. Symlinks copied only when relative and resolving within the original network package.
- `checkpoint1-evidence/main-unchanged.json`: snapshot-time preservation check; final check is in `main-unchanged-final.json`.
- `checkpoint1-evidence/red-results.json`: executed negative acceptance observations.
- `checkpoint1_snapshot.py`: one-shot provenance capture, not a production component; do not rerun against the existing snapshot.
- `checkpoint1_red.py`: repeatable sandbox-only RED reproducer; creates disposable fixtures under evidence, never touches real package state.

No dirty tracked main files imported. Existing root enforcement script/plugin/config were ignored and absent from HEAD; imported explicitly after discovery, with hashes recorded in snapshot manifest. Six untracked canonical/root enforcement surfaces were also imported. This is a selected baseline, not the entire dirty working tree. Dirty generator/validator changes remain excluded pending hunk-level necessity review. Imported state and existing receipts are historical data, not permission to execute or seed new runs. No production implementation edits yet.

## Verified RED evidence and limits

`python3 checkpoint1_red.py` exits 1 and reports four RED cases:

1. Root real shell `check write` with missing binding/state/config returns `allow`.
2. Network-local real shell does the same.
3. Actual root Claude pre-tool hook returns empty success when its enforcement script is missing.
4. Root real `dispatch-failed` accepts a callback carrying stale owner/run/epoch/version environment values and changes the fixture state.

Initial root-script probes were NOT_REPRODUCED because that ignored dependency was absent from HEAD; this was a fixture deficiency, not a passing control. After provenance-bound import all four reproduced. RED results prove only these cases, not the full acceptance matrix.

[VERIFIED by source inspection] Root plugin auto-initializes singleton state, returns empty output for missing script, and blocks only `block:` rather than requiring explicit allow; unresolved package binding can return without blocking. Root shell writes singleton state directly, without run binding/CAS. Network local shell includes specialist receipt checks that must survive adaptation. Network AGENTS line 27 has the broad missing-task stop rule; product dispatch lines 3–7 distinguish coordinator and leaf. Product was not copied into candidate.

[VERIFIED] History identities inspected: 57fe142 dispatch/adapters, 2ac545c session-aware directory resolution, dae50dc primary task permission, 5a6758f task-only dispatch, 8f0f5dc enforcement introduction. Detailed historical diffs and prior PR evidence have not yet been inspected; do that before choosing implementation details.

[ASSUMPTION / pending] No live legacy-writer quiescence evidence. No actual TypeScript plugin runtime test executed. Network August-state/October-context mismatch is controller-reported, not independently reproduced here. Do not claim a live dispatch test from the controller's earlier harmless leaf observation.

## Mandatory design mapping

| Requirement | Proposed existing owner / surfaces | RED-first acceptance |
|---|---|---|
| Coordinator-only missing-dispatch stop; leaves execute handoff without task and return needs | Canonical AGENTS, dispatch protocol, agent/command templates, generator and validator; network-local equivalents | Harmless task:false leaf continues; unavailable coordinator stops; contradictory generated contract rejected |
| Immutable validated workspace/run binding | Existing enforcement script boundary, root/canonical plugin, hooks, commands, compaction and resume templates | Two runs, moved pointer, delayed callback, resume and nested packages cannot retarget a bound session |
| Versioned schema/config; owner epoch and state version distinct from revision count | Shared storage support within existing enforcement directory; shell remains entry point | Concurrent claims one winner; stale owner/epoch/version rejection leaves bytes unchanged |
| Stable single-host local filesystem advisory lock, atomic publication | Existing enforcement storage path; never unlink/replace lock inode | Same-directory temporary file flush/fsync, rename and directory fsync; state published before pointer; fault injection leaves unpublished run inert |
| Explicit allow/success; deny ambiguity and errors | Actual plugin and platform hook paths, not only helper tests | Missing script, timeout, corrupt/dangling pointer, invalid/escaping ID, unsupported schema and ambiguous workspace all deny mutations; no auto-init or parent/latest fallback |
| Quiescent transfer and legacy migration | Explicit administration/import command through same lock/CAS boundary | Reject transfer with running effects; preserve singleton; exact matching legacy import is idempotent and interruption-safe; fresh runs inherit no old gates/receipts/approvals/revisions |
| Retention under same lock | Store admission/retention operations | Delete only validated terminal inactive unlocked quiescent runs; race tests; protected-cap exhaustion refuses admission |
| Preserve network specialization | Adapt network-local script/config/plugin/tests rather than replacing wholesale | Receipts bound to run/phase/dispatch; existing phase/specialist and infrastructure authority gates retained |
| Propagation parity | Canonical meta, templates, generator, validator, generated adapters | Generate twice with no drift; smallest canonical tests and validator plus network tests and diff check |

Advisory fencing protects cooperating filesystem operations only. JSON epochs cannot stop already-running external effects. No transfer/import/live activation without proven quiescence of legacy writers. Config/schema validation and CAS apply to every mutating command, callbacks included. Pointer remains a discovery aid, never binding authority.

## Task Dependency Graph

| Task | Depends on | Dependents | Reason |
|---|---|---|---|
| 1. Baseline/RED checkpoint | None | 2 | Establish exact source and safe isolated candidate |
| 2. Storage and binding core | 1 | 3 | Run identity/CAS/publication semantics must precede adapter mutations |
| 3. Runtime adapters and network specialization | 2 | 4 | Actual hooks and retained domain gates must satisfy same binding contract |
| 4. Canonical propagation and validation | 3 | 5 | Review requires coherent generated candidate and passing selected checks |
| 5. Independent exact-candidate review | 4 | Controller closeout | Required QC/red-team must assess final content, not an earlier draft |

## Parallel Execution Graph

Sequential sole-writer waves: 1 → 2 → 3 → 4. Within each wave, independent read-only tests may run concurrently on distinct fixtures. Wave 5 reviewers may run read-only in parallel if controller permits; no leaf dispatch. No estimated speedup claimed without timings.

## Tasks and category/skill recommendations

These are controller recommendations, not delegation requests by this leaf. Reuse this session for writer checkpoints.

### Task 1: Baseline and RED checkpoint
Category `implementation`: bounded evidence capture. Skills: `professional-business-writing` for progress prose; `git-master` for worktree/history if available. Acceptance: hashes, source unchanged, RED evidence and bounded mapping. Status: checkpoint artifacts produced, not repair completion.

### Task 2: Storage and binding core
Category `implementation`: one writer, existing enforcement scope. Skills: `workflow-sequencing` for lifecycle invariants. Depends on 1. Add failing tests first, then minimal schema, stable advisory lock, CAS, publication, import and retention implementation. Acceptance: isolation, race, stale owner, quiescent transfer, fault injection, legacy and cap tests pass. Keep function budgets; do not introduce a second competing state implementation.

### Task 3: Runtime and network adapters
Category `implementation`. Skills: `workflow-sequencing`, `professional-business-writing`. Depends on 2. RED actual plugin/hook failures before fixing explicit bindings, callbacks, commands/compaction/resume and leaf wording. Adapt network gates in place. Acceptance: real adapter tests cover error/timeout/corruption, nested roots and task:false leaf; original singleton byte-identical.

### Task 4: Propagation and validation
Category `implementation`. Skills: `file-structure-design`, `qa-validation`, `professional-business-writing`. Depends on 3. Tighten contradiction validator first; update canonical templates/generator and only target adapters. Acceptance: two generation passes byte-stable, selected canonical tests/validator and network tests pass, diff check clean, main unchanged. Do not propagate to product engineering.

### Task 5: Independent review
Categories `code-review` and `security-review`, controller-owned dispatch only. Skills: `qa-validation`, `red-team-analysis`. Depends on 4. Acceptance: independent exact-candidate QC/red-team; mandatory findings repaired by this sole writer and affected checks/review repeated. No broken Oracle rerun.

### Skills evaluation across tasks

Included recommendations are scoped above. For each task, omit the other task-specific skills unless its scope expands. Omit `agent-design` and `skill-design`: no new roster or reusable skill design. Omit `domain-research` and `source-validation`: current work is local enforcement, not a new domain research assignment. Omit `objective-decomposition`: controller supplied bounded objective. Omit `final-packaging`: no final delivery at this checkpoint. Omit `dev-browser`, `playwright`, `frontend-skill`, `frontend-ui-ux`, and `emil-design-eng`: no browser/UI work. Omit `github-pr-resolution`: no PR changes authorized. Git skill availability is not established; commands used standard explicit worktree/status/history operations, without history rewriting.

## Commit Strategy

No commit or staging authorized. If later explicitly authorized, propose atomic green changesets: (1) core storage/binding with tests; (2) actual adapters plus network gate-preserving adaptation and tests; (3) canonical contract/generator/validator plus generated parity. Avoid a publishable unsafe half-migration; combine dependent changes into one cohesive commit if intermediate states would weaken enforcement. Never include unrelated main WIP or bulk-force-add the ignored network tree. Controller must select an explicit network artifact delivery mechanism before committing ignored outputs.

## Success Criteria

Checkpoint success is provenance and reproduced defects only. Repair success requires the complete requested acceptance matrix, preservation of main/product/singleton, two-pass generation, actual adapter tests and independent exact-candidate review. No release authority or completion claim follows.

## TODO List (ADD THESE)

- Wave 2: Resume this writer for Task 2; blocks Task 3; category `implementation`; skill `workflow-sequencing`; QA race/CAS/publication/import/retention tests.
- Wave 3: Resume for Task 3 after Task 2; blocks Task 4; category `implementation`; skills `workflow-sequencing`, `professional-business-writing`; QA actual plugin/hooks and network gates.
- Wave 4: Resume for Task 4 after Task 3; blocks Task 5; category `implementation`; skills `file-structure-design`, `qa-validation`, `professional-business-writing`; QA generator twice, validators, selected tests and diff/source checks.
- Wave 5: Controller arranges Task 5 after Task 4; categories `code-review`/`security-review`; skills `qa-validation`, `red-team-analysis`; QA exact-candidate findings with sole-writer repair loop.

Execution instructions: retain one writer, this worktree and this record; do not dispatch from this leaf. Stop after each bounded controller checkpoint. Track work in the controller's existing record without creating another competing progress log.

## Checkpoint 2 — isolated storage and binding core

Authorized scope: storage/binding only; no adapter activation, original/live initialization or migration. All state execution used temporary test fixtures. Same writer, candidate and base retained. Guidance reused from checkpoint 1; new Outline search returned unrelated operational history, not implementation authority.

### History and filesystem references

[VERIFIED] Read the 2ac545c plugin diff: its parent-walking package resolution and permissive ambiguity branch explain why this core accepts only an explicit canonical absolute workspace with its own package marker. Inspected 8f0f5dc history/stat showing canonical `enforcement/` as shared implementation owner. The path-filtered 57fe142 shell diff was empty; no claim that it supplied storage semantics. Local search found no existing flock/state_version/owner_epoch implementation in canonical package. New module belongs in existing `enforcement/`, not a parallel service.

[VERIFIED, retrieved 2026-10-01] Linux man-pages 6.19, the Linux kernel/C-library documentation project:

- https://man7.org/linux/man-pages/man2/flock.2.html — exclusive advisory locks attach to open file descriptions; nonblocking contention fails; locks do not constrain noncooperating writers. Use one stable package-store inode, never replace or unlink it.
- https://man7.org/linux/man-pages/man2/fsync.2.html — file fsync alone does not persist its directory entry; explicitly fsync the containing directory.
- https://man7.org/linux/man-pages/man2/rename.2.html — rename replacement is atomic on a filesystem; cross-filesystem rename fails. Same-directory temporary files avoid that boundary. Atomic visibility is not multi-file transactionality.
- Python os documentation lookup (`https://docs.python.org/3/library/os.html#os.fsync`) returned HTTP 503; not used as retrieved evidence.

### Exact implementation scope

- Added `agent-packages/workflow-designer-agent/enforcement/run_store.py`: reusable Python library, not wired into any runtime. Explicit store initialization with immutable versioned config; strict workspace/run/session identifiers; nonblocking stable package flock; expected owner/epoch/version checks; monotonic state version; separate owner epoch; same-directory flushed/fsynced replacement plus directory fsync.
- Added `agent-packages/workflow-designer-agent/tests/test_run_store.py`: fixture-only standard-library tests, including real multiprocess claim/update/retention competition.
- Added `checkpoint2-evidence/red-observations.json`; final test log, preservation receipt and candidate hashes are adjacent evidence, not a second progress record.
- Updated this authoritative progress record only. Existing scripts, root hooks/plugins, generated adapters, network package and singleton remain unchanged.

State is durably written unpublished, then discovery pointer written, then state marked published. Either interruption boundary denies run use. Discovery never substitutes for explicit run/session lookup. Session records cannot be retargeted; binding changes also compare owner/epoch/version and increment state version. A transferred owner invalidates previous epoch-bound sessions. State and domain payload are separate; phase gates/revision_count remain opaque domain data for later adapter validation.

Admission refuses protected-cap exhaustion; retention is explicit, under the same lock, with exact CAS, terminal/inactive state and quiescence evidence. Minimal permanent retirement markers prohibit run-ID reuse (avoiding stale-token ABA). No lock inode deletion/replacement. Retirement markers do not count toward retained full-run capacity; their cumulative metadata growth is a known limitation, not silently garbage-collected.

Legacy import reads only the fixed package singleton path, requires an explicit matching run_id, exact CAS and quiescence evidence, and preserves original bytes. Interrupted matching imports resume; conflicting identity/content/owner is denied. Fresh runs start with empty domain data. Legacy singleton lacking matching identity is refused, not inferred from a date/pointer. No assertion that live writers are quiesced. Quiescence evidence is a caller-supplied precondition; JSON fencing cannot stop already-running effects, and later authorized adapters must validate evidence rather than treat a string as independent proof.

### TDD evidence and quality limits

Actual command: `python3 -B -m unittest discover -s agent-packages/workflow-designer-agent/tests -p test_run_store.py`.

RED progression: 12 missing-module errors before implementation; first 12 green; added tests produced two behavioral failures (corrupt-pointer overwrite and retired-ID reuse); fixed both and reached 18 green; added session-binding tests produced two missing-method errors; implemented bindings and reached 22 green. Added actual multiprocess update/retention coverage before the final run. Final exact results are in `checkpoint2-evidence/tests.txt`.

Additional checks: storage-module LSP diagnostics returned no errors; helper line-budget inspection identified `remove` at 21 nonblank lines and it was reduced. Formatting is automatically applied by the editing environment. Final syntax/diagnostic, line-budget, whitespace, source-preservation and candidate-hash receipts are recorded with the final run.

The scope is cooperative single-host local filesystem access. Config requires `filesystem: local` but does not independently certify the mount type; live use must establish that precondition. This is not protection against a malicious same-UID process replacing directories or bypassing advisory locks. Fsync failure after rename is an ambiguous persistence outcome: do not blindly retry with old CAS; reread the exact run. Fault tests inject exceptions, not physical power loss.

### Runtime integration remaining / atomic commit boundary

Not activated or claimed green: existing singleton shell, OpenCode plugin, Claude/other hooks, callback/compaction/resume adapters, network phase/specialist receipt validation, generated contracts and whole-package validator. Storage `update` is an internal domain-data primitive, not an authorization gate; do not expose it directly to model tools. Checkpoint 3 must route authorized domain transitions through this core and preserve network-local gates. Existing checkpoint1 runtime defects remain until that integration.

No staging/commit performed. If explicitly authorized later, this core and tests form one atomic changeset, kept inactive until adapters are coherently integrated. Do not commit or publish a migration that leaves competing legacy writers active. Independent exact-candidate QC/red-team remains controller-owned and pending.

## Checkpoint 3 — actual adapter integration

Routing revision 82 fetched live on 2026-10-01 during this checkpoint, replacing the prior observed r80 receipt; coordinator-owned /update routing and sole-writer boundary unchanged. No Outline edits. Same candidate and base retained.

### Implementation and evidence

Canonical `enforcement/run_cli.py` is the JSON-only deployed boundary; `run_policy.py` handles scoped tool checks, phase transitions and dispatch/effect receipts; `run_hook.py` handles hook events. The old shell implementation is replaced by a thin entry point and accepts no legacy command flags or state-path overrides. Root, canonical installed copies and network-local adapters are distributed by candidate-only `checkpoint3_sync.py`. Network `network_policy.py` preserves specialist mapping and requires completed run/phase/dispatch/agent-bound evidence; failed/cancelled/input_required receipts no longer satisfy successful gate completion. All 17 network phase/specialist entries and implementation/revision maps remain intact. Network source and installed configs match.

The plugin no longer initializes state or walks parents. Session SDK directory resolution selects only an exact workspace, then persisted session binding supplies the run. Mutation requests pass owner/epoch/version CAS. Before/after hooks hold in-flight effects for writes and dispatch; delayed callbacks retain their original envelope. Compaction and resume retain bound identity. Failed/malformed/missing/timeout subprocess results throw or return nonzero; only explicit success/allow passes. Unknown legacy transitions (including model-driven approval/recovery) are disabled rather than left as alternate writers.

Task:false leaf reads are demonstrated; leaves cannot dispatch or pass coordinator gates. Coordinator task absence denies dispatch; allowed agent names are explicitly pinned in the actor handoff. The added agent-scope test first reproduced a gap, then passed after the allowlist check. Domain configuration is pinned in run data; on-disk policy drift denies requests. Actors and session enrollment are separately authorized operator setup, not automatic initialization.

Command/contract edits: canonical AGENTS, dispatch protocol and four commands; network AGENTS, dispatch protocol and resume-execution; root AGENTS; shared run-binding documentation. Removed canonical fallback-role adoption and progress-inference resume. The existing generator's command-only function propagates these changed commands to platform copies; full generator/template/validator propagation remains checkpoint 4. No generic generator run over the network package occurred. Product engineering is untouched.

Actual RED evidence: three Python entry-point failures and one Bun plugin failure before repair. Final commands/results are in `checkpoint3-evidence/final-checks.json` with raw logs `test-0.txt` through `test-3.txt`; exact candidate paths/hashes are in `candidate-paths.json`. Installed runtimes: Bun 1.3.11, Node 22.22.0, Python 3.13.5. No install. Tests execute actual plugin handlers and actual shell/Python processes; only SDK registration and session lookup are fixture stubs. This is not a live host end-to-end activation claim.

Final selected checks: 24 storage tests, 13 runtime Python tests, 10 Bun plugin tests, and two existing network config/phase alignment tests. A first network pytest command used the wrong working directory and collected nothing; corrected package-local execution passed. Actual plugin/hook tests include missing scripts, invalid JSON, subprocess errors/timeouts, stale callbacks with byte preservation, pointer movement, malformed/dangling pointer, unsupported schema, compaction and hook-envelope relay. Original/main preservation is checked separately from expected candidate snapshot changes.

### Remaining integration boundaries and findings

- No live enrollment, migration, restart or activation; no claim legacy writers are quiesced.
- The live OpenCode/Claude host contract for workflow_receipt metadata and callback-envelope relay is not proven. Missing relay fails closed. Bun tests mock only SDK/tool registration, not enforcement subprocesses.
- A callback whose original CAS token was superseded by intervening state updates is deliberately rejected; its effect remains unresolved. A real nested worker that updates shared state therefore needs an explicit reviewed reconciliation/receipt-token protocol before operational activation. Do not silently refresh to latest. This is an unresolved lifecycle/liveness integration finding, not a passing nested-work execution claim.
- Opaque bash/exec work remains denied until exact-action authority mediation exists. No broad shell approval fallback. This restricts functionality; it is not a declaration of operational readiness.
- New policy/hook event handlers are within the 40-line handler budget; storage helpers remain within 20. Static LSP cannot resolve the uninstalled plugin/Bun/Node declarations and dynamically deployed Python imports. Installed-runtime tests pass; no full typecheck pass claimed. These environment limitations remain visible for independent review.
- Checkpoint 4 must update the general generator to distribute Python dependencies and preserve network-local policy/config, tighten contradictory-contract validation, reconcile residual generated-agent wording and perform two-pass full generation. The bounded sync helper is evidence tooling, not a second production generator.

Atomic commit strategy unchanged: no staging or commit authorized/performed. Keep core and integrated adapters/tests together if separate commits could expose mixed legacy/new writers. Independent exact-candidate QC/red-team remains mandatory and controller-owned; no release authority follows from these tests.

## Checkpoint 3b — scoped intermediate QC repairs

QC provenance: `session_read` for `ses_f09259c2affefTD8qrTCbzqMYZ` returned Session not found. The user's F1–F7 summary is the supplied review evidence; no full report or final package-wide review is claimed. Scope is F1/F2/F7 core lifecycle plus F6 operator path. F3/F4/F5 remain mandatory next-checkpoint work, not optional recommendations. Existing routing r82/controller guidance reused; no dispatch or coordinator-role adoption.

### Changes and safety contract

- Added canonical `enforcement/run_effects.py`: versioned typed effect identities, scope/authorization/attempt fencing, durable origin-session/call lookup, signed completion proof validation and explicit reconciliation. Active effect IDs are indexes into persistent records, not sufficient authority to complete an effect.
- Updated `run_policy.py` to use typed begin/end handlers; an end-kind/origin mismatch rejects leaf attempts to consume a parent dispatch. Failure/reopen increments phase attempt and invalidates old receipts. Updated `run_cli.py` with effect-status and reconcile-effect, and a root-explicit testable entry point.
- Updated `run_store.py` with a transaction-local exact-replay check under the existing package lock. Accepted first completion consumes caller-supplied CAS and increments state_version once. Exact replay may recognize the already-consumed request without writing; a different request digest or changed authorization/attempt rejects. No read-latest replacement for mutation CAS.
- Added `run_operator.py` and `operator_cli.py`: explicit pinned-policy run creation, profile-validated enrollment, terminal-child attestation, signed completion evidence, signed human-declaration import and same-phase quiescent recovery. Authentication uses an inherited capability descriptor and private local key, not model request text. No source/live capability or state was installed; only disposable fixture capabilities were used.
- Updated network-local `network_policy.py` to require the current phase attempt and deliverable digest, current-attempt marker and a completion-proof digest. The existing specialist and phase maps are unchanged.
- Extended `run-binding.md`, the bounded candidate sync file list, and added `tests/test_effect_lifecycle.py`. Two existing runtime negative regressions first reproduced cross-kind completion and old network receipt reuse.

Reconciliation requires an explicitly authorized coordinator reconciler, the original immutable effect identity and random token, operator-authenticated allowed-producer completion proof, terminal registered children, same workspace/run/owner/epoch/scope/authorization/attempt and a fresh explicitly supplied expected tuple with reason provenance. A normal parent callback that predates child enrollment/mutations remains byte-preserving rejected. Reconciliation does not increment revision_count. Conflicting replay, substitutions, revocation and unknown effects deny.

Operator attestation establishes a trusted local operator's statement about producer completion or human approval. It does not independently authenticate a human's identity or prove live process termination. The domain operator must provide that evidence; fixture tests do not establish live quiescence. The capability file and enforcement targets remain subject to F3 protection; do not activate while ordinary file tools can access or replace privileged material.

### RED-first and selected verification

Before implementation, six lifecycle tests failed for the missing operator path. Separate actual-shell regressions reproduced both F2 cross-kind consumption and F7 old same-phase receipt reuse. After typed lifecycle implementation, a direct network-policy test still reproduced old-attempt acceptance; the attempt/deliverable checks repaired it.

Selected final commands and raw outputs are in `checkpoint3b-evidence/`. Coverage includes nested parent→task:false child work→terminal child→unchanged stale parent rejection→explicit reconcile→empty effects→gate; overlapping children completed in reverse order; enrollment version changes; token/session/run/kind/phase/digest substitutions; authenticated producer checks; multiprocess reconciliation races; simulated lost response after durable commit and exact replay; actual JSON-shell nested flow; actual inherited-FD operator enrollment; bounded recovery; and old network receipt rejection. Prior checkpoint3 host success tests are not current proof after this stricter core protocol change: F4 must replace unsigned host receipt assumptions with this contract.

### Remaining mandatory findings and commit boundary

- F3: ordinary file-tool target and argument enforcement, including state/config/lock/enforcer/binding/key protection, traversal and symlinks — not attempted here.
- F4: registered host before/success/failure lifecycle, durable lookup consumption, signed completion/envelope relay and truthful unsupported-host declarations — core lookup is implemented; host integration remains unproved and existing unsigned metadata fails closed.
- F5: bounded exact-action diagnostic/test/mutation adapter and bash_is_conditional configuration reconciliation — not attempted here.
- Structural `loc-breach` findings identified during this bounded repair: formatting expands several new validation/identity helpers beyond the 20-line utility budget (notably validate_profile and make_record), and operator dispatch exceeds 40 lines. Record retained for scoped follow-up; no claim of structural review clearance or complete static typecheck. Runtime imports remain dynamic, with editor resolution warnings.

No commit/staging authority or action. Atomic strategy: keep typed lifecycle, store transaction/replay semantics, operator validation, network attempt checks and regression tests in one cohesive changeset; host integration must not publish a mixed unsigned/typed operational contract. This is an intermediate repair checkpoint, not final package acceptance, activation or release approval.

## Checkpoint 3c — quiescent return after controller timeout

The controller's 30-minute polling timeout did not terminate or replace this writer. On reattachment, this same writer completed the current bounded test pass and stopped before propagation/review. No background agent or live host work was started. Test processes were awaited; fixture-process cwd inspection and main preservation results are in `checkpoint3c-evidence/preservation.json`.

### Completed edits and actual tests

- F3: complete tool arguments reach policy mediation. Canonical targets must be explicitly in the actor handoff; protected enforcement/config/capability paths, traversal, symlinks and hardlinks are denied. Patch headers enumerate add/update/delete/move targets before mutation. Directory searches are bounded. Active effect targets reserve their paths against cooperating tool writes.
- F4: OpenCode plugin now uses durable origin session/call lookup, not an in-memory pending map. It forwards actual arguments, creates/enrolls native task children from an operator-pinned child profile, consumes typed host observations through the authenticated operator boundary, and records explicit authorized reconciliation provenance. Trusted failure observations become terminal failures rather than successful receipts. Duplicate matching callbacks after plugin recreation are no-ops. New exact-action tool has an actual registered success path.
- Claude file-hook fixtures exercise the registered PreToolUse/PostToolUse/PostToolUseFailure lifecycle and durable lookup without invented echoed context. Successful pre-hooks do not auto-approve native host permission requests. Claude Task/Agent dispatch and custom action adapters are explicitly unsupported; unknown subagent bindings do not inherit parent authority. Candidate settings register the matched lifecycle, preserving unrelated settings entries. No settings were activated in the live host.
- F5: added operator-pinned argv catalog with executable/input hashes, explicit action IDs, bounded subprocess execution without a shell, and exact signed-human-approval matching for mutation-class definitions. Raw bash/exec remains rejected in favor of workflow_action. Candidate configs remove bash_is_conditional and identify exact-action-v1. A real pinned diagnostic executes successfully through the actual OpenCode custom tool.

Final current test pass: storage 24/24; lifecycle/mediation 20/20; actual JSON-shell/hook 17/17; Bun actual plugin 15/15 with 22 assertions. All four commands exited 0. `checkpoint3c-evidence/test-receipt.json` records the synchronous tool result, not a fabricated raw transcript. SDK tool registration/session APIs are fixture stubs; plugin handlers, operator authentication and enforcement subprocesses execute real candidate code. No full live model session or deployment acceptance is claimed.

### Host contract evidence

- Installed OpenCode version: `0.0.0-branch-from-22c1c40-202608050252`. Read-only `git show 22c1c40` from `/home/jfi/GitHub/opencode-release-turn-fix` inspected `packages/plugin/src/index.ts`, `packages/plugin/src/tool.ts`, `packages/opencode/src/session/processor.ts`, and `packages/opencode/src/tool/task.ts`. No fork files or original session prompts were read or modified beyond these source objects. This confirms before/after hooks, message.part.updated error records, native task_id/sessionId semantics, and lack of callID in custom-tool context.
- Official OpenCode plugin reference retrieved 2026-10-01: https://opencode.ai/docs/plugins/ (page last updated Sep 29, 2026). Its argument-mutation and event contracts were checked against the installed source baseline, not assumed from latest documentation alone.
- Installed Claude Code version: 2.1.286. Official reference retrieved 2026-10-01: https://code.claude.com/docs/en/hooks . Tests use documented cwd/session/tool_use_id/tool_input fields and separate success/failure events. Claude child-agent dispatch identity remains unsupported rather than inferred.
- OMO or other replacement task providers have not been certified against the native task_id/sessionId contract. Missing/mismatched child receipts fail closed. This is a host-provider acceptance boundary, not a claim that all OpenCode task overrides work.

### Remaining work — do not propagate or claim closure yet

F3 still needs the complete positive multi-file/rename/search and argument-substitution matrix against actual providers, plus adversarial review of filesystem race boundaries. The supported tools mediate targets, but this is not an OS sandbox against noncooperating same-UID processes.

F4 needs broader provider-specific acceptance and failure/child-cancellation coverage. Native OpenCode happy path, task:false worker, missing coordinator dispatch, restart lookup, duplicate completion, and error events pass. Claude Task/Agent remains intentionally unsupported; the working primary path is the pinned native OpenCode adapter. No original host config activation is authorized.

F5 still needs an executed authorized-mutation approval/denial matrix, action-input drift/timeout tests, and full phase/authority review. In particular, mutation-class exact actions must be checked against current phase/revision/domain authority as well as the implemented actor/action grant and human receipt; do not treat the present diagnostic success as that missing acceptance. Registered code is operator-reviewed and hash-pinned; no claim of an OS process sandbox or safety of unreviewed test code.

Scoped structural cleanup is incomplete. Several prior helpers were split or reduced, but actual remaining Python function-budget findings are counted in `checkpoint3c-evidence/size-findings.json`; no zero-finding or complete static-typecheck claim. This is retained work, not hidden by passing runtime tests. Current TypeScript SDK/Node/Bun declaration resolution remains unavailable without installation; Bun executes/transpiles the module successfully.

Atomic commit strategy remains one coherent lifecycle/mediation/adapter/test changeset if splitting would expose mixed contracts. No staging, commit, install, restart, migration, release, propagation run or independent-review dispatch occurred. Resume this same writer only for the remaining scoped work; original main and product engineering remain outside the write boundary.

## Checkpoint 3d — remaining bounded runtime acceptance

Same sole writer, worktree and base. This checkpoint adds missing acceptance and refactors existing owners; no new production module, unrelated scope, full generator run or review dispatch. Existing controller/routing guidance reused. Main preservation, candidate hashes, quiescence, test logs and actual size findings are recorded in `checkpoint3d-evidence/`.

### Repairs and tests

Shared mutation authority now governs both native writes and exact mutation actions: run authorization must remain active; phase must be assigned and in the implementation/revision map; the phase must be in progress; prior gates must have passed; dispatch failure/escalation blocks mutation; network coordinator-only authority cannot execute specialist work. Exact human receipts additionally match owner epoch, current phase and phase attempt with strict value types. Signed approval revocation disables prior receipts for the same action subject hash.

RED tests first demonstrated an out-of-phase mutation, boolean phase substitution and ineffective signed revocation. The final suite includes denied and successful authorized mutations, fresh revision-phase receipt acceptance, stale-phase receipt rejection, executable/input drift controls, and bounded timeout leaving the effect protected for a failure receipt. No arbitrary shell or inline-evaluation fallback was introduced.

Mediation tests now include positive multi-file add/update/move headers and scoped glob/grep, conflicting path-key substitution, symlink replacement between check and begin, and a competing mutation denied by an active target lease. Actual plugin tests retain working task:false and native task parent/child paths and add cancellation with an active child: parent/unknown error events do not release the protected effect; after the child's trusted terminal failure, the parent can terminalize as failed, never successful. An unverified task provider's foreign child metadata is rejected without state change.

All 15 recorded structural breaches were addressed in their existing files: shared mutation authority replaces duplicated gate logic; schema field sets and subprocess policy move to named module constants; effect call identity, child registration, proof binding and completion packet construction are separated by responsibility. Final size findings are measured with the same helper/handler budgets and classifier as checkpoint3c, not a relaxed threshold. See the actual `size-findings.json`; no complete static typecheck claim is made.

### Filesystem race and provider assessment

Cooperating model-tool mutations revalidate full canonical arguments during locked effect admission; active target leases prevent overlapping approved actions and native writes. Input/executable hashes are checked before approved execution. Tests prove a symlink swap before begin is rejected and competing mutation leaves state unchanged.

This workflow-layer boundary cannot make a third-party native tool's later filesystem open atomic with preflight validation. A noncooperating same-UID process changing a symlink or executable after admission remains a TOCTOU risk. No claim of OS sandboxing, openat/fexecve pinning or protection against a hostile operator is made. Activation requires exclusive workspace/control-file ownership and operator-reviewed, hash-pinned action code; stronger hostile-process guarantees require a host executor/sandbox boundary outside this repair. Exact actions remain trusted reviewed code, not permission to run arbitrary newly edited tests.

Compatibility remains the version-checked native OpenCode contract and tested Claude file-hook contract. OMO/replacement task integrations are not claimed working; foreign/missing child identity fails closed. Claude Task/Agent dispatch is still explicitly unsupported. No live service, config activation, credentials or original session prompts were touched.

Atomic strategy: preserve authority gates, receipt semantics, existing-file refactors and regression tests together; do not split into a state that permits mixed enforcement. No staging/commit/push/merge/install/restart/deploy occurred. This is runtime acceptance evidence for controller routing, not final package propagation, independent-review approval or release authority.

## Checkpoint 4 — production generation and exact-candidate review handoff

Routing r82 re-fetched live on 2026-10-01; same controller-owned /update and sole writer. No new writer, original mutation or live activation. Production `scripts/sync-platform-configs.py` now owns complete runtime generation, local hook merging and explicit shared-runtime refresh. `checkpoint3_sync.py` is retired rather than left as a competing copy implementation. Destructive skill-directory cleanup was removed; existing local preflight scripts, network specialist policy and phase maps are retained.

Canonical agents, agent/workflow templates, generation prompt, operating contracts and README now carry the coordinator/leaf distinction and immutable binding requirements. Generated OpenCode workers explicitly load task:false. The actual Bun worker test reads that generated implementation-planner contract before exercising harmless scoped work; coordinator missing-dispatch denial remains separately tested. These are artifact-loaded fixture tests, not live model dispatch certification. The deterministic validator now rejects a broad stop clause even when a leaf exemption appears elsewhere. A validator false positive in descriptive contract prose was resolved by clarifying the prose, not relaxing the negative test.

Retirement metadata is bounded: combined full runs and retirement markers cannot exceed four times immutable retained-run capacity. Admission refuses at exhaustion; fences, protected runs and the lock are not removed. RED cap-exhaustion coverage failed before the guard and passed afterward. This bounds retirement history, not every possible evidence payload byte.

Baseline triage was performed once: canonical validator 54/54 PASS before adding the new role-contract check. Full network baseline produced 24 PASS/7 FAIL: stale golden-fixture requirements, three tests for the intentionally removed singleton CLI, and local preflight overwritten during the first production-generator trial. The generator now retains local preflight; its network script was restored only from its hash-verified original snapshot. Golden fixtures were completed without weakening validation, and receipt tests now exercise actual typed JSON requests and authenticated fixture attestations. No unrelated main WIP was imported. The full network suite then passed 31 tests.

Production generation is run twice over root, canonical-local and network-local targets. Exact generated hashes, local network config/policy preservation, all raw commands/results, validator reports and the consolidated manifest are under `checkpoint4-evidence/`. `candidate-manifest.json` covers tracked/untracked/ignored changes against HEAD plus explicit checkpoint1 import hashes, with before/base/import and candidate digests; only the manifest's recursive self-hash is excluded. Main preservation is recorded separately. Review must use this final candidate rather than earlier checkpoint hashes.

Compatibility limits remain: version-checked native OpenCode contract and Claude file hooks; OMO/replacement task providers are uncertified and Claude Task/Agent is unsupported. Hostile same-UID filesystem races require host-level controls; no OS sandbox or live infrastructure acceptance is claimed. Historical singleton data remains untouched. The changelog entry is Unreleased, with independent focused QC/red-team pending—not a version release or approval.

Atomic commit strategy: one coherent repair changeset containing source runtime, generator, contracts/templates, validators, generated adapters and tests; do not commit incomplete mixed contracts. No staging/commit/push/merge/restart/deploy occurred. This is the controller's exact-candidate handoff for independent focused review, contingent on the final evidence results; it does not claim reviewer approval.

## Focused review repair — Q1–Q5

Review provenance: user supplied five mandatory HIGH findings against manifest `0cfe3d31941720dde549fb6400349b77a008e725b8907e877988e38d57e5aeab`. The full review session was not claimed accessible. Same writer, candidate, base and original boundaries retained. All five issues were reproduced in failing tests before repairs; passing earlier suites did not invalidate those findings.

- Q1: exact-action input/output leases and existing lease comparisons now use the same canonical workspace-relative namespace as native tools. Absolute, ./ and directory aliases are tested; root directory reservations cover descendants. The signed definition is retained unchanged. Overlap denies without state mutation; disjoint work remains allowed.
- Q2: state reads and post-mutation publication validate typed effect identity, record keys, run/owner bindings, lifecycle status and exact equality between running records and the active index. Missing/orphaned/mismatched/terminal index corruption denies reads, transfer, finish and retention without repair. The old bare-ID effect API is explicitly disabled; typed lifecycle tests retain the valid quiescent transfer path. Shared identity hashing/validation replaces duplicated checks.
- Q3: network gates resolve the authoritative effect, require receipt equality, verify completion-proof digest/signature/producer/outcome and current owner, authority, phase attempt and deliverable. Tests cover valid completion plus missing, altered, orphaned, mismatched, stale-owner/authorization/deliverable and validly signed wrong-outcome/producer cases.
- Q4: one progression guard blocks dispatch and successful gates on escalation or revocation, including after three real fail transitions. Inspection and failure handling remain available without clearing authority holds. An authenticated operator-only clear-hold command requires exact CAS, quiescence and signed audit provenance. Bounded revision extensions preserve revision history; revocation clearance changes authority identity and invalidates attempt receipts. Ordinary recover/model requests cannot clear the hold.
- Q5: hook merging identifies managed handler signatures by exact command/type/args, not filename substrings. It removes/replaces only managed entries, retains unrelated controls and group metadata, and merges the current managed entries without duplicate growth. Mixed groups, similar filenames, multiple matchers and repeated generation are tested.

Production regeneration, affected runtime suites, validators, network tests and two-pass byte stability are rerun into `review-repair-evidence/`; the new manifest supersedes the reviewed candidate but does not overwrite its evidence. Raw commands/results and main preservation are in that directory. Native OpenCode/Claude file-hook boundaries and unsupported OMO/Claude Task providers are unchanged. No install, commit, push, merge, migration, restart, deployment or live activation occurred.

Atomic strategy: keep Q1–Q5 runtime/schema/gate/generator changes and their regressions together; review the replacement exact manifest before any acceptance claim. The independent reviewer must recheck these fixes. This record is not a self-issued approval.

## Q5-R1 — original-settings migration repair

User-supplied focused re-review closed Q1–Q4 but reproduced a missing-signature migration defect in Q5. No full-session access or approval is inferred. The same writer changed only exact generator ownership signatures plus regression/evidence tooling; Q1–Q4 runtime logic was not changed.

Verified original root and network settings against checkpoint1 hashes, then captured byte-identical fixtures with provenance under the canonical tests. Root SHA-256: `f2e36a97dc75f1a54dfebfba95b0a8941d9bf5016c3e78e217938df1e728afcb`; network SHA-256: `5ee6e01de4e77d8b545aeba53f6aaef7ee5dfa28449bc173d9371a9dd845127c`. The original main files were read only. Production ownership recognition now includes exactly the three observed braced-variable commands for pre-tool-use, pre-compact and dispatch-gate scripts; no substring matching was added.

RED: migration from original network settings retained 11 matching Write workflow handlers; root retained 3. GREEN: both provenance-backed tests now require exactly one managed handler for each supported event/tool, retain the mixed security-domain approval hook and group metadata, verify installed executable permissions, execute actual registered Write pre-hook → fixture file write → post-hook, and assert no active effects remain. The unrelated security hook executes once. A second production sync is byte-identical. This tests migration, not merely an already-clean candidate.

Final affected tests, generation digests, validators, consolidated manifest and main preservation are regenerated under `hook-migration-evidence/`. Its file-inventory groups code/tests, docs, generated artifacts and evidence and separately enumerates baseline imports, including the new original-settings fixtures. This prevents copied baseline material from being reported as newly authored implementation.

Atomic strategy: keep the exact-signature fix and provenance-backed migration regressions together with the repair candidate. No staging, commit, release, install, activation, new writer or original mutation occurred. Q5-R1 still requires the independent reviewer's recheck; unsupported provider boundaries remain unchanged.

## Final approval provenance and bookkeeping boundary

The controller/user reports final independent focused QC and adversarial PASS from session `ses_f09259c2affefTD8qrTCbzqMYZ` against manifest `712bd809162ace0b39da125e232949343811c0c525be784c9130422066a50f62`. The reviewer verified 405/405 entries before and after review, independently exercised both provenance-bound original-settings migrations and a separate original failing probe, and observed one pre-hook and one post-hook exiting 0 with no active effects. The unrelated security hook remained present and executed once; generation remained stable. Q1–Q4 evidence was reused only after verifying their source and installed copies unchanged. No mandatory findings remained. This is attributed controller/user-supplied review provenance; this writer does not claim to have retrieved the full review session.

The reviewed manifest remains immutable. This progress-only append is bookkeeping outside its reviewed content; the final separate receipt records the reviewed progress hash, new progress hash and exact delta. No source, generated implementation, test or reviewed evidence artifact is changed by this final step, and no review coverage is claimed for new source. Existing tests are not rerun because implementation inputs are unchanged. Main hashes/status/HEAD, candidate whitespace and final file counts are checked afresh and recorded in `hook-migration-evidence/final-receipt.json`, separately from the manifest to avoid recursive repackaging.

Unsupported OMO/replacement task integration, Claude Task/Agent/exact-action adapters and live acceptance limitations remain in force. Review PASS does not authorize installation, activation, migration, deployment, commit or release. Rollback here means do not promote the isolated candidate; there has been no live migration to reverse, and no destructive cleanup is required or authorized.

Atomic commit strategy remains a future explicit authorization decision: keep the reviewed runtime/generator/contracts/tests coherent rather than exposing mixed enforcement. Nothing is staged or committed. The same writer is now performing final bookkeeping only.
