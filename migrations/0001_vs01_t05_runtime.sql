CREATE SCHEMA bsl_runtime;

CREATE FUNCTION bsl_runtime.reject_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'bsl_runtime records are append-only';
END;
$$;

CREATE TABLE bsl_runtime.study_run (
    run_id uuid PRIMARY KEY,
    session_id uuid NOT NULL,
    request_revision integer NOT NULL CHECK (request_revision >= 1),
    supersedes_run_id uuid REFERENCES bsl_runtime.study_run(run_id),
    request_identity char(64) NOT NULL CHECK (request_identity ~ '^[0-9a-f]{64}$'),
    run_key_sha256 char(64) NOT NULL UNIQUE CHECK (run_key_sha256 ~ '^[0-9a-f]{64}$'),
    packet_identity char(64) NOT NULL CHECK (
        packet_identity = 'aebcbb50fc8383f2f4f395bc71116563325c1fde237427dc8c1bc8140e8ebe31'
    ),
    packet_sha256 char(64) NOT NULL CHECK (
        packet_sha256 = '9f81621785924161cc4861e2af9f010bd18e822b60199d62a6327eff44ea0409'
    ),
    packet_receipt_identity uuid NOT NULL CHECK (
        packet_receipt_identity = '01a02bbe-bda5-776b-a95e-16bb40d18597'::uuid
    ),
    packet_receipt_file_sha256 char(64) NOT NULL CHECK (
        packet_receipt_file_sha256 = '02272e1ec458a33e449aa93f9508a57d4eaacf3d9dccc48888f3952bbe96dad4'
    ),
    runtime_spec_sha256 char(64) NOT NULL CHECK (
        runtime_spec_sha256 = '06e97f36db1071d9085688ceb33dbc66f02dd0349889ab4df4d0fa280801d9e5'
    ),
    executor_kind text NOT NULL CHECK (executor_kind = 'DETERMINISTIC_REFERENCE'),
    created_at timestamptz NOT NULL,
    UNIQUE (session_id, request_revision)
);

CREATE TABLE bsl_runtime.runtime_artifact (
    artifact_sha256 char(64) PRIMARY KEY CHECK (artifact_sha256 ~ '^[0-9a-f]{64}$'),
    run_id uuid NOT NULL REFERENCES bsl_runtime.study_run(run_id),
    artifact_type text NOT NULL CHECK (
        artifact_type IN ('REQUEST', 'EXECUTION_RECORD', 'ANSWER_BRIEF', 'ANSWER_STUDY', 'AUDIT_RECEIPT')
    ),
    contract_name text NOT NULL,
    artifact_json jsonb NOT NULL,
    created_at timestamptz NOT NULL,
    UNIQUE (run_id, artifact_type)
);

CREATE TABLE bsl_runtime.runtime_event (
    event_id uuid PRIMARY KEY,
    run_id uuid NOT NULL REFERENCES bsl_runtime.study_run(run_id),
    stream_sequence smallint NOT NULL CHECK (stream_sequence >= 1),
    state text NOT NULL CHECK (
        state IN ('RECEIVED', 'NORMALIZED', 'CLASSIFIED', 'IDENTITIES_RESOLVED', 'PLAN_FROZEN',
                  'EVIDENCE_ASSESSED', 'CANDIDATE_RECEIVED', 'VERIFYING', 'RENDERED', 'AUDITED', 'COMPLETE')
    ),
    artifact_sha256 char(64) REFERENCES bsl_runtime.runtime_artifact(artifact_sha256),
    event_json jsonb NOT NULL,
    previous_event_sha256 char(64) CHECK (previous_event_sha256 ~ '^[0-9a-f]{64}$'),
    event_sha256 char(64) NOT NULL CHECK (event_sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL,
    UNIQUE (run_id, stream_sequence),
    UNIQUE (run_id, event_sha256)
);

CREATE TRIGGER study_run_reject_mutation
BEFORE UPDATE OR DELETE ON bsl_runtime.study_run
FOR EACH ROW EXECUTE FUNCTION bsl_runtime.reject_mutation();

CREATE TRIGGER runtime_artifact_reject_mutation
BEFORE UPDATE OR DELETE ON bsl_runtime.runtime_artifact
FOR EACH ROW EXECUTE FUNCTION bsl_runtime.reject_mutation();

CREATE TRIGGER runtime_event_reject_mutation
BEFORE UPDATE OR DELETE ON bsl_runtime.runtime_event
FOR EACH ROW EXECUTE FUNCTION bsl_runtime.reject_mutation();
