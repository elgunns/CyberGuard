-- CyberGuard database schema (PostgreSQL).
-- Applied by database/init_db.py. Every statement uses IF NOT EXISTS, so running it again is safe.
-- The full uploaded file is never stored here (FR-16).

-- One row per uploaded log file. Holds the upload details and summary counts.
CREATE TABLE IF NOT EXISTS analyses (
    id                BIGSERIAL PRIMARY KEY,
    original_filename TEXT NOT NULL,
    file_size_bytes   INTEGER NOT NULL CHECK (file_size_bytes >= 0),
    status            TEXT NOT NULL DEFAULT 'uploaded'
                      CHECK (status IN ('uploaded', 'parsing', 'completed', 'failed')),
    total_lines       INTEGER NOT NULL DEFAULT 0 CHECK (total_lines >= 0),
    skipped_lines     INTEGER NOT NULL DEFAULT 0 CHECK (skipped_lines >= 0),
    event_count       INTEGER NOT NULL DEFAULT 0 CHECK (event_count >= 0),
    error_message     TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at      TIMESTAMPTZ
);

-- One row per parsed log line that produced an event. Stores parsed fields, not the raw line.
CREATE TABLE IF NOT EXISTS parsed_events (
    id            BIGSERIAL PRIMARY KEY,
    analysis_id   BIGINT NOT NULL REFERENCES analyses (id) ON DELETE CASCADE,
    line_number   INTEGER NOT NULL CHECK (line_number > 0),
    occurred_at   TIMESTAMPTZ,
    log_level     TEXT,                 -- severity from the log line (FR-05), if present
    event_type    TEXT NOT NULL,        -- for example login_failure, login_success, app_error, http_request
    outcome       TEXT CHECK (outcome IN ('success', 'failure', 'other')),
    username      TEXT,                 -- stored locally only; never sent to Gemini (CLAUDE.md)
    source_ip     TEXT,
    endpoint      TEXT,                 -- web server lines only (FR-06c)
    http_status   INTEGER CHECK (http_status BETWEEN 100 AND 599),
    message       TEXT,                 -- parsed message, with no raw line
    is_suspicious BOOLEAN NOT NULL DEFAULT FALSE  -- set by detection rules (FR-07)
);

-- One row per detected incident (FR-07, FR-08). Types are the four from decision D-09.
CREATE TABLE IF NOT EXISTS incidents (
    id            BIGSERIAL PRIMARY KEY,
    analysis_id   BIGINT NOT NULL REFERENCES analyses (id) ON DELETE CASCADE,
    incident_type TEXT NOT NULL
                  CHECK (incident_type IN ('FAILED_LOGIN_BURST', 'LOGIN_SUCCESS_AFTER_FAILURES',
                                           'REPEATED_APP_ERROR', 'REPEATED_SERVER_ERROR')),
    severity      TEXT NOT NULL CHECK (severity IN ('Low', 'Medium', 'High', 'Critical')),
    status        TEXT NOT NULL DEFAULT 'Open'
                  CHECK (status IN ('Open', 'Investigating', 'Resolved')),
    title         TEXT NOT NULL,
    source_ip     TEXT,
    endpoint      TEXT,
    event_count   INTEGER NOT NULL CHECK (event_count > 0),
    window_start  TIMESTAMPTZ,
    window_end    TIMESTAMPTZ,
    evidence      TEXT NOT NULL,        -- human-readable evidence summary
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Gemini outputs (FR-18, FR-19). Each row is either an incident explanation or an analysis summary.
-- When status is 'unavailable' (FR-21), content is empty and the analysis is still kept.
CREATE TABLE IF NOT EXISTS ai_outputs (
    id          BIGSERIAL PRIMARY KEY,
    analysis_id BIGINT REFERENCES analyses (id) ON DELETE CASCADE,
    incident_id BIGINT REFERENCES incidents (id) ON DELETE CASCADE,
    output_type TEXT NOT NULL CHECK (output_type IN ('incident_explanation', 'analysis_summary')),
    status      TEXT NOT NULL CHECK (status IN ('success', 'unavailable')),
    content     TEXT,
    model_name  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (status = 'unavailable' OR content IS NOT NULL),
    CHECK ((output_type = 'incident_explanation' AND incident_id IS NOT NULL)
        OR (output_type = 'analysis_summary' AND analysis_id IS NOT NULL))
);

-- Record of Telegram alerts sent (FR-22, FR-25 to FR-28). Used for the cooldown checks.
CREATE TABLE IF NOT EXISTS sent_alerts (
    id          BIGSERIAL PRIMARY KEY,
    alert_type  TEXT NOT NULL
                CHECK (alert_type IN ('CRITICAL_INCIDENT', 'HTTP_500_BURST',
                                      'AI_FAILURES', 'BACKEND_DOWN')),
    alert_key   TEXT NOT NULL,           -- for example "incident:42" or "http_500_burst"
    incident_id BIGINT REFERENCES incidents (id) ON DELETE SET NULL,
    sent_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- FR-28b: at most one Critical alert per incident. The database enforces this too.
CREATE UNIQUE INDEX IF NOT EXISTS sent_alerts_one_critical_per_incident
    ON sent_alerts (incident_id)
    WHERE alert_type = 'CRITICAL_INCIDENT';

CREATE INDEX IF NOT EXISTS sent_alerts_key_sent_at ON sent_alerts (alert_key, sent_at);
CREATE INDEX IF NOT EXISTS parsed_events_analysis ON parsed_events (analysis_id);
CREATE INDEX IF NOT EXISTS incidents_analysis ON incidents (analysis_id);
CREATE INDEX IF NOT EXISTS incidents_status ON incidents (status);
CREATE INDEX IF NOT EXISTS ai_outputs_incident ON ai_outputs (incident_id);
CREATE INDEX IF NOT EXISTS ai_outputs_analysis ON ai_outputs (analysis_id);
