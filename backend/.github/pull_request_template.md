## Summary
- What does this PR change?

## Security / Auth
- [ ] Endpoints are protected with @require_auth
- [ ] Fine-grained permissions via @require_permission
- [ ] Ownership checks where applicable
- [ ] No sensitive data in errors/logs

## Correctness
- [ ] Resume behavior verified (uses persisted mode_id)
- [ ] Redis TTL-safe updates (preserve TTL)
- [ ] Exam lock acquisition is checked + rollback on failure

## Tests / Verification
- [ ] python3 -m compileall app
- [ ] Grep: no raw SQL / db access in service layer
- [ ] Grep: require_permission present on routes

## Notes / Rollout
- Any migration considerations?
- Backwards compatibility?
