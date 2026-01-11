# CLAUDE CODE CLI - COMPLETE BACKEND MIGRATION
# LernSystemX: Enterprise-Grade Social Learning Platform
# Full Compliance: DSA + NetzDG + GDPR + ISO 27001 + Child Safety + DRM

---

## 🎯 EXECUTIVE SUMMARY

**Projekt:** LernSystemX - Instagram für Lernen (Social Learning Platform)  
**Ziel:** Migration von chaotischer Struktur (766 Verzeichnisse, 1592 Files) zu Enterprise Architecture  
**Compliance:** 10+ internationale Standards  
**Features:** Feature Flags für progressive Aktivierung  
**Timeline:** Phased Rollout (Beta → 25% → 100%)

---

## 📚 COMPLIANCE REQUIREMENTS - VOLLSTÄNDIG

### 🇪🇺 DSGVO/GDPR (Datenschutz-Grundverordnung)

**Status:** 🔴 PFLICHT für EU-Kunden  
**Bußgeld:** Bis zu 20 Mio. EUR oder 4% Jahresumsatz  
**Gültig seit:** 25. Mai 2018

#### Artikel-Übersicht:

**Art. 5 - Grundsätze (Principles)**
- Rechtmäßigkeit, Verarbeitung nach Treu und Glauben, Transparenz
- Zweckbindung (Purpose Limitation)
- Datenminimierung (Data Minimization) ⭐
- Richtigkeit (Accuracy)
- Speicherbegrenzung (Storage Limitation)
- Integrität und Vertraulichkeit (Security)

**Art. 6 - Rechtsgrundlagen (Legal Basis)**
- Einwilligung (Consent)
- Vertragserfüllung (Contract)
- Rechtliche Verpflichtung (Legal Obligation)
- Berechtigtes Interesse (Legitimate Interest)

**Art. 7 - Einwilligung (Consent Management)** ⭐
- Opt-in (nicht Opt-out)
- Granulare Einwilligung (pro Zweck)
- Leicht widerrufbar
- Dokumentationspflicht
- Keine Kopplung an Vertrag

**Art. 8 - Kinder (Children Protection)**
- Unter 16 Jahren: Einwilligung der Eltern
- Deutschland: Unter 16 Jahren
- USA (COPPA): Unter 13 Jahren

**Art. 15-22 - Betroffenenrechte (Data Subject Rights)** ⭐
- **Art. 15:** Recht auf Auskunft (Right of Access) → Datenexport
- **Art. 16:** Recht auf Berichtigung (Rectification)
- **Art. 17:** Recht auf Löschung (Right to Erasure / "Right to be Forgotten") ⭐
- **Art. 18:** Recht auf Einschränkung (Restriction)
- **Art. 20:** Recht auf Datenübertragbarkeit (Data Portability) ⭐
- **Art. 21:** Widerspruchsrecht (Right to Object)
- **Art. 22:** Automatisierte Entscheidungen (Automated Decision-Making)

**Art. 25 - Datenschutz durch Technikgestaltung (Privacy by Design)** ⭐
- Privacy by Default
- Pseudonymisierung
- Anonymisierung
- Datenschutzfreundliche Voreinstellungen

**Art. 30 - Verzeichnis von Verarbeitungstätigkeiten (Processing Records)** ⭐
- Vollständiges Verzeichnis aller Datenverarbeitungen
- Zweck, Kategorien, Empfänger, Löschfristen
- Technische und organisatorische Maßnahmen

**Art. 33-34 - Meldung von Datenschutzverletzungen (Breach Notification)** ⭐
- 72 Stunden Meldefrist an Aufsichtsbehörde
- Unverzügliche Benachrichtigung Betroffener bei hohem Risiko
- Dokumentationspflicht

**Art. 35 - Datenschutz-Folgenabschätzung (DPIA - Data Protection Impact Assessment)** ⭐
- Pflicht bei hohem Risiko
- Beschreibung der Verarbeitung
- Bewertung der Notwendigkeit
- Bewertung der Risiken
- Abhilfemaßnahmen

**Art. 37 - Datenschutzbeauftragter (Data Protection Officer - DPO)**
- Pflicht ab 20 Mitarbeiter (Deutschland)
- Unabhängig
- Berichtspflicht an Geschäftsführung

**Art. 44-49 - Internationale Übermittlungen (International Transfers)**
- Angemessenheitsbeschluss (Adequacy Decision)
- Standardvertragsklauseln (Standard Contractual Clauses - SCC)
- Binding Corporate Rules (BCR)

#### Implementation Requirements:

```
/app/compliance/gdpr/
├── /principles              # Art. 5 - Grundsätze
│   ├── lawfulness.py            # Rechtmäßigkeit
│   ├── purpose_limitation.py    # Zweckbindung
│   ├── data_minimization.py     # ⭐ Datenminimierung
│   ├── accuracy.py              # Richtigkeit
│   ├── storage_limitation.py    # Speicherbegrenzung
│   └── integrity_confidentiality.py # Sicherheit
│
├── /legal_basis             # Art. 6 - Rechtsgrundlagen
│   ├── consent.py               # Einwilligung
│   ├── contract.py              # Vertragserfüllung
│   ├── legal_obligation.py      # Rechtliche Verpflichtung
│   └── legitimate_interest.py   # Berechtigtes Interesse
│
├── /consent                 # ⭐ Art. 7 - Einwilligungsverwaltung
│   ├── consent_manager.py       # Hauptverwaltung
│   ├── consent_storage.py       # Dokumentation
│   ├── withdrawal.py            # Widerruf
│   ├── granular_consent.py      # Zweckspezifisch
│   └── consent_ui.py            # UI-Komponenten
│
├── /children                # Art. 8 - Kinderschutz
│   ├── age_verification.py
│   └── parental_consent.py
│
├── /data_subject_rights     # ⭐ Art. 15-22 - Betroffenenrechte
│   ├── access.py                # Art. 15 - Auskunftsrecht
│   ├── rectification.py         # Art. 16 - Berichtigung
│   ├── erasure.py               # ⭐ Art. 17 - Löschung
│   ├── restriction.py           # Art. 18 - Einschränkung
│   ├── portability.py           # ⭐ Art. 20 - Datenübertragbarkeit
│   ├── objection.py             # Art. 21 - Widerspruch
│   └── automated_decision.py    # Art. 22 - Automatisierung
│
├── /privacy_by_design       # ⭐ Art. 25 - Privacy by Design
│   ├── default_settings.py
│   ├── pseudonymization.py
│   ├── anonymization.py
│   └── minimization.py
│
├── /processing_records      # Art. 30 - Verarbeitungsverzeichnis
│   ├── registry.py
│   ├── documentation.py
│   └── generator.py
│
├── /breach_management       # ⭐ Art. 33-34 - Datenpannen
│   ├── breach_detector.py       # Automatische Erkennung
│   ├── breach_notification.py   # 72h Meldung
│   ├── authority_notification.py # Aufsichtsbehörde
│   ├── user_notification.py     # Betroffenen-Benachrichtigung
│   └── breach_log.py            # Dokumentation
│
├── /dpia                    # Art. 35 - Datenschutz-Folgenabschätzung
│   ├── dpia_manager.py          # ⭐ DPIA Workflow
│   ├── risk_assessment.py       # Risikobewertung
│   ├── mitigation.py            # Abhilfemaßnahmen
│   └── documentation.py         # DPIA-Dokumentation
│
├── /transfers               # Art. 44-49 - Internationale Übermittlungen
│   ├── adequacy_decision.py     # EU-Angemessenheitsbeschluss
│   ├── standard_clauses.py      # SCC
│   └── bcr.py                   # Binding Corporate Rules
│
├── /dpo                     # Art. 37 - Datenschutzbeauftragter
│   ├── dpo_tools.py
│   ├── monitoring.py
│   └── reporting.py
│
└── /social_data             # ⭐ Social Media spezifisch
    ├── post_deletion.py         # Alle Posts löschen
    ├── comment_deletion.py      # Alle Kommentare löschen
    ├── like_deletion.py         # Alle Likes löschen
    ├── follower_deletion.py     # Social Graph löschen
    ├── message_deletion.py      # Nachrichten löschen
    └── social_export.py         # Social Data exportieren
```

