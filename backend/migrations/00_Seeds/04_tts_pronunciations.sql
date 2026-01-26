-- ============================================================================
-- Seed Data: TTS Pronunciation System
-- Description: Initial German TTS pronunciation records for business, technical, and mathematical terms
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (Seed Data - runs AFTER all structural migrations)
-- ============================================================================

-- Insert initial German pronunciation rules
INSERT INTO translations.tts_pronunciations (original_word, phonetic_spelling, language, category, word_type, source, verified) VALUES
-- Business terms (compound)
('Listeneinkaufspreis', 'Listen Einkaufs Preis', 'de', 'business', 'compound', 'manual', true),
('Zieleinkaufspreis', 'Ziel Einkaufs Preis', 'de', 'business', 'compound', 'manual', true),
('Bareinkaufspreis', 'Bar Einkaufs Preis', 'de', 'business', 'compound', 'manual', true),
('Einstandspreis', 'Einstands Preis', 'de', 'business', 'compound', 'manual', true),
('Verkaufspreis', 'Verkaufs Preis', 'de', 'business', 'compound', 'manual', true),
('Selbstkostenpreis', 'Selbstkosten Preis', 'de', 'business', 'compound', 'manual', true),
('Bezugskalkulation', 'Bezugs Kalkullazion', 'de', 'business', 'compound', 'manual', true),
('Handelskalkulation', 'Handels Kalkullazion', 'de', 'business', 'compound', 'manual', true),
('Verkaufskalkulation', 'Verkaufs Kalkullazion', 'de', 'business', 'compound', 'manual', true),
('Bezugskosten', 'Bezugs Kosten', 'de', 'business', 'compound', 'manual', true),
('Handlungskosten', 'Handlungs Kosten', 'de', 'business', 'compound', 'manual', true),
('Lieferantenrabatt', 'Lieferannten Rabbatt', 'de', 'business', 'compound', 'manual', true),
('Lieferantenskonto', 'Lieferannten Skonnto', 'de', 'business', 'compound', 'manual', true),
('Kundenrabatt', 'Kunden Rabbatt', 'de', 'business', 'compound', 'manual', true),
('Kundenskonto', 'Kunden Skonnto', 'de', 'business', 'compound', 'manual', true),

-- Business terms (single words)
('Rabatt', 'Rabbatt', 'de', 'business', 'noun', 'manual', true),
('Skonto', 'Skonnto', 'de', 'business', 'noun', 'manual', true),
('Kalkulation', 'Kalkullazion', 'de', 'business', 'noun', 'manual', true),
('Lieferant', 'Lieferannt', 'de', 'business', 'noun', 'manual', true),
('Lieferanten', 'Lieferannten', 'de', 'business', 'noun', 'manual', true),
('Provision', 'Proviesion', 'de', 'business', 'noun', 'manual', true),
('Marge', 'Marsche', 'de', 'business', 'noun', 'manual', true),
('Gewinnmarge', 'Gewinn Marsche', 'de', 'business', 'compound', 'manual', true),

-- Abbreviations (business)
('LEP', 'Listen Einkaufs Preis', 'de', 'business', 'abbreviation', 'manual', true),
('ZEP', 'Ziel Einkaufs Preis', 'de', 'business', 'abbreviation', 'manual', true),
('BEP', 'Bar Einkaufs Preis', 'de', 'business', 'abbreviation', 'manual', true),
('VKP', 'Verkaufs Preis', 'de', 'business', 'abbreviation', 'manual', true),
('SKP', 'Selbstkosten Preis', 'de', 'business', 'abbreviation', 'manual', true),
('MwSt', 'Mehrwertsteuer', 'de', 'business', 'abbreviation', 'manual', true),
('USt', 'Umsatzsteuer', 'de', 'business', 'abbreviation', 'manual', true),

-- Abbreviations (general)
('inkl', 'inklusive', 'de', 'general', 'abbreviation', 'manual', true),
('exkl', 'exklusive', 'de', 'general', 'abbreviation', 'manual', true),
('zzgl', 'zuzüglich', 'de', 'general', 'abbreviation', 'manual', true),
('abzgl', 'abzüglich', 'de', 'general', 'abbreviation', 'manual', true),
('Stk', 'Stück', 'de', 'general', 'abbreviation', 'manual', true),
('ca', 'zirka', 'de', 'general', 'abbreviation', 'manual', true),
('bzw', 'beziehungsweise', 'de', 'general', 'abbreviation', 'manual', true),
('z.B.', 'zum Beispiel', 'de', 'general', 'abbreviation', 'manual', true),
('d.h.', 'das heißt', 'de', 'general', 'abbreviation', 'manual', true),
('usw', 'und so weiter', 'de', 'general', 'abbreviation', 'manual', true),

-- IT terms
('Server', 'Sörver', 'de', 'technical', 'noun', 'manual', true),
('Router', 'Ruuter', 'de', 'technical', 'noun', 'manual', true),
('Switch', 'Suitsch', 'de', 'technical', 'noun', 'manual', true),
('Firewall', 'Feierwall', 'de', 'technical', 'noun', 'manual', true),
('Cloud', 'Klaud', 'de', 'technical', 'noun', 'manual', true),
('Software', 'Softweär', 'de', 'technical', 'noun', 'manual', true),
('Hardware', 'Hardweär', 'de', 'technical', 'noun', 'manual', true),
('Download', 'Daunlohd', 'de', 'technical', 'noun', 'manual', true),
('Upload', 'Aplohd', 'de', 'technical', 'noun', 'manual', true),
('Update', 'Apdäit', 'de', 'technical', 'noun', 'manual', true),
('Backup', 'Bäckapp', 'de', 'technical', 'noun', 'manual', true),
('Interface', 'Interfäis', 'de', 'technical', 'noun', 'manual', true),
('Cache', 'Käsch', 'de', 'technical', 'noun', 'manual', true),
('Browser', 'Brauser', 'de', 'technical', 'noun', 'manual', true),

-- Mathematical terms
('Prozent', 'Prozent', 'de', 'math', 'noun', 'manual', true),
('Dezimal', 'Deziemahl', 'de', 'math', 'noun', 'manual', true),
('Bruch', 'Bruch', 'de', 'math', 'noun', 'manual', true),
('Quotient', 'Kozient', 'de', 'math', 'noun', 'manual', true),
('Dividend', 'Diviedent', 'de', 'math', 'noun', 'manual', true),
('Divisor', 'Diviesor', 'de', 'math', 'noun', 'manual', true)

ON CONFLICT (original_word, language) DO UPDATE SET
    phonetic_spelling = EXCLUDED.phonetic_spelling,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================================
-- Verification
-- ============================================================================

SELECT COUNT(*) as total_pronunciations FROM translations.tts_pronunciations WHERE source = 'manual' AND verified = true;
SELECT COUNT(DISTINCT category) as categories FROM translations.tts_pronunciations WHERE source = 'manual';
