-- Migration: Register Structogram Builder as System Feature #26
-- Category: interactive_tools (alongside whiteboard_engine)

INSERT INTO support_systems.system_features (feature_code, feature_name, category, icon, description)
VALUES (
    'structogram_builder',
    'Struktogramm-Builder',
    'interactive_tools',
    'structogram',
    'Interaktiver Nassi-Shneiderman Editor für Programmablaufpläne'
)
ON CONFLICT DO NOTHING;