---

### 🇪🇺 DSA (Digital Services Act)

**Status:** 🔴 PFLICHT ab 17. Februar 2024  
**Bußgeld:** Bis zu 6% Jahresumsatz (VLOP) oder 10 Mio. EUR  
**Gilt für:** ALLE Online-Plattformen mit User-Generated Content in EU

#### Kategorien:

**1. Intermediary Service Provider** (< 45M User/Monat)
- Basic Content Moderation
- Reporting Mechanism
- Transparency
- Terms of Service

**2. Very Large Online Platform (VLOP)** (≥ 45M User/Monat)
- Alle von (1) +
- Risk Assessment (jährlich)
- Independent Audit (jährlich)
- Researcher Data Access
- Ad Library
- Crisis Response Mechanism

#### DSA Artikel-Übersicht:

**Art. 13 - Terms & Conditions**
- Klare, verständliche Nutzungsbedingungen
- Information über Content Moderation
- Beschwerdemechanismen

**Art. 14 - Notice & Action Mechanism** ⭐
- Nutzer können illegale Inhalte melden
- Einfaches Meldeformular
- Begründung erforderlich
- Bestätigung an Melder

**Art. 15 - Statement of Reasons** ⭐
- Bei Content-Entfernung: Begründung
- Rechtsgrundlage angeben
- Beschwerdemöglichkeit
- Sprache des Nutzers

**Art. 16 - Internal Complaint System**
- Internes Beschwerdeverfahren
- 6 Monate Bearbeitungszeit
- Transparente Entscheidungen

**Art. 17 - Out-of-Court Dispute Settlement**
- Zertifizierte Streitbeilegungsstellen
- Nutzer kann sich beschweren
- Kostenfrei für Nutzer

**Art. 24 - Recommender Systems Transparency** ⭐ (VLOP)
- Hauptparameter offenlegen
- Wie funktioniert der Algorithmus?
- Nutzer-Kontrolle ermöglichen
- Mindestens eine nicht-algorithmische Option

**Art. 33 - Risk Assessment** (VLOP)
- Jährliche Risikobewertung
- Systemische Risiken identifizieren
- Minderungsmaßnahmen

**Art. 34 - Independent Audit** (VLOP)
- Jährlicher unabhängiger Audit
- Compliance prüfen

**Art. 35 - Crisis Response** (VLOP)
- Bei Krisensituationen (z.B. Terroranschlag)
- Schnelle Reaktion
- Zusammenarbeit mit Behörden

#### Implementation Requirements:

```
/app/compliance/dsa/
├── /content_moderation      # ⭐ Art. 14-16 - Content Moderation
│   ├── moderation_engine.py     # Haupt-Engine
│   ├── ai_moderator.py          # AI Pre-screening
│   ├── human_review.py          # Menschliche Review-Queue
│   ├── priority_system.py       # Critical/High/Medium/Low
│   ├── automated_actions.py     # Auto-hide/delete
│   ├── appeal_process.py        # Art. 16 - Beschwerdeverfahren
│   └── review_decisions.py      # Entscheidungstracking
│
├── /ai_detection            # ⭐ AI Content Analysis
│   ├── text_analyzer.py         # Toxicity, Hate Speech, NSFW
│   ├── image_analyzer.py        # NSFW, Violence
│   ├── video_analyzer.py        # Video Content
│   ├── spam_detector.py         # Spam Detection
│   ├── bot_detector.py          # Bot/Fake Accounts
│   ├── deepfake_detector.py     # Deepfake Detection
│   └── misinformation.py        # Fact-checking Integration
│
├── /reporting               # ⭐ Art. 14 - User Reporting
│   ├── report_handler.py        # Report Processing
│   ├── report_categories.py     # Hate/Harassment/Spam/etc
│   ├── evidence_collection.py   # Screenshots, Links
│   ├── reporter_protection.py   # Anonymes Melden
│   └── status_tracking.py       # Report Status
│
├── /transparency            # ⭐ Art. 13, 15 - Transparency
│   ├── terms_of_service.py      # ToS Management
│   ├── community_guidelines.py  # Content Policies
│   ├── moderation_logs.py       # Public Moderation Logs
│   ├── transparency_reports.py  # Quarterly Reports
│   ├── removal_reasons.py       # Art. 15 - Begründungen
│   └── statistics.py            # Öffentliche Statistiken
│
├── /algorithm_transparency  # ⭐ Art. 24 - Algorithmen (VLOP)
│   ├── algorithm_disclosure.py  # Wie Feed funktioniert
│   ├── parameters_explanation.py # Hauptparameter
│   ├── user_controls.py         # Nutzer kann Feed steuern
│   ├── chronological_option.py  # Nicht-algorithmische Option
│   └── preference_settings.py   # Nutzereinstellungen
│
├── /risk_assessment         # Art. 33 - Risk Assessment (VLOP)
│   ├── risk_assessment.py
│   ├── systemic_risks.py
│   └── mitigation.py
│
├── /audit                   # Art. 34 - Independent Audit (VLOP)
│   ├── audit_preparation.py
│   └── evidence_collection.py
│
└── /crisis_response         # Art. 35 - Crisis Protocol (VLOP)
    ├── crisis_detection.py      # Viral Harmful Content
    ├── emergency_response.py    # Sofortmaßnahmen
    └── coordination.py          # Behörden-Koordination
```

---

### 🇩🇪 NetzDG (Netzwerkdurchsetzungsgesetz)

**Status:** 🔴 PFLICHT ab 2 Millionen User in Deutschland  
**Bußgeld:** Bis zu 50 Mio. EUR  
**Gültig seit:** 1. Oktober 2017 (Update 2021)

#### Kern-Anforderungen:

**§ 1 - Anwendungsbereich**
- Telemediendiensteanbieter
- Mit mehr als 2 Millionen Nutzern in Deutschland
- Die zum Zweck der Gewinnerzielung Inhalte Dritter speichern

**§ 2 - Meldeverfahren**
- Leicht erkennbares Meldeformular
- Dokumentation der Meldung
- Bestätigung des Eingangs
- Fristen-Tracking

**§ 3 - Umgang mit Beschwerden** ⭐
- **Offensichtlich rechtswidrig:** Entfernung innerhalb 24 Stunden
- **Rechtswidrig:** Entfernung innerhalb 7 Tagen
- Komplexe Fälle: Längere Prüfung möglich
- Begründung der Entscheidung

**§ 4 - Halbjährliche Berichtspflicht** ⭐
- Deadline: 31. Januar (Jul-Dez) & 31. Juli (Jan-Jun)
- Anzahl eingegangener Beschwerden
- Anzahl Löschungen/Sperrungen
- Durchschnittliche Bearbeitungszeit
- Organisation des Beschwerdemanagements

**§ 5 - Zustellungsbevollmächtigter** ⭐
- In Deutschland ansässige Person
- Empfangsbevollmächtigt für Zustellungen
- Name und Anschrift im Impressum

**§ 1 Abs. 3 - Rechtswidrige Inhalte (StGB-Katalog):**
- § 86 StGB - Verbreiten von Propagandamitteln verfassungswidriger Organisationen
- § 86a StGB - Verwenden von Kennzeichen verfassungswidriger Organisationen
- § 89a StGB - Vorbereitung einer schweren staatsgefährdenden Gewalttat
- § 91 StGB - Anleitung zur Begehung einer schweren staatsgefährdenden Gewalttat
- **§ 100a StGB - Landesverräterische Fälschung**
- **§ 111 StGB - Öffentliche Aufforderung zu Straftaten**
- **§ 126 StGB - Störung des öffentlichen Friedens durch Androhung von Straftaten**
- **§ 129 StGB - Bildung krimineller Vereinigungen**
- **§ 129a StGB - Bildung terroristischer Vereinigungen**
- **§ 129b StGB - Kriminelle und terroristische Vereinigungen im Ausland**
- **§ 130 StGB - Volksverhetzung** ⭐
- **§ 131 StGB - Gewaltdarstellung** ⭐
- **§ 140 StGB - Belohnung und Billigung von Straftaten**
- **§ 166 StGB - Beschimpfung von Bekenntnissen**
- **§ 184b StGB - Verbreitung, Erwerb und Besitz kinderpornographischer Inhalte** ⭐ CRITICAL
- § 185 StGB - Beleidigung ⭐
- § 186 StGB - Üble Nachrede ⭐
- § 187 StGB - Verleumdung ⭐
- § 201a StGB - Verletzung des höchstpersönlichen Lebensbereichs
- **§ 241 StGB - Bedrohung** ⭐
- **§ 269 StGB - Fälschung beweiserheblicher Daten**

#### Implementation Requirements:

```
/app/compliance/netzdg/
├── /illegal_content         # ⭐ StGB-Katalog
│   ├── __init__.py
│   ├── stgb_catalog.py          # Vollständiger StGB-Katalog
│   ├── hate_speech.py           # § 130 StGB - Volksverhetzung
│   ├── insult.py                # § 185 StGB - Beleidigung
│   ├── defamation.py            # § 186/187 StGB - Verleumdung
│   ├── threat.py                # § 241 StGB - Bedrohung
│   ├── violence.py              # § 131 StGB - Gewaltdarstellung
│   ├── csam_detection.py        # § 184b StGB - CSAM (CRITICAL!)
│   ├── terrorism.py             # § 129a/b StGB - Terrorismus
│   ├── incitement.py            # § 111 StGB - Aufruf zu Straftaten
│   └── glorification.py         # § 140 StGB - Billigung
│
├── /response_times          # ⭐ § 3 - Bearbeitungsfristen
│   ├── sla_manager.py           # Service Level Agreement
│   ├── urgent_24h.py            # Offensichtlich rechtswidrig (24h)
│   ├── standard_7d.py           # Rechtswidrig (7 Tage)
│   ├── complex_cases.py         # Komplexe Fälle
│   ├── escalation.py            # Eskalationsprozess
│   └── monitoring.py            # SLA Monitoring
│
├── /reporting_mechanism     # § 2 - Meldeverfahren
│   ├── report_form.py           # Meldeformular
│   ├── documentation.py         # Dokumentation
│   ├── confirmation.py          # Eingangsbestätigung
│   └── tracking.py              # Fristen-Tracking
│
├── /transparency_reports    # ⭐ § 4 - Halbjährliche Berichte
│   ├── report_generator.py      # Auto-generation
│   ├── statistics.py            # Statistiken
│   ├── publication.py           # Veröffentlichung
│   ├── deadlines.py             # 31. Jan / 31. Jul
│   └── templates.py             # Report-Templates
│
└── /representative          # ⭐ § 5 - Zustellungsbevollmächtigter
    ├── contact_info.py          # Kontaktdaten
    ├── legal_requests.py        # Rechtliche Anfragen
    └── impressum_integration.py # Impressum-Integration
```

---

### 👶 CHILD SAFETY (Multi-Country)

