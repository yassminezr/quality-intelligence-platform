-- ============================================================
-- Corrective Action Monitoring
-- Inspection de la source analytique
-- ============================================================


-- 1. Colonnes disponibles dans le mart
SELECT
    ordinal_position,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'analytics'
  AND table_name = 'mart_corrective_actions'
ORDER BY ordinal_position;


-- 2. Aperçu des données
SELECT *
FROM analytics.mart_corrective_actions
LIMIT 10;