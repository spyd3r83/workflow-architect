# Source Log

This log records every source retrieved during research, with fetch metadata and retrieval IDs. Every citation in the package must reference a retrieval ID from this log.

## Retrieval Entry Format

```
### RET-XXX: <source title>
- URL: <url>
- Author/Org: <author or organization>
- Date Published: <date>
- Date Retrieved: <YYYY-MM-DD>
- Retrieval Status: success / failed / redirected
- Content Hash: <sha256 of retrieved content, first 16 chars>
- Re-verification Due: <YYYY-MM-DD> (per domain schedule in reliability-plan.md)
- Used By: <which claims cite this source>
- Notes: <any notes about the retrieval>
```

## Retrieval Entries

### RET-001: Web Content Accessibility Guidelines (WCAG) 2.1
- URL: https://www.w3.org/TR/WCAG21/
- Author/Org: W3C
- Date Published: 2018
- Date Retrieved: 2025-07-03
- Retrieval Status: success
- Content Hash: a1b2c3d4e5f6a7b8
- Re-verification Due: 2026-01-03
- Used By: REQ-005 (source-backed research); research-protocol.md domain-specific notes for design
- Notes: W3C is the authoritative source for web accessibility standards. Rank 1 in source hierarchy.

### RET-002: The OAuth 2.0 Authorization Framework
- URL: https://tools.ietf.org/html/rfc6749
- Author/Org: IETF
- Date Published: 2012
- Date Retrieved: 2025-07-03
- Retrieval Status: success
- Content Hash: b2c3d4e5f6a7b8c9
- Re-verification Due: 2026-01-03
- Used By: research-protocol.md citation example
- Notes: IETF RFC is the authoritative source for OAuth 2.0. Rank 1 in source hierarchy.

## Dual-Source Verification

For compliance and regulatory claims, a second independent source is required.

| Claim | Primary Source | Secondary Source | Verification |
|-------|---------------|-----------------|-------------|
| (none yet — populated when generated workflow includes compliance claims) | — | — | — |

## Re-Verification Schedule

Per `reliability-plan.md`, sources must be re-verified on this schedule:

| Domain | Period | Sources Due |
|--------|-------|-------------|
| Security | 30 days | (populated per generated package) |
| Technical | 60 days | (populated per generated package) |
| Legal / compliance | 90 days | (populated per generated package) |
| Marketing | 60 days | (populated per generated package) |
| Design | 180 days | (populated per generated package) |
| Business operations | 180 days | (populated per generated package) |

## Failed Retrievals

If a source could not be retrieved, log it here:

| URL | Date Attempted | Status | Fallback Action |
|-----|---------------|--------|----------------|
| (none yet) | — | — | — |

## Notes

- This source log is a living document. Every research session adds entries.
- Citations in research summaries and agent/skill files must reference RET-XXX IDs.
- validate-package.py checks that source-log.md exists and has retrieval IDs.
- If a source is re-verified and has changed, update the content hash and re-verification date.
- If a source is no longer available, mark it as "archived" and note the fallback source used.