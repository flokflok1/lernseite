# Runner API Hardening

## Goals
- Enforce auth + GBA permissions on runner execution endpoints
- Keep service layer free of raw SQL (repository pattern)
- Ensure Redis TTL safety for session state
- Ensure exam lock correctness with rollback on lock conflict
- Use runner-specific ErrorCodes for i18n mapping

## Endpoints
- POST /api/v1/runner/sessions (runner.sessions.execute)
- GET  /api/v1/runner/sessions/{id} (runner.sessions.read)
- PATCH /api/v1/runner/sessions/{id}/state (runner.sessions.execute)
- POST /api/v1/runner/sessions/{id}/finish (runner.sessions.execute)

## Key Behaviors
- Resume uses stored mode_id (does not re-resolve mode)
- Redis state updates preserve TTL
- Exam lock scope: course_id if available else method_id
- Lock conflict returns RUNNER_EXAM_LOCKED (HTTP 409)

## Verification Commands
- python3 -m compileall app
- grep -R "@require_permission" -n app/api/v1/runner
- grep -nE "get_db_connection|db_pool\.connection\(|cursor\(|psycopg" app/application/services/runner/session_service.py
