select * from harvard.artifact_metadata;
select * from harvard.artifact_media;
select * from harvard.artifact_colors;

use harvard;

# Metadata
-- 1.Artifacts from 11th century (Byzantine)
SELECT * FROM artifact_metadata WHERE century LIKE '%11th%' AND culture='Byzantine';
-- 2.Unique cultures
SELECT DISTINCT culture FROM artifact_metadata;
-- 3.Artifacts from Archaic Period
SELECT * FROM artifact_metadata WHERE period='Archaic';
-- 4.Artifact titles ordered by accession year (desc)
SELECT title, accessionyear FROM artifact_metadata ORDER BY accessionyear DESC;
-- 5.Artifacts per department
SELECT department, COUNT(*) AS total FROM artifact_metadata GROUP BY department;

# Media
-- 6.Artifacts with >1 image 
SELECT * FROM artifact_media WHERE imagecount > 1;
-- 7.Average rank of artifacts
SELECT AVG(rankk) AS avg_rank FROM artifact_media;
-- 8.Artifacts with colorcount > mediacount 
SELECT * FROM artifact_media WHERE colorcount > mediacount;
-- 9.Artifacts created between 1500 and 1600 
SELECT * FROM artifact_media WHERE datebegin >= 1500 AND dateend <= 1600;
-- 10.Artifacts with no media 
SELECT * FROM artifact_media WHERE mediacount=0;

# Colors
-- 11.Distinct hues 
SELECT DISTINCT hue FROM artifact_colors;
-- 12.Top 5 most used colors
SELECT color, COUNT(*) AS freq FROM artifact_colors GROUP BY color ORDER BY freq DESC LIMIT 5;
-- 13.Average % coverage per hue
SELECT hue, AVG(percent) AS avg_percent FROM artifact_colors GROUP BY hue;
-- 14.Colors for artifact ID: "DYNAMIC", 
# handled separately
-- 15.Total number of color entries
SELECT COUNT(*) AS total_colors FROM artifact_colors;

# Join Queries
-- 16.Artifact titles & hues (Byzantine culture)
SELECT m.title, c.hue FROM artifact_metadata m JOIN artifact_colors c ON m.id=c.objectid WHERE m.culture='Byzantine';
-- 17.Each artifact title with hues
SELECT m.title, c.hue FROM artifact_metadata m JOIN artifact_colors c ON m.id=c.objectid;
-- 18.Titles, cultures, ranks where period not null
SELECT m.title, m.culture, media.rankk FROM artifact_metadata m JOIN artifact_media media ON m.id=media.objectid WHERE m.period IS NOT NULL;
-- 19.Top 10 ranked artifacts with hue Grey
SELECT m.title, media.rankk FROM artifact_metadata m JOIN artifact_media media ON m.id=media.objectid JOIN artifact_colors c ON m.id=c.objectid WHERE c.hue='Grey' ORDER BY media.rankk LIMIT 10;
-- 20.Artifacts per classification & avg media count
SELECT m.classification, COUNT(*) AS total, AVG(media.mediacount) AS avg_media FROM artifact_metadata m JOIN artifact_media media ON m.id=media.objectid GROUP BY m.classification;

# Innovative 5
-- 21.Most common mediums
SELECT medium, COUNT(*) AS freq FROM artifact_metadata WHERE medium IS NOT NULL GROUP BY medium ORDER BY freq DESC LIMIT 5;
-- 22.Departments with artifacts spanning >500 years
SELECT department, MIN(datebegin) AS earliest, MAX(dateend) AS latest, (MAX(dateend) - MIN(datebegin)) AS span_years FROM artifact_media m JOIN artifact_metadata meta ON m.objectid = meta.id WHERE m.datebegin IS NOT NULL AND m.dateend IS NOT NULL GROUP BY department HAVING span_years > 500;
-- 23.Top 10 longest artifact titles
SELECT id, title, LENGTH(title) AS title_length FROM artifact_metadata WHERE title IS NOT NULL ORDER BY title_length DESC LIMIT 10;
-- 24.Average number of colors per artifact
SELECT AVG(color_count) AS avg_colors_per_artifact FROM (SELECT objectid, COUNT(*) AS color_count FROM artifact_colors GROUP BY objectid) sub;
-- 25.Artifacts with missing title or culture
SELECT * FROM artifact_metadata WHERE title IS NULL OR culture IS NULL;
}