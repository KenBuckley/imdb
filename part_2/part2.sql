WITH daily_events AS (
    SELECT
        event_date,
        num_entries_per_day,
        total_bytes_processed,
        average_processing_time,
        file_list as files,
        SUM(total_bytes_processed) OVER (ORDER BY event_date) AS total_bytes_cumulative,
        all_tags,
        min_time_ms,
        min_event_id  -- Add this to uniquely identify the slowest entry
    FROM (
        SELECT
            date_trunc('day', event_time) AS event_date,
            COUNT(*) AS num_entries_per_day,
            SUM(bytes_processed) AS total_bytes_processed,
            AVG(processing_time_ms) as average_processing_time,
            array_agg(DISTINCT file_name) AS file_list,
            array_agg(DISTINCT tag) FILTER (WHERE tag IS NOT NULL) AS all_tags,
            MIN(processing_time_ms) FILTER (WHERE metadata->>'source' = 'HTSGET') as min_time_ms,
            -- extra:get the event_id of the row with the min(processing_time_ms).
            (array_agg(event_id ORDER BY processing_time_ms)
             FILTER (WHERE metadata->>'source' = 'HTSGET'))[1] as min_event_id
        FROM file_processing_events
        LEFT JOIN LATERAL unnest(COALESCE(tags, ARRAY[]::text[])) AS tag ON true
        WHERE metadata->>'source' = 'HTSGET'
        AND metadata ? 'weights'   --todo check if required
        AND jsonb_typeof(metadata->'weights') = 'array'  --required or will get error
        GROUP BY event_date
    ) as day_stats
    ORDER BY event_date
),
-- Pre-calculate weights for the slowest entries
slowest_entries_weights AS (
    SELECT
        event_id,
        date_trunc('day', event_time) as event_date,
        (SELECT AVG(weight::numeric)
         FROM jsonb_array_elements_text(metadata->'weights') AS weight) AS avg_weight,
        (SELECT SUM(weight::numeric)
         FROM jsonb_array_elements_text(metadata->'weights') AS weight) AS sum_weight
    FROM file_processing_events
    WHERE metadata->>'source' = 'HTSGET'
    AND metadata ? 'weights'
    AND jsonb_typeof(metadata->'weights') = 'array' -- neccessary
)
SELECT
    de.event_date,
    de.num_entries_per_day,
    de.total_bytes_processed,
    de.average_processing_time,
    de.files,
    de.total_bytes_cumulative,
    de.all_tags,
    sew.avg_weight as average_weight_from_slowest_entry,
    sew.sum_weight as total_weight_from_slowest_entry
FROM daily_events de
JOIN slowest_entries_weights sew ON de.min_event_id = sew.event_id
ORDER BY de.event_date;

