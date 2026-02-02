# Changelog

## [Unreleased]

### Runner API Hardening
- Added GBA permissions to runner session endpoints (execute/read)
- TTL-safe Redis state updates (preserve TTL)
- Correct resume behavior (use persisted mode_id)
- Exam lock acquisition checked with rollback on conflict (409)
- Runner-specific error codes for frontend/i18n mapping
