-- ============================================================================
-- Seed Data: Agent Intelligence Domain Taxonomy
-- Description: Initial knowledge domains for agent learning system
-- Source: 089_consolidated.sql (094_agent_global_knowledge_part1.sql)
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (Seed Data)
-- ============================================================================

-- ============================================================================
-- Domain Taxonomy - Initial Knowledge Domains
-- ============================================================================
-- Seeds the domain_taxonomy table with 8 knowledge domains
-- Each domain represents a major subject area for cross-course agent learning
--
-- Domains:
--   1. networking - Computer networking, protocols, topologies
--   2. programming - Programming languages, algorithms, design patterns
--   3. databases - SQL, NoSQL, data modeling
--   4. web_dev - Frontend, backend, APIs
--   5. devops - CI/CD, containers, cloud infrastructure
--   6. security - IT security, encryption, authentication
--   7. math - Mathematics (algebra, analysis, statistics)
--   8. business - Business/Management (accounting, controlling, marketing)
--
-- Topics: Pre-defined topics for each domain (stored as JSON array)

INSERT INTO agent_intelligence.domain_taxonomy (domain_code, domain_name, domain_level, description, topics) VALUES
('networking', 'Netzwerktechnik', 1, 'Computernetzwerke, Protokolle, Topologien', '["TCP/IP", "OSI-Modell", "Routing", "Switching", "Firewall"]'),
('programming', 'Programmierung', 1, 'Programmiersprachen, Algorithmen, Design Patterns', '["Python", "JavaScript", "OOP", "Funktional", "Datenstrukturen"]'),
('databases', 'Datenbanken', 1, 'SQL, NoSQL, Datenmodellierung', '["PostgreSQL", "MongoDB", "Normalisierung", "Indexierung", "Transaktionen"]'),
('web_dev', 'Webentwicklung', 1, 'Frontend, Backend, APIs', '["Vue.js", "React", "REST", "GraphQL", "Authentication"]'),
('devops', 'DevOps', 1, 'CI/CD, Container, Cloud', '["Docker", "Kubernetes", "Git", "Jenkins", "AWS"]'),
('security', 'IT-Sicherheit', 1, 'Verschlüsselung, Authentifizierung, Bedrohungen', '["OWASP", "JWT", "SSL/TLS", "Penetration Testing", "Firewalls"]'),
('math', 'Mathematik', 1, 'Algebra, Analysis, Statistik', '["Lineare Algebra", "Calculus", "Wahrscheinlichkeit", "Statistik"]'),
('business', 'Betriebswirtschaft', 1, 'BWL, Controlling, Marketing', '["Buchhaltung", "Kostenrechnung", "Marketing", "Projektmanagement"]')
ON CONFLICT (domain_code) DO NOTHING;

-- ============================================================================
-- Verification
-- ============================================================================

SELECT COUNT(*) as total_agent_domains FROM agent_intelligence.domain_taxonomy;