**Standards:**
- 🇺🇸 **COPPA** (Children's Online Privacy Protection Act)
- 🇩🇪 **JMStV** (Jugendmedienschutz-Staatsvertrag)
- 🇬🇧 **UK Age Appropriate Design Code**
- 🇪🇺 **GDPR Art. 8** (Kinder unter 16)

#### COPPA (USA) - Unter 13 Jahren:

**Requirements:**
- Parental Consent erforderlich
- Keine Behavioral Advertising
- Data Minimization verschärft
- No Third-Party Tracking
- Bußgeld: Bis zu 50k USD pro Violation

#### JMStV (Deutschland):

**Requirements:**
- Altersverifikation bei nicht-jugendfreien Inhalten
- Jugendschutzbeauftragter ab 50 Mitarbeiter
- Voreinstellungen kindersicher
- Alterseinstufung von Inhalten

#### UK Age Appropriate Design Code:

**15 Design Standards für Kinder:**
1. Best interests of the child
2. Data protection impact assessments
3. Age-appropriate application
4. Transparency
5. Detrimental use of data
6. Policies and community standards
7. Default settings
8. Data minimization
9. Data sharing
10. Geolocation
11. Parental controls
12. Profiling
13. Nudge techniques
14. Connected toys and devices
15. Online tools

#### Implementation Requirements:

```
/app/compliance/child_safety/
├── /age_verification        # ⭐ Altersverifikation
│   ├── age_gate.py              # Altersabfrage
│   ├── verification_methods.py  # ID/Credit Card/Face
│   ├── parental_consent.py      # COPPA (< 13)
│   ├── age_estimation.py        # AI Age Estimation
│   └── document_verification.py # ID-Dokument Check
│
├── /content_filtering       # ⭐ Altersgerechte Inhalte
│   ├── age_rating.py            # Content Age Rating (USK-style)
│   ├── safe_search.py           # Safe Search Filter
│   ├── restricted_mode.py       # Kids Mode
│   ├── content_warnings.py      # Content Warnings
│   └── automatic_blur.py        # Auto-blur NSFW
│
├── /parental_controls       # ⭐ Elternkontrolle
│   ├── family_link.py           # Parent Dashboard
│   ├── screen_time.py           # Nutzungslimits
│   ├── content_approval.py      # Pre-approval
│   ├── activity_reports.py      # Aktivitäts-Monitoring
│   ├── messaging_controls.py    # Wer kann schreiben
│   └── notification_alerts.py   # Eltern-Benachrichtigungen
│
├── /grooming_prevention     # ⭐ Online Grooming Schutz
│   ├── pattern_detection.py     # Verdächtige Muster
│   ├── age_gap_limits.py        # Erwachsene-Kind Kontakt begrenzen
│   ├── private_messaging_rules.py # DM Restriktionen
│   ├── keyword_monitoring.py    # Grooming Keywords
│   ├── alert_system.py          # Eltern/Behörden alarmieren
│   └── reporting.py             # Report to NCMEC/BKA
│
└── /education               # Safety Education
    ├── safety_tips.py
    ├── reporting_guide.py
    └── resources.py
```

---

### 🌍 ISO/IEC 27001:2022 (Information Security Management System)

**Status:** 🟡 STARK EMPFOHLEN für B2B  
**Kosten:** 10-50k EUR Zertifizierung  
**Gültig:** Weltweit anerkannt

#### ISMS Core (Clauses 4-10):

**Clause 4 - Context of the Organization**
- Understanding the organization
- Understanding stakeholder needs
- Determining ISMS scope
- Information security management system

**Clause 5 - Leadership**
- Leadership and commitment
- Policy
- Organizational roles, responsibilities and authorities

**Clause 6 - Planning**
- Actions to address risks and opportunities
- Information security objectives and planning

**Clause 7 - Support**
- Resources
- Competence
- Awareness
- Communication
- Documented information

**Clause 8 - Operation**
- Operational planning and control
- Information security risk assessment
- Information security risk treatment

**Clause 9 - Performance Evaluation**
- Monitoring, measurement, analysis and evaluation
- Internal audit
- Management review

**Clause 10 - Improvement**
- Nonconformity and corrective action
- Continual improvement

#### Annex A - 93 Controls (14 Categories):

**A.5 - Organizational Controls (37 controls)**
- Policies for information security
- Information security roles and responsibilities
- Segregation of duties
- Management responsibilities
- Contact with authorities
- ...

**A.6 - People Controls (8 controls)**
- Screening
- Terms and conditions of employment
- Information security awareness, education and training
- Disciplinary process
- ...

**A.7 - Physical Controls (14 controls)**
- Physical security perimeters
- Physical entry
- Securing offices, rooms and facilities
- ...

**A.8 - Technological Controls (34 controls)**
- User endpoint devices
- Privileged access rights
- Information access restriction
- Access to source code
- Secure authentication
- ...

**A.9 - Access Control** ⭐ (Implementation Priority: HIGH)
**A.10 - Cryptography** ⭐ (Implementation Priority: HIGH)
**A.12 - Operations Security** ⭐ (Implementation Priority: HIGH)
**A.16 - Incident Management** ⭐ (Implementation Priority: HIGH)
**A.17 - Business Continuity** ⭐ (Implementation Priority: MEDIUM)

#### Implementation Requirements:

```
/app/compliance/iso27001/
├── /isms                    # ⭐ ISMS Core (Clauses 4-10)
│   ├── isms_framework.py        # Main Framework
│   ├── context.py               # Clause 4 - Context
│   ├── scope.py                 # ISMS Scope
│   ├── leadership.py            # Clause 5 - Leadership
│   ├── planning.py              # Clause 6 - Planning
│   ├── support.py               # Clause 7 - Support
│   ├── operation.py             # Clause 8 - Operation
│   ├── performance.py           # Clause 9 - Performance
│   └── improvement.py           # Clause 10 - Improvement
│
├── /risk_management         # ⭐ Risk Assessment & Treatment
│   ├── risk_assessment.py       # Risk Identification
│   ├── risk_analysis.py         # Risk Analysis
│   ├── risk_evaluation.py       # Risk Evaluation
│   ├── risk_treatment.py        # Treatment Plan
│   ├── risk_register.py         # Risk Register
│   ├── risk_monitoring.py       # Monitoring
│   └── risk_reporting.py        # Reporting
│
├── /controls                # Annex A Controls (93 controls)
│   ├── /a05_organizational
│   │   ├── a05_01_policies.py
│   │   ├── a05_02_roles.py
│   │   ├── a05_03_segregation.py
│   │   └── ... (37 controls total)
│   │
│   ├── /a06_people
│   │   ├── a06_01_screening.py
│   │   ├── a06_02_terms.py
│   │   ├── a06_03_awareness.py
│   │   └── ... (8 controls total)
│   │
│   ├── /a07_physical
│   ├── /a08_technological
│   │
│   ├── /a09_access_control  # ⭐ PRIORITY HIGH
│   │   ├── access_policy.py
│   │   ├── user_management.py
│   │   ├── privilege_management.py
│   │   └── access_review.py
│   │
│   ├── /a10_cryptography    # ⭐ PRIORITY HIGH
│   │   ├── crypto_policy.py
│   │   ├── key_management.py
│   │   └── crypto_controls.py
│   │
│   ├── /a11_physical_security
│   │
│   ├── /a12_operations      # ⭐ PRIORITY HIGH
│   │   ├── procedures.py
│   │   ├── change_management.py
│   │   ├── capacity_management.py
│   │   ├── malware_protection.py
│   │   ├── backup.py
│   │   ├── logging.py           # A.12.4 Logging
│   │   └── monitoring.py
│   │
│   ├── /a13_communications
│   ├── /a14_acquisition
│   ├── /a15_supplier
│   │
│   ├── /a16_incident        # ⭐ PRIORITY HIGH
│   │   ├── incident_management.py
│   │   ├── incident_response.py
│   │   ├── evidence_collection.py
│   │   └── lessons_learned.py
│   │
│   ├── /a17_business_continuity # ⭐ PRIORITY MEDIUM
│   │   ├── bcp.py               # Business Continuity Plan
│   │   ├── drp.py               # Disaster Recovery Plan
│   │   ├── redundancy.py
│   │   └── testing.py
│   │
│   └── /a18_compliance
│       ├── legal_requirements.py
│       ├── ip_rights.py
│       └── privacy_compliance.py
│
├── /audit                   # Internal Audits
│   ├── audit_scheduler.py
│   ├── audit_execution.py
│   ├── audit_reporting.py
│   └── audit_logger.py          # ⭐ Audit Trail
│
└── /certification           # Certification Support
    ├── evidence_collector.py
    ├── gap_analysis.py
    ├── documentation.py
    └── readiness_check.py
```

---

### 📊 ISO/IEC 25010:2011 (Software Quality Model)

**8 Quality Characteristics:**

1. **Functional Suitability**
   - Functional completeness
   - Functional correctness
   - Functional appropriateness

2. **Performance Efficiency**
   - Time behaviour
   - Resource utilization
   - Capacity

3. **Compatibility**
   - Co-existence
   - Interoperability

4. **Usability**
   - Appropriateness recognizability
   - Learnability
   - Operability
   - User error protection
   - User interface aesthetics
   - Accessibility

5. **Reliability**
   - Maturity
   - Availability
   - Fault tolerance
   - Recoverability

6. **Security**
   - Confidentiality
   - Integrity
   - Non-repudiation
   - Accountability
   - Authenticity

7. **Maintainability**
   - Modularity
   - Reusability
   - Analysability
   - Modifiability
   - Testability

8. **Portability**
   - Adaptability
   - Installability
   - Replaceability

#### Implementation:

```
/app/compliance/iso25010/
├── /characteristics
│   ├── functional_suitability.py
│   ├── performance_efficiency.py
│   ├── compatibility.py
│   ├── usability.py
│   ├── reliability.py
│   ├── security.py
│   ├── maintainability.py
│   └── portability.py
│
└── /metrics
    ├── code_metrics.py          # Cyclomatic Complexity, LOC
    ├── test_metrics.py          # Coverage, Pass Rate
    ├── performance_metrics.py   # Response Time, Throughput
    └── quality_dashboard.py
```

---

### 🧪 ISO/IEC 29119 (Software Testing)

**Test Coverage Requirements:**

- **Unit Tests:** 85%+ Code Coverage ⭐
- **Integration Tests:** All API Endpoints
- **Security Tests:** OWASP Top 10
- **Performance Tests:** Load & Stress
- **Penetration Tests:** Quarterly
- **DRM Tests:** Anti-Tamper, License Validation

#### Implementation:

```
/app/compliance/iso29119/
├── /strategies
│   ├── test_strategy.py
│   ├── test_planning.py
│   └── test_design.py
│
├── /coverage
│   ├── code_coverage.py         # ⭐ 85%+ Target
│   ├── branch_coverage.py
│   └── mutation_testing.py
│
└── /reporting
    ├── test_reports.py
    └── quality_dashboard.py
```

---

### 🛡️ OWASP Top 10 (2021)

**Top 10 Web Application Security Risks:**

1. **A01:2021 - Broken Access Control** ⭐
   - Unauthorized access to resources
   - Missing authorization checks
   - Insecure Direct Object References (IDOR)

2. **A02:2021 - Cryptographic Failures** ⭐
   - Weak encryption algorithms
   - Unencrypted sensitive data
   - Weak key management

3. **A03:2021 - Injection** ⭐
   - SQL Injection
   - NoSQL Injection
   - Command Injection
   - LDAP Injection

4. **A04:2021 - Insecure Design**
   - Missing security requirements
   - Threat modeling missing
   - Secure design patterns not used

5. **A05:2021 - Security Misconfiguration** ⭐
   - Default credentials
   - Unnecessary features enabled
   - Error messages expose information

6. **A06:2021 - Vulnerable and Outdated Components**
   - Using components with known vulnerabilities
   - No dependency management

7. **A07:2021 - Identification and Authentication Failures** ⭐
   - Weak passwords allowed
   - Missing MFA
   - Session fixation

8. **A08:2021 - Software and Data Integrity Failures**
   - Unsigned code/data
   - Insecure CI/CD pipeline
   - Auto-update without verification

9. **A09:2021 - Security Logging and Monitoring Failures** ⭐
   - Missing logs
   - No alerting
   - No incident response

10. **A10:2021 - Server-Side Request Forgery (SSRF)**
    - Unvalidated URLs
    - Network access from user input

#### Implementation:

```
/app/compliance/owasp/
├── a01_broken_access.py
├── a02_crypto_failures.py
├── a03_injection.py
├── a04_insecure_design.py
├── a05_misconfiguration.py
├── a06_vulnerable_components.py
├── a07_auth_failures.py
├── a08_integrity_failures.py
├── a09_logging_failures.py
└── a10_ssrf.py
```

---

### 🔐 CERT Secure Coding Standards (Python)

**Core Rules:**
- Input Validation
- Expressions
- Integers
- Strings
- Memory Management (für Python weniger relevant)

#### Implementation:

```
/app/compliance/cert/
├── input_validation.py
├── expressions.py
├── integers.py
├── strings.py
└── memory_management.py
```

---

### 🔒 DRM System (Denuvo-Style)

**Features:**
- AES-256-GCM Encryption
- RSA-4096 Key Exchange
- Hardware Binding (HWID)
- License Management (Online + Offline)
- Anti-Tamper Protection
- Forensic Watermarking
- Access Control

#### Implementation:

```
/app/security/drm/
├── /core
│   ├── drm_engine.py            # Main DRM Engine
│   ├── protection_layer.py      # Protection Orchestration
│   ├── security_context.py      # Security Context Manager
│   └── drm_config.py            # DRM Configuration
│
├── /encryption
│   ├── aes_cipher.py            # AES-256-GCM
│   ├── rsa_cipher.py            # RSA-4096
│   ├── key_manager.py           # Key Rotation
│   ├── key_derivation.py        # PBKDF2 + HKDF
│   ├── hardware_crypto.py       # Hardware-bound Keys
│   └── crypto_primitives.py     # Low-level Crypto
│
├── /license
│   ├── license_generator.py     # License Generation
│   ├── license_validator.py     # Online + Offline Validation
│   ├── license_server.py        # HA License Server
│   ├── license_types.py         # License Types
│   ├── hwid_generator.py        # Hardware ID
│   ├── device_manager.py        # Device Binding (Max 3)
│   ├── offline_license.py       # Offline Grace (7 days)
│   └── license_renewal.py       # Automatic Renewal
│
├── /anti_tamper
│   ├── integrity_checker.py     # Code Integrity (SHA-256)
│   ├── checksum_validator.py    # Runtime Validation
│   ├── debugger_detection.py    # Anti-Debug
│   ├── vm_detection.py          # Virtual Machine Detection
│   ├── memory_protection.py     # Memory Encryption
│   ├── code_obfuscation.py      # Bytecode Obfuscation
│   ├── runtime_guard.py         # Runtime Integrity Monitor
│   └── tamper_response.py       # Tamper Response Actions
│
├── /watermarking
│   ├── visible_watermark.py     # Visible Username
│   ├── invisible_watermark.py   # Steganography (LSB)
│   ├── forensic_watermark.py    # User ID + Timestamp
│   ├── watermark_extractor.py   # Leak Source ID
│   ├── digital_signature.py     # RSA Content Signing
│   └── video_watermark.py       # Video Watermarking
│
├── /access_control
│   ├── drm_middleware.py        # DRM Check Middleware
│   ├── content_gate.py          # Content Access Gate
│   ├── session_validator.py     # Session-bound Access
│   ├── access_logger.py         # Audit Trail
│   └── rate_limiter.py          # DRM Rate Limiting
│
├── /monitoring
│   ├── drm_monitor.py           # Health Monitoring
│   ├── violation_detector.py    # Piracy Detection
│   ├── alert_manager.py         # Real-time Alerts
│   ├── analytics.py             # DRM Analytics
│   └── forensics.py             # Forensic Analysis
│
└── /streaming
    ├── hls_encryptor.py         # HLS AES-128
    ├── dash_encryptor.py        # MPEG-DASH
    └── token_generator.py       # Streaming Tokens
```

---

## 📋 PHASE 1: PREPARATION & ANALYSIS

### Step 1.1: Backup erstellen

```bash
#!/bin/bash
# Backup Script

cd /home/pascal/Lernsystem
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🔄 Creating backup..."
tar -czf ../lernsystem_backup_${TIMESTAMP}.tar.gz backend/
echo "✅ Backup created: ../lernsystem_backup_${TIMESTAMP}.tar.gz"

# Git commit if available
cd backend
if [ -d .git ]; then
    git add -A
    git commit -m "Backup before migration (${TIMESTAMP})" 2>/dev/null || echo "Nothing to commit"
    echo "✅ Git backup committed"
fi

echo ""
echo "📊 Backup Summary:"
ls -lh ../lernsystem_backup_${TIMESTAMP}.tar.gz
```

### Step 1.2: Aktuelle Struktur analysieren

```bash
#!/bin/bash
# Structure Analysis Script

cd /home/pascal/Lernsystem/backend

echo "📁 Analyzing current structure..."
echo ""

# Create analysis directory
mkdir -p /tmp/lernsystem_analysis

# Generate tree (max 4 levels)
echo "Generating directory tree..."
tree -h -C -I '__pycache__|*.pyc|.git|venv|node_modules|.pytest_cache' -L 4 > /tmp/lernsystem_analysis/structure_level4.txt

# Generate full tree (to file)
tree -h -C -I '__pycache__|*.pyc|.git|venv|node_modules|.pytest_cache' > /tmp/lernsystem_analysis/structure_full.txt

# Count statistics
echo ""
echo "📊 Statistics:"
echo "----------------------------------------"
echo "Total directories:"
find . -type d -not -path '*/\.*' -not -path '*/venv/*' -not -path '*/__pycache__/*' | wc -l
echo ""
echo "Total Python files:"
find . -name '*.py' -not -path '*/\.*' -not -path '*/venv/*' -not -path '*/__pycache__/*' | wc -l
echo ""
echo "Total lines of code:"
find . -name '*.py' -not -path '*/\.*' -not -path '*/venv/*' -not -path '*/__pycache__/*' -exec wc -l {} + | tail -1
echo "----------------------------------------"

# Show structure (level 4)
echo ""
echo "📂 Directory Structure (Level 4):"
echo "----------------------------------------"
cat /tmp/lernsystem_analysis/structure_level4.txt
echo ""

# Find duplicates
echo "🔍 Finding potential duplicates..."
find . -name '*.py' -not -path '*/\.*' -not -path '*/venv/*' -not -path '*/__pycache__/*' -type f -exec basename {} \; | sort | uniq -d > /tmp/lernsystem_analysis/duplicate_filenames.txt

if [ -s /tmp/lernsystem_analysis/duplicate_filenames.txt ]; then
    echo "⚠️  Found duplicate filenames:"
    cat /tmp/lernsystem_analysis/duplicate_filenames.txt
else
    echo "✅ No duplicate filenames found"
fi

echo ""
echo "💾 Analysis saved to: /tmp/lernsystem_analysis/"
```

### Step 1.3: Ziel-Architektur laden

```bash
#!/bin/bash
# Load Target Architecture

cd /home/pascal/Lernsystem/scripts

echo "📖 Loading target architecture..."
echo ""

if [ ! -f complete-social-backend-architecture.md ]; then
    echo "❌ ERROR: complete-social-backend-architecture.md not found!"
    exit 1
fi

echo "✅ Target architecture found"
echo ""
echo "📄 File info:"
ls -lh complete-social-backend-architecture.md
echo ""

# Show first 50 lines
echo "📋 Preview (first 50 lines):"
echo "----------------------------------------"
head -50 complete-social-backend-architecture.md
echo "----------------------------------------"
echo ""

echo "📚 To view full file:"
echo "cat /home/pascal/Lernsystem/scripts/complete-social-backend-architecture.md"
```

### Step 1.4: Migration Mapping erstellen

```bash
#!/bin/bash
# Create Migration Mapping

cd /home/pascal/Lernsystem/backend

echo "🗺️  Creating migration mapping..."

cat > /tmp/lernsystem_analysis/migration_mapping.md << 'EOF'
# Migration Mapping: Current → Target

## 📁 Directory Mappings

### Root Level
- `src/` → `app/` (RENAME)
- `src/__init__.py` → `app/__init__.py` (MIGRATE)
- `src/config.py` → `app/config.py` (MIGRATE)
- `src/extensions.py` → `app/extensions.py` (MIGRATE)

### API Layer
- `src/api/` → `app/api/v1/` (MIGRATE)
- `src/api/routes/` → `app/api/v1/` (FLATTEN)

### Models
- `src/models/` → `app/models/` (KEEP STRUCTURE)

### Services
- `src/services/` → `app/services/` (KEEP STRUCTURE)

### Repositories
- `src/repositories/` → `app/repositories/` (KEEP STRUCTURE)

### NEW: Core System (Feature Flags)
- CREATE: `app/core/feature_flags/`
- CREATE: `app/core/rollout/`
- CREATE: `app/core/configuration/`

### NEW: Social Layer
- CREATE: `app/social/posts/`
- CREATE: `app/social/feed/`
- CREATE: `app/social/follow/`
- CREATE: `app/social/engagement/`
- CREATE: `app/social/profiles/`
- CREATE: `app/social/discovery/`
- CREATE: `app/social/notifications/`
- CREATE: `app/social/analytics/`

### NEW: Compliance Layer
- CREATE: `app/compliance/dsa/` (complete)
- CREATE: `app/compliance/netzdg/` (complete)
- CREATE: `app/compliance/gdpr/` (complete)
- CREATE: `app/compliance/child_safety/` (complete)
- CREATE: `app/compliance/iso27001/` (complete)
- CREATE: `app/compliance/iso25010/`
- CREATE: `app/compliance/owasp/`
- CREATE: `app/compliance/cert/`

### NEW: Security Layer
- CREATE: `app/security/drm/` (complete Denuvo-style)
- `src/security/` → `app/security/auth/` (if exists)
- CREATE: `app/security/rbac/`
- CREATE: `app/security/middleware/`
- CREATE: `app/security/encryption/`

### NEW: AI Layer
- `src/ai/` → `app/ai/generation/` (if exists)
- CREATE: `app/ai/content_moderation/`
- CREATE: `app/ai/recommendation/`
- CREATE: `app/ai/safety/`

### NEW: Monitoring Layer
- CREATE: `app/monitoring/trust_safety/`
- CREATE: `app/monitoring/feature_analytics/`
- CREATE: `app/monitoring/metrics/`
- CREATE: `app/monitoring/logging/`
- CREATE: `app/monitoring/tracing/`
- CREATE: `app/monitoring/alerting/`

## 📄 File Actions

### To Migrate (Copy & Update Imports)
- All `*.py` files in `src/`
- Update all imports: `from src.` → `from app.`
- Update all imports: `import src.` → `import app.`

### To Delete (After Migration)
- `src/` directory (after verification)
- Duplicate files (if found)
- Old test files in wrong locations

### To Create (New Files)
- See complete-social-backend-architecture.md
- ~200+ new Python files
- All `__init__.py` files

## 🔄 Import Update Strategy

### Pattern Replacements:
```python
# Old
from src.models import User
from src.services import AuthService
import src.utils

# New
from app.models import User
from app.services import AuthService
import app.utils
```

### Automated Script:
```bash
find app/ -name '*.py' -type f -exec sed -i 's/from src\./from app\./g' {} +
find app/ -name '*.py' -type f -exec sed -i 's/import src\./import app\./g' {} +
```

## ✅ Verification Checklist

- [ ] All files migrated from `src/` to `app/`
- [ ] All imports updated
- [ ] No more `src.*` imports
- [ ] All tests pass
- [ ] Flask app starts successfully
- [ ] No duplicate files
- [ ] Old `src/` directory removed

## 📊 Progress Tracking

### Phase 1: Preparation ⏳
- [ ] Backup created
- [ ] Structure analyzed
- [ ] Mapping created
- [ ] Target architecture loaded

### Phase 2: Core Migration ⏳
- [ ] Root files migrated
- [ ] API layer migrated
- [ ] Models migrated
- [ ] Services migrated
- [ ] Repositories migrated

### Phase 3: New Features ⏳
- [ ] Feature Flags implemented
- [ ] Social Layer created
- [ ] Compliance Layer created
- [ ] Security Layer created
- [ ] AI Layer extended
- [ ] Monitoring Layer created

### Phase 4: Testing ⏳
- [ ] Unit tests updated
- [ ] Integration tests updated
- [ ] All tests passing
- [ ] Manual testing completed

### Phase 5: Cleanup ⏳
- [ ] Old `src/` deleted
- [ ] Duplicates removed
- [ ] Documentation updated
- [ ] Git committed

EOF

echo "✅ Migration mapping created"
echo ""
echo "📄 View mapping:"
echo "cat /tmp/lernsystem_analysis/migration_mapping.md"
```

---

## 📋 PHASE 2: CREATE NEW STRUCTURE

### Step 2.1: Create complete directory structure

```bash
#!/bin/bash
# Create Complete Directory Structure

cd /home/pascal/Lernsystem/backend

echo "🏗️  Creating complete directory structure..."
echo ""

# Function to create directory with confirmation
create_dir() {
    mkdir -p "$1"
    if [ $? -eq 0 ]; then
        echo "✅ Created: $1"
    else
        echo "❌ Failed: $1"
    fi
}

# Core System
echo "📦 Core System..."
create_dir "app/core/feature_flags"
create_dir "app/core/rollout"
create_dir "app/core/configuration"

# API Layer
echo ""
echo "🌐 API Layer..."
create_dir "app/api/v1"
create_dir "app/api/social"
create_dir "app/api/community"
create_dir "app/api/messaging"
create_dir "app/api/admin"
create_dir "app/api/ai"

# Social Layer
echo ""
echo "🌟 Social Layer..."
create_dir "app/social/posts"
create_dir "app/social/feed"
create_dir "app/social/follow"
create_dir "app/social/engagement"
create_dir "app/social/profiles"
create_dir "app/social/discovery"
create_dir "app/social/notifications"
create_dir "app/social/analytics"

# Compliance - DSA
echo ""
echo "⚖️  Compliance: DSA..."
create_dir "app/compliance/dsa/content_moderation"
create_dir "app/compliance/dsa/ai_detection"
create_dir "app/compliance/dsa/reporting"
create_dir "app/compliance/dsa/transparency"
create_dir "app/compliance/dsa/algorithm_transparency"
create_dir "app/compliance/dsa/crisis_response"

# Compliance - NetzDG
echo ""
echo "⚖️  Compliance: NetzDG..."
create_dir "app/compliance/netzdg/illegal_content"
create_dir "app/compliance/netzdg/response_times"
create_dir "app/compliance/netzdg/transparency_reports"
create_dir "app/compliance/netzdg/reporting_mechanism"
create_dir "app/compliance/netzdg/representative"

# Compliance - GDPR
echo ""
echo "⚖️  Compliance: GDPR..."
create_dir "app/compliance/gdpr/principles"
create_dir "app/compliance/gdpr/legal_basis"
create_dir "app/compliance/gdpr/consent"
create_dir "app/compliance/gdpr/children"
create_dir "app/compliance/gdpr/data_subject_rights"
create_dir "app/compliance/gdpr/privacy_by_design"
create_dir "app/compliance/gdpr/processing_records"
create_dir "app/compliance/gdpr/breach_management"
create_dir "app/compliance/gdpr/dpia"
create_dir "app/compliance/gdpr/transfers"
create_dir "app/compliance/gdpr/dpo"
create_dir "app/compliance/gdpr/social_data"

# Compliance - Child Safety
echo ""
echo "⚖️  Compliance: Child Safety..."
create_dir "app/compliance/child_safety/age_verification"
create_dir "app/compliance/child_safety/content_filtering"
create_dir "app/compliance/child_safety/parental_controls"
create_dir "app/compliance/child_safety/grooming_prevention"
create_dir "app/compliance/child_safety/education"

# Compliance - ISO 27001
echo ""
echo "⚖️  Compliance: ISO 27001..."
create_dir "app/compliance/iso27001/isms"
create_dir "app/compliance/iso27001/risk_management"
create_dir "app/compliance/iso27001/controls/a05_organizational"
create_dir "app/compliance/iso27001/controls/a06_people"
create_dir "app/compliance/iso27001/controls/a07_physical"
create_dir "app/compliance/iso27001/controls/a08_technological"
create_dir "app/compliance/iso27001/controls/a09_access_control"
create_dir "app/compliance/iso27001/controls/a10_cryptography"
create_dir "app/compliance/iso27001/controls/a11_physical_security"
create_dir "app/compliance/iso27001/controls/a12_operations"
create_dir "app/compliance/iso27001/controls/a13_communications"
create_dir "app/compliance/iso27001/controls/a14_acquisition"
create_dir "app/compliance/iso27001/controls/a15_supplier"
create_dir "app/compliance/iso27001/controls/a16_incident"
create_dir "app/compliance/iso27001/controls/a17_business_continuity"
create_dir "app/compliance/iso27001/controls/a18_compliance"
create_dir "app/compliance/iso27001/audit"
create_dir "app/compliance/iso27001/certification"

# Compliance - Other Standards
echo ""
echo "⚖️  Compliance: Other Standards..."
create_dir "app/compliance/iso25010/characteristics"
create_dir "app/compliance/iso25010/metrics"
create_dir "app/compliance/iso29119/strategies"
create_dir "app/compliance/iso29119/coverage"
create_dir "app/compliance/iso29119/reporting"
create_dir "app/compliance/owasp"
create_dir "app/compliance/cert"

# Security - DRM
echo ""
echo "🔒 Security: DRM..."
create_dir "app/security/drm/core"
create_dir "app/security/drm/encryption"
create_dir "app/security/drm/license"
create_dir "app/security/drm/anti_tamper"
create_dir "app/security/drm/watermarking"
create_dir "app/security/drm/access_control"
create_dir "app/security/drm/monitoring"
create_dir "app/security/drm/streaming"

# Security - Other
echo ""
echo "🔒 Security: Other..."
create_dir "app/security/auth"
create_dir "app/security/rbac"
create_dir "app/security/middleware"
create_dir "app/security/encryption"

# AI Layer
echo ""
echo "🤖 AI Layer..."
create_dir "app/ai/content_moderation"
create_dir "app/ai/recommendation"
create_dir "app/ai/safety"
create_dir "app/ai/generation"

# Monitoring Layer
echo ""
echo "📊 Monitoring Layer..."
create_dir "app/monitoring/trust_safety"
create_dir "app/monitoring/feature_analytics"
create_dir "app/monitoring/metrics"
create_dir "app/monitoring/logging"
create_dir "app/monitoring/tracing"
create_dir "app/monitoring/alerting"

# Other Layers
echo ""
echo "📦 Other Layers..."
create_dir "app/i18n/locales"
create_dir "app/services"
create_dir "app/repositories"
create_dir "app/models"
create_dir "app/tasks"
create_dir "app/websocket"
create_dir "app/utils"

# Infrastructure
echo ""
echo "🏗️  Infrastructure..."
create_dir "infrastructure/docker"
create_dir "infrastructure/kubernetes"
create_dir "infrastructure/terraform"

# Tests
echo ""
echo "🧪 Tests..."
create_dir "tests/unit"
create_dir "tests/integration"
create_dir "tests/e2e"
create_dir "tests/compliance"
create_dir "tests/security"
create_dir "tests/performance"

# Scripts
echo ""
echo "📜 Scripts..."
create_dir "scripts/migration"
create_dir "scripts/deployment"
create_dir "scripts/maintenance"

# Documentation
echo ""
echo "📚 Documentation..."
create_dir "docs/api"
create_dir "docs/architecture"
create_dir "docs/compliance"
create_dir "docs/security"
create_dir "docs/deployment"

# Compliance Evidence
echo ""
echo "📁 Compliance Evidence..."
create_dir "compliance_evidence/gdpr"
create_dir "compliance_evidence/iso27001"
create_dir "compliance_evidence/dsa"
create_dir "compliance_evidence/netzdg"
create_dir "compliance_evidence/audits"

echo ""
echo "✅ Directory structure created!"
echo ""
echo "📊 Summary:"
echo "Total directories created: $(find app -type d | wc -l)"
```

### Step 2.2: Create all __init__.py files

```bash
#!/bin/bash
# Create __init__.py Files

cd /home/pascal/Lernsystem/backend

echo "📝 Creating __init__.py files..."
echo ""

# Find all directories in app/ and create __init__.py
find app -type d -exec touch {}/__init__.py \;

# Count created files
INIT_COUNT=$(find app -name '__init__.py' | wc -l)

echo "✅ Created $INIT_COUNT __init__.py files"
echo ""

# Verify
echo "📋 Sample __init__.py locations:"
find app -name '__init__.py' | head -20
```

---

## 📋 PHASE 3: CORE MIGRATION

### Step 3.1: Migrate root files

```bash
#!/bin/bash
# Migrate Root Files

cd /home/pascal/Lernsystem/backend

echo "📦 Migrating root files..."
echo ""

# Function to migrate file
migrate_file() {
    src_file=$1
    dest_file=$2
    
    if [ -f "$src_file" ]; then
        cp "$src_file" "$dest_file"
        echo "✅ Migrated: $src_file → $dest_file"
    else
        echo "⏭️  Skipped (not found): $src_file"
    fi
}

# Migrate core files
migrate_file "src/__init__.py" "app/__init__.py"
migrate_file "src/config.py" "app/config.py"
migrate_file "src/extensions.py" "app/extensions.py"
migrate_file "src/app.py" "app.py"
migrate_file "src/wsgi.py" "wsgi.py"

echo ""
echo "✅ Root files migrated"
```

### Step 3.2: Update imports in migrated files

```python
#!/usr/bin/env python3
# scripts/migration/update_imports.py

import os
import re
import sys
from pathlib import Path

def update_imports_in_file(filepath):
    """Update imports from src.* to app.*"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace imports
        # from src.xxx import yyy
        content = re.sub(r'from src\.', 'from app.', content)
        
        # import src.xxx
        content = re.sub(r'import src\.', 'import app.', content)
        
        # Only write if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False

def main():
    backend_dir = Path('/home/pascal/Lernsystem/backend')
    app_dir = backend_dir / 'app'
    
    if not app_dir.exists():
        print("❌ app/ directory not found!")
        return
    
    print("🔄 Updating imports in all Python files...")
    print("")
    
    updated_files = []
    
    # Find all .py files
    for py_file in app_dir.rglob('*.py'):
        if update_imports_in_file(py_file):
            updated_files.append(py_file)
            print(f"✅ Updated: {py_file.relative_to(backend_dir)}")
    
    # Also update root files
    for root_file in ['app.py', 'wsgi.py', 'manage.py']:
        root_path = backend_dir / root_file
        if root_path.exists():
            if update_imports_in_file(root_path):
                updated_files.append(root_path)
                print(f"✅ Updated: {root_file}")
    
    print("")
    print(f"✅ Updated {len(updated_files)} files")
    
    # Verify no more src.* imports
    print("")
    print("🔍 Verifying no more src.* imports...")
    
    remaining = []
    for py_file in app_dir.rglob('*.py'):
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'from src.' in content or 'import src.' in content:
                remaining.append(py_file)
    
    if remaining:
        print(f"⚠️  Found {len(remaining)} files with remaining src.* imports:")
        for f in remaining[:10]:  # Show first 10
            print(f"   - {f.relative_to(backend_dir)}")
    else:
        print("✅ No remaining src.* imports found!")

if __name__ == '__main__':
    main()
```

```bash
# Run the import updater
python3 scripts/migration/update_imports.py
```

### Step 3.3: Migrate existing modules

```bash
#!/bin/bash
# Migrate Existing Modules

cd /home/pascal/Lernsystem/backend

echo "📦 Migrating existing modules..."
echo ""

# Function to migrate directory
migrate_directory() {
    src_dir=$1
    dest_dir=$2
    
    if [ -d "$src_dir" ]; then
        echo "📁 Migrating: $src_dir → $dest_dir"
        
        # Copy directory
        cp -r "$src_dir"/* "$dest_dir/" 2>/dev/null
        
        # Count files
        FILE_COUNT=$(find "$dest_dir" -name '*.py' | wc -l)
        echo "   ✅ Copied $FILE_COUNT Python files"
    else
        echo "⏭️  Skipped (not found): $src_dir"
    fi
    echo ""
}

# Migrate directories
migrate_directory "src/api" "app/api/v1"
migrate_directory "src/models" "app/models"
migrate_directory "src/services" "app/services"
migrate_directory "src/repositories" "app/repositories"
migrate_directory "src/tasks" "app/tasks"
migrate_directory "src/utils" "app/utils"
migrate_directory "src/websocket" "app/websocket"
migrate_directory "src/i18n" "app/i18n"

# If src/ai exists, migrate to app/ai/generation
if [ -d "src/ai" ]; then
    echo "🤖 Migrating AI modules..."
    mkdir -p "app/ai/generation"
    cp -r src/ai/* app/ai/generation/ 2>/dev/null
    echo "   ✅ AI modules migrated to app/ai/generation/"
    echo ""
fi

echo "✅ Module migration complete"
echo ""
echo "📊 Migrated modules:"
echo "   - API Layer: $(find app/api/v1 -name '*.py' 2>/dev/null | wc -l) files"
echo "   - Models: $(find app/models -name '*.py' 2>/dev/null | wc -l) files"
echo "   - Services: $(find app/services -name '*.py' 2>/dev/null | wc -l) files"
echo "   - Repositories: $(find app/repositories -name '*.py' 2>/dev/null | wc -l) files"
echo "   - Tasks: $(find app/tasks -name '*.py' 2