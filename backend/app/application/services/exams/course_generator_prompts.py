"""
Course Generator Prompts — KI-Prompt Templates.

Separated from service logic per G07 (no hardcoded AI config inline).
"""
from typing import List, Dict


def build_deep_explanation_prompt(topic: str, questions: List[Dict]) -> str:
    """Build prompt for Deep Explanation (LM00) content generation."""
    topic_label = topic.replace('_', ' ').title()

    # Extract sample questions for context
    sample_texts = []
    for q in questions[:8]:
        text = q.get('question_text', '')[:200]
        if text:
            sample_texts.append(f"- {text}")
    samples = '\n'.join(sample_texts)

    return f"""Du bist ein erfahrener IT-Dozent fuer IHK-Pruefungsvorbereitung.

Erstelle eine ausfuehrliche Erklaerung zum Thema "{topic_label}" fuer die IHK Fachinformatiker AP1 Pruefung.

## Kontext: Echte Pruefungsaufgaben zu diesem Thema
{samples}

## Anforderungen:
1. Erklaere das Thema von Grund auf — stelle dir einen Azubi im 2. Lehrjahr vor
2. Verwende konkrete Beispiele aus der IT-Praxis
3. Beziehe dich auf typische IHK-Pruefungsaufgaben
4. Strukturiere mit Ueberschriften (## und ###)
5. Nutze Aufzaehlungen und Tabellen wo sinnvoll
6. Laenge: 800-1500 Woerter
7. Sprache: Deutsch, fachlich korrekt aber verstaendlich

## Ausgabeformat:
Markdown-Text (kein JSON, kein Code-Block drumherum).
Beginne direkt mit der Erklaerung."""


def build_step_by_step_prompt(topic: str, questions: List[Dict]) -> str:
    """Build prompt for Step-by-Step (LM01) content generation."""
    topic_label = topic.replace('_', ' ').title()

    # Find calculation or complex questions for step-by-step
    complex_qs = [
        q for q in questions
        if q.get('question_type') in ('calculation', 'code', 'case_study')
    ][:5]

    if not complex_qs:
        complex_qs = questions[:5]

    examples = []
    for q in complex_qs:
        text = q.get('question_text', '')[:300]
        solution = q.get('solution_text', '')[:200]
        examples.append(f"Aufgabe: {text}\nLoesungshinweis: {solution}")
    examples_text = '\n\n'.join(examples)

    return f"""Du bist ein erfahrener IT-Dozent.

Erstelle eine Schritt-fuer-Schritt Anleitung zum Thema "{topic_label}" fuer die IHK AP1 Pruefung.

## Beispiel-Aufgaben aus echten Pruefungen:
{examples_text}

## Anforderungen:
1. Zeige den Loesungsweg Schritt fuer Schritt
2. Erklaere WARUM jeder Schritt notwendig ist
3. Nutze nummerierte Schritte (1., 2., 3. ...)
4. Bei Berechnungen: zeige Zwischenergebnisse
5. Bei Code/SQL: zeige Teilloesungen die aufeinander aufbauen
6. Gib am Ende Tipps fuer die Pruefung
7. Laenge: 600-1000 Woerter

## Ausgabeformat:
Markdown-Text. Beginne direkt mit der Anleitung."""
