-- Seed forum sources for the crawler.
-- Run this in the Supabase SQL editor (requires service role / admin access).
--
-- Confirmed enum values (probed 2026-03-15):
--   source_type_enum : official | forum | news
--   platform_enum    : mumsnet | reddit | elevenplusexams | school_site
--   access_method_enum: manual | api | rss | webscrape
--   document_type_enum: post
--
-- The crawler picks up all active sources with access_method='webscrape'.

INSERT INTO sources (school_id, source_name, source_type, platform, access_method, url, active, trust_base_score)
VALUES
  (
    NULL,
    'Mumsnet - Secondary Education (waiting lists)',
    'forum',
    'mumsnet',
    'webscrape',
    'https://www.mumsnet.com/Talk/secondary_education?keywords=waiting+list+grammar',
    true,
    0.55
  ),
  (
    NULL,
    'Reddit - r/GrammarSchools',
    'forum',
    'reddit',
    'webscrape',
    'https://www.reddit.com/r/GrammarSchools/search/?q=waiting+list&sort=new',
    true,
    0.50
  ),
  (
    NULL,
    'Elevenplusexams - Waiting List Discussion',
    'forum',
    'elevenplusexams',
    'webscrape',
    'https://www.elevenplusexams.co.uk/forum/11plus/viewforum.php?f=3',
    true,
    0.60
  )
ON CONFLICT DO NOTHING;
