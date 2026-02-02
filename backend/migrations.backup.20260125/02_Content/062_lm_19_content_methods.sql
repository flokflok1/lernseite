-- ============================================================================
-- Migration: 062_lm_19_content_methods.sql
-- Version: 1.0.0
-- Description: View für 12 Content-Lernmethoden
-- Author: LernsystemX Migration System
-- Date: 2026-01-02 (Cleaned 2026-01-06)
-- ============================================================================

-- ============================================================================
-- VIEW: v_content_learning_methods
-- Description: Active Content-Lernmethoden (12 methods: LM00-LM11)
-- ============================================================================
CREATE OR REPLACE VIEW v_content_learning_methods AS
SELECT
    type_id,
    method_type,
    name,
    group_code,
    description,
    ki_usage,
    tier,
    icon
FROM learning_methods.learning_method_types
WHERE active = TRUE
  AND method_type IN (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
ORDER BY method_type;

COMMENT ON VIEW v_content_learning_methods IS
'Aktive Content-Lernmethoden (12 Methoden: LM00-LM11).
Gruppe A (Erklärend): LM00-LM04 (5 Methoden)
Gruppe B (Praxis): LM05-LM08 (4 Methoden)
Gruppe C (Prüfung): LM09-LM11 (3 Methoden)
Für neue Lektionen nur diese LMs verwenden.
System-Features: support_systems.system_features (25 Features)';

-- NOTE: v_system_features view removed - System Features are now in
-- support_systems.system_features table (see 074_system_features.sql)

-- ============================================================================
-- End of Migration: 062_lm_19_content_methods.sql
-- ============================================================================
