-- vulnbench schema: ground truth, benchmark questions, harness findings, scores.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS ground_truth (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    source        TEXT NOT NULL,          -- e.g. secllmholmes-handcrafted, secllmholmes-realworld, terragoat
    file_path     TEXT NOT NULL,          -- repo-relative path within the source repo
    is_vulnerable INTEGER NOT NULL,       -- 1 = vulnerable, 0 = safe/patched
    cwe           TEXT,                   -- normalized "CWE-<n>" or NULL (IaC checks)
    vuln_name     TEXT,
    check_id      TEXT,                   -- checkov check id for IaC oracle rows
    line_start    INTEGER,
    line_end      INTEGER,
    rationale     TEXT,
    cve           TEXT
);
CREATE INDEX IF NOT EXISTS idx_gt_source ON ground_truth(source);
CREATE INDEX IF NOT EXISTS idx_gt_path   ON ground_truth(file_path);

CREATE TABLE IF NOT EXISTS questions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    suite            TEXT NOT NULL,       -- sola_ispm | sola_crossvendor | code_vuln
    qid              TEXT NOT NULL,       -- stable id within the suite
    category         TEXT,                -- e.g. "AWS Hygiene", vendor combo, or CWE
    text             TEXT NOT NULL,
    ground_truth_ref INTEGER REFERENCES ground_truth(id),
    UNIQUE (suite, qid)
);

CREATE TABLE IF NOT EXISTS findings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL,
    harness         TEXT NOT NULL,
    revision_id     TEXT,
    title           TEXT,
    description     TEXT,
    file_path       TEXT,                 -- first entry of code_paths, line stripped
    line            INTEGER,
    code_paths      TEXT,                 -- raw JSON array as ingested
    vuln_type       TEXT,                 -- free text from the harness
    cwe             TEXT,                 -- resolved "CWE-<n>" or NULL
    mitigation_diff TEXT,
    cve             TEXT
);
CREATE INDEX IF NOT EXISTS idx_findings_run ON findings(run_id, harness);

CREATE TABLE IF NOT EXISTS scores (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id             TEXT NOT NULL,
    harness            TEXT NOT NULL,
    gt_id              INTEGER NOT NULL REFERENCES ground_truth(id),
    finding_id         INTEGER REFERENCES findings(id),
    outcome            TEXT NOT NULL,     -- tp_correct_cwe | tp_wrong_cwe | miss | false_positive | true_negative
    expert_score       REAL NOT NULL,     -- 0 | 0.5 | 1
    faithfulness       REAL,
    hallucination_free REAL,
    correctness        REAL,
    retrieval_use      REAL,
    example_adapt      REAL,
    judge_mode         TEXT,              -- offline-heuristic | anthropic
    UNIQUE (run_id, harness, gt_id)
);
