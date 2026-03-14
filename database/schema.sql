-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.admissions_events (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  school_id uuid,
  document_id uuid,
  event_type USER-DEFINED NOT NULL,
  category text CHECK (category = ANY (ARRAY['catchment'::text, 'open'::text, 'pupil_premium'::text])),
  score numeric,
  distance_miles numeric,
  data_trust_score numeric,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT admissions_events_pkey PRIMARY KEY (id),
  CONSTRAINT admissions_events_school_id_fkey FOREIGN KEY (school_id) REFERENCES public.schools(id),
  CONSTRAINT admissions_events_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id)
);
CREATE TABLE public.agents (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  status text DEFAULT 'idle'::text,
  config jsonb DEFAULT '{}'::jsonb,
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT agents_pkey PRIMARY KEY (id)
);
CREATE TABLE public.documents (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  source_id uuid,
  document_type USER-DEFINED NOT NULL,
  raw_content text NOT NULL,
  metadata jsonb DEFAULT '{}'::jsonb,
  crawled_at timestamp with time zone DEFAULT now(),
  CONSTRAINT documents_pkey PRIMARY KEY (id),
  CONSTRAINT documents_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(id)
);
CREATE TABLE public.official_data (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  school_id uuid,
  cutoff_score numeric,
  cutoff_distance numeric,
  admission_year integer,
  source_url text,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT official_data_pkey PRIMARY KEY (id),
  CONSTRAINT official_data_school_id_fkey FOREIGN KEY (school_id) REFERENCES public.schools(id)
);
CREATE TABLE public.parent_reports (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  school_id uuid,
  reported_rank integer,
  distance_km numeric,
  report_date date,
  verified boolean DEFAULT false,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT parent_reports_pkey PRIMARY KEY (id),
  CONSTRAINT parent_reports_school_id_fkey FOREIGN KEY (school_id) REFERENCES public.schools(id)
);
CREATE TABLE public.school_benchmarks (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  school_id uuid,
  academic_year integer NOT NULL,
  selective_pass_mark numeric,
  last_catchment_score_offered numeric,
  last_open_score_offered numeric,
  top_1_percent_catchment_score numeric,
  top_1_percent_open_score numeric,
  is_official_data boolean DEFAULT false,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT school_benchmarks_pkey PRIMARY KEY (id),
  CONSTRAINT school_benchmarks_school_id_fkey FOREIGN KEY (school_id) REFERENCES public.schools(id)
);
CREATE TABLE public.schools (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  name text NOT NULL,
  borough text,
  school_type text,
  published_admission_number integer,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT schools_pkey PRIMARY KEY (id)
);
CREATE TABLE public.sources (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  school_id uuid,
  source_name text NOT NULL,
  source_type USER-DEFINED NOT NULL,
  platform USER-DEFINED NOT NULL,
  access_method USER-DEFINED NOT NULL,
  url text NOT NULL,
  active boolean DEFAULT true,
  trust_base_score numeric DEFAULT 0.50,
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT sources_pkey PRIMARY KEY (id),
  CONSTRAINT sources_school_id_fkey FOREIGN KEY (school_id) REFERENCES public.schools(id)
);
CREATE TABLE public.waiting_list_updates (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  school_id uuid,
  rank_position integer,
  update_date date,
  source text,
  confidence_score numeric,
  notes text,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT waiting_list_updates_pkey PRIMARY KEY (id),
  CONSTRAINT waiting_list_updates_school_id_fkey FOREIGN KEY (school_id) REFERENCES public.schools(id)
);