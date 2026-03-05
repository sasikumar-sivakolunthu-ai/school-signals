-- School Signals Database Schema

-- Table: schools
CREATE TABLE schools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    borough TEXT,
    school_type TEXT,
    published_admission_number INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table: waiting_list_updates
CREATE TABLE waiting_list_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID REFERENCES schools(id),
    rank_position INTEGER,
    update_date DATE,
    source TEXT,
    confidence_score NUMERIC,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table: parent_reports
CREATE TABLE parent_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID REFERENCES schools(id),
    reported_rank INTEGER,
    distance_km NUMERIC,
    report_date DATE,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table: official_data
CREATE TABLE official_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID REFERENCES schools(id),
    cutoff_score NUMERIC,
    cutoff_distance NUMERIC,
    admission_year INTEGER,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
