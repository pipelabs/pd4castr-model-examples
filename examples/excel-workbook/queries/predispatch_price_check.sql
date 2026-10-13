SELECT file_generate_time
FROM pdrloader.pdr_report_audit
WHERE
    file_generate_time > NOW() - INTERVAL '24 hours'
    AND file_id = 'PREDISPATCHIS'
ORDER BY file_generate_time DESC
LIMIT 1
