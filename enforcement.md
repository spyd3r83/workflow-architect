# Workflow Enforcement

The canonical runtime lives in enforcement/. The production generator installs its complete Python dependencies, shell boundary, OpenCode plugin and matched Claude file hooks. Use `run-binding.md` for the operator and role contract. Generation never initializes or migrates runtime state.

State belongs to an explicitly bound workspace/run/session under .opencode/workflow-runs, not the legacy singleton. Every mutation consumes an expected owner/epoch/version tuple under one stable local advisory lock. Atomic file publication and typed effects protect concurrent transitions. Native host observations are authenticated; delayed callbacks require explicit authorized reconciliation rather than latest-state substitution.

Only a coordinator dispatches task(). Assigned task:false leaves perform their handoffs without delegation. Missing coordinator task() stops dispatch. File tools are scope-mediated; shell commands use an operator-pinned exact-action catalog. Mutation-class actions require current phase/revision/domain authority and exact human approval.

Native OpenCode and Claude file-hook contract tests are fixture-backed evidence, not live activation. OMO/replacement task providers are uncertified; Claude Task/Agent and its exact-action adapter are unsupported. Codex/Copilot/Devin generated agent documents do not establish runtime hook parity. Unsupported execution paths must not bypass the operator boundary.

Retained runs are bounded by configured capacity. Combined runs and permanent retirement markers are bounded at four times capacity, with admission refused at exhaustion. No lock or retirement fence is removed to make room. See `run-binding.md` for filesystem trust and evidence-size limitations.
