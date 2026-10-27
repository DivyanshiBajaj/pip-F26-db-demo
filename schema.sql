CREATE TABLE student (
    student_id              SERIAL          PRIMARY KEY,
    netid                   VARCHAR(16)     NOT NULL UNIQUE,
    name                    VARCHAR(100)    NOT NULL,
    school_year             VARCHAR(16)     NOT NULL,
    intro_programming       VARCHAR(16)     NOT NULL
                            CHECK (intro_programming IN ('took_it', 'equivalent', 'neither')),
    skill_programming       SMALLINT        NOT NULL
                            CHECK (skill_programming BETWEEN 1 AND 5),
    skill_data_stats        SMALLINT        NOT NULL
                            CHECK (skill_data_stats BETWEEN 1 AND 5),
    skill_frontend_design   SMALLINT        NOT NULL
                            CHECK (skill_frontend_design BETWEEN 1 AND 5),
    skill_business_pitch    SMALLINT        NOT NULL
                            CHECK (skill_business_pitch BETWEEN 1 AND 5),
    working_style           TEXT            NOT NULL,
    interests               TEXT            NOT NULL,
    semester_goal           TEXT            NOT NULL,
    submitted_at            TIMESTAMPTZ     NOT NULL
);

CREATE TABLE tool (
    tool_id     SERIAL          PRIMARY KEY,
    name        VARCHAR(32)     NOT NULL UNIQUE
);

CREATE TABLE availability_slot (
    slot_id     SERIAL          PRIMARY KEY,
    name        VARCHAR(32)     NOT NULL UNIQUE
);

CREATE TABLE student_tool (
    student_id  INT             NOT NULL REFERENCES student (student_id),
    tool_id     INT             NOT NULL REFERENCES tool (tool_id),
    PRIMARY KEY (student_id, tool_id)
);

CREATE TABLE student_availability (
    student_id  INT             NOT NULL REFERENCES student (student_id),
    slot_id     INT             NOT NULL REFERENCES availability_slot (slot_id),
    PRIMARY KEY (student_id, slot_id)
);
