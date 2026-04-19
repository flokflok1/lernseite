-- ============================================================================
-- Migration: 143_ap2_item_sub_area.sql
-- Description: Sub-Area Tagging für AP2 Learning Items.
--              Ermöglicht feingranulare Mastery-Heatmaps pro Kern-Modul
--              (z.B. innerhalb "IPv6 Deep": basics, notation, comparison,
--              eui64, slaac, prefix, ndp, netzplan, transition, security).
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-19
-- ============================================================================

-- Sub-Area: feingranulare Topic-Zone innerhalb eines Moduls
ALTER TABLE assessments.ap2_learning_items
    ADD COLUMN IF NOT EXISTS sub_area VARCHAR(64);

-- Optional: freie Tags für Cross-Cutting (z.B. ['klausur2024', 'rechenweg'])
ALTER TABLE assessments.ap2_learning_items
    ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT ARRAY[]::TEXT[];

-- Index für schnelle Sub-Area-Aggregationen im Dashboard
CREATE INDEX IF NOT EXISTS idx_ap2_items_sub_area
    ON assessments.ap2_learning_items(sub_area)
    WHERE sub_area IS NOT NULL;

-- Display-Reihenfolge + Farbe für die Heatmap-UI (frei konfigurierbar pro Modul)
CREATE TABLE IF NOT EXISTS assessments.ap2_module_sub_area_meta (
    module_id UUID NOT NULL REFERENCES assessments.ap2_modules(module_id) ON DELETE CASCADE,
    sub_area VARCHAR(64) NOT NULL,
    label_de VARCHAR(128) NOT NULL,
    label_en VARCHAR(128),
    sort_order INTEGER NOT NULL DEFAULT 0,
    icon VARCHAR(8),            -- Emoji für UI (📐 / 🔐 / ...)
    color VARCHAR(16),          -- Tailwind-Farbklasse oder HEX
    description TEXT,           -- Kurzbeschreibung was diese Sub-Area abdeckt
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (module_id, sub_area)
);

COMMENT ON TABLE assessments.ap2_module_sub_area_meta IS
'Darstellung-Metadaten für Sub-Areas pro Modul. Sort-Reihenfolge, Icon, Label
für die Heatmap im Modul-Dashboard.';

COMMIT;
