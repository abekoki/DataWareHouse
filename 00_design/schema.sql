-- 外部キー制約を有効化
PRAGMA foreign_keys = ON;

-- task_table
CREATE TABLE IF NOT EXISTS task_table (
    task_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    task_set INTEGER,
    task_name TEXT,
    task_describe TEXT
);

-- subject_table
CREATE TABLE IF NOT EXISTS subject_table (
    subject_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT
);

-- video_table
CREATE TABLE IF NOT EXISTS video_table (
    video_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    video_dir TEXT,
    subject_ID INTEGER,
    video_date TEXT,
    video_length INTEGER,
    FOREIGN KEY (subject_ID) REFERENCES subject_table(subject_ID) ON DELETE RESTRICT
);

-- tag_table
CREATE TABLE IF NOT EXISTS tag_table (
    tag_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    video_ID INTEGER,
    task_ID INTEGER,
    start INTEGER,
    end INTEGER,
    FOREIGN KEY (video_ID) REFERENCES video_table(video_ID) ON DELETE RESTRICT,
    FOREIGN KEY (task_ID) REFERENCES task_table(task_ID) ON DELETE RESTRICT
);

-- core_lib_table
CREATE TABLE IF NOT EXISTS core_lib_table (
    core_lib_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    core_lib_version TEXT,
    core_lib_update_information TEXT,
    core_lib_base_version_ID INTEGER,
    core_lib_commit_hash TEXT UNIQUE,
    FOREIGN KEY (core_lib_base_version_ID) REFERENCES core_lib_table(core_lib_ID) ON DELETE SET NULL
);

-- core_lib_output_table
CREATE TABLE IF NOT EXISTS core_lib_output_table (
    core_lib_output_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    core_lib_ID INTEGER,
    video_ID INTEGER,
    core_lib_output_dir TEXT,
    FOREIGN KEY (core_lib_ID) REFERENCES core_lib_table(core_lib_ID) ON DELETE RESTRICT,
    FOREIGN KEY (video_ID) REFERENCES video_table(video_ID) ON DELETE RESTRICT
);

-- algorithm_table
CREATE TABLE IF NOT EXISTS algorithm_table (
    algorithm_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    algorithm_version TEXT,
    algorithm_update_information TEXT,
    algorithm_base_version_ID INTEGER,
    algorithm_commit_hash TEXT UNIQUE,
    FOREIGN KEY (algorithm_base_version_ID) REFERENCES algorithm_table(algorithm_ID) ON DELETE SET NULL
);

-- algorithm_output_table
CREATE TABLE IF NOT EXISTS algorithm_output_table (
    algorithm_output_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    algorithm_ID INTEGER,
    core_lib_output_ID INTEGER,
    algorithm_output_dir TEXT,
    FOREIGN KEY (algorithm_ID) REFERENCES algorithm_table(algorithm_ID) ON DELETE RESTRICT,
    FOREIGN KEY (core_lib_output_ID) REFERENCES core_lib_output_table(core_lib_output_ID) ON DELETE RESTRICT
);

-- 推奨インデックス
CREATE INDEX IF NOT EXISTS idx_core_lib_version ON core_lib_table(core_lib_version);
CREATE INDEX IF NOT EXISTS idx_algorithm_version ON algorithm_table(algorithm_version);


