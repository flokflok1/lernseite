-- ============================================================================
-- Seed Data: Dashboard Widget Definitions
-- Description: Standard dashboard widgets available to users
--              15 widget types organized by role tier (free, premium, school_admin)
-- Source: 080_dashboard_widget_system.sql
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (Seed Data)
-- ============================================================================

-- ============================================================================
-- Dashboard Widget Definitions - 15 Standard Widgets
-- ============================================================================
-- Seeds the dashboards.widgets table with 15 standard widget types
-- Each widget has role-based access control via min_role_required
--
-- Widget Categories:
--   1. Learning Widgets (free) - Progress, Courses, Library, Time Tracker, Tasks
--   2. Analytics Widgets (free) - Score, Messages, Theory Access
--   3. Premium Widgets (premium) - KI Recommendations, Token Status, LiveRoom, Groups, Exam Simulator, KI Quick Panel
--   4. Organisation Widgets (school_admin) - Calendar
--
-- Role Access Hierarchy:
--   1. free (student)
--   2. premium
--   3. creator
--   4. teacher
--   5. school_admin
--   6. company_admin
--   7. admin
--   8. superadmin

INSERT INTO dashboards.widgets (widget_type, name, description, component_path, min_role_required, default_settings) VALUES
-- Learning Widgets (Alle Rollen)
('progress', 'Lernfortschritt', 'Visualisierung des Lernfortschritts über alle Kurse', 'ProgressWidget.vue', 'free', '{"show_percentage": true, "show_chart": true}'),
('courses', 'Meine Kurse', 'Übersicht aktiver Kurse', 'CoursesWidget.vue', 'free', '{"max_courses": 5, "show_progress": true}'),
('library', 'Bibliothek', 'Gespeicherte Kurse und Inhalte', 'LibraryWidget.vue', 'free', '{"show_recent": true}'),
('time_tracker', 'Lernzeit-Tracker', 'Lernzeit-Statistiken und Streak-Tracking', 'TimeTrackerWidget.vue', 'free', '{"show_streak": true, "show_daily": true}'),
('tasks', 'Aufgaben', 'To-Do Liste und Deadlines', 'TasksWidget.vue', 'free', '{"show_completed": false}'),

-- Analytics Widgets (Free+)
('score', 'Prüfungsergebnisse', 'Übersicht Prüfungsergebnisse mit Trendanalyse', 'ScoreWidget.vue', 'free', '{"show_trend": true, "show_history": 5}'),
('messages', 'Benachrichtigungen', 'System- und Community-Nachrichten', 'MessagesWidget.vue', 'free', '{"show_unread_only": true}'),
('theory_access', 'Theorie-Schnellzugriff', 'Schnellzugriff auf Theorieblätter', 'TheoryAccessWidget.vue', 'free', '{"show_recent": 5}'),

-- Premium Widgets (Premium+)
('ki_recommendations', 'KI-Empfehlungen', 'Personalisierte Kurs- und Lernempfehlungen', 'KIRecommendationsWidget.vue', 'premium', '{"max_recommendations": 5, "auto_refresh": true}'),
('token_status', 'Token-Status', 'Token-Guthaben und Verbrauchsstatistik', 'TokenStatusWidget.vue', 'premium', '{"show_history": true, "show_forecast": true}'),
('liveroom', 'LiveRoom', 'Schnellzugriff auf LiveRoom-Sessions', 'LiveRoomWidget.vue', 'premium', '{"show_active": true, "show_scheduled": true}'),
('groups', 'Gruppen', 'Private und Team-Lerngruppen', 'GroupsWidget.vue', 'premium', '{"show_activity": true}'),
('exam_simulator', 'Prüfungssimulator', 'Zugriff auf Prüfungssimulationen', 'ExamSimulatorWidget.vue', 'premium', '{"show_recent_results": true}'),
('ki_quick_panel', 'KI-Assistent', 'KI-Assistent Mini-Panel für schnelle Fragen', 'KIQuickPanelWidget.vue', 'premium', '{"show_history": false}'),

-- School/Organisation Widgets (School Admin+)
('calendar', 'Kalender', 'Termine und Deadlines', 'CalendarWidget.vue', 'school_admin', '{"show_upcoming": 7, "show_past": false}')

ON CONFLICT (widget_type) DO NOTHING;

-- ============================================================================
-- Verification
-- ============================================================================

SELECT COUNT(*) as total_dashboard_widgets FROM dashboards.widgets;
