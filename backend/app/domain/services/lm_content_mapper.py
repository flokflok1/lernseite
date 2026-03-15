"""Pure domain service mapping exam questions to Learning Method content structures."""

import hashlib
from typing import Dict, List

# Question type -> LM type IDs (general learning context)
QUESTION_TYPE_TO_LM: Dict[str, List[int]] = {
    'mcq': [6, 7],          # Flashcards, Drag & Drop
    'fill_blank': [8],       # Cloze Test
    'essay': [10],           # IHK-Style Tasks
    'calculation': [5],      # Math Interactive
    'code': [10],            # IHK-Style Tasks
    'case_study': [11],      # Multi-Step Practical
}

# Exam prep context: Active Recall > passive recognition.
# MCQ as IHK-Tasks (active answering) + Cloze (fill-in recall),
# NOT Flashcards (passive recognition) or Drag & Drop (matching).
EXAM_QUESTION_TYPE_TO_LM: Dict[str, List[int]] = {
    'mcq': [10, 8],          # IHK-Tasks (active), Cloze (recall)
    'fill_blank': [8],       # Cloze Test
    'essay': [10],           # IHK-Style Tasks
    'calculation': [5, 10],  # Math Interactive + IHK-Tasks
    'code': [10],            # IHK-Style Tasks
    'case_study': [11, 10],  # Multi-Step + IHK-Tasks
}

ALWAYS_INCLUDE = [0]  # Deep Explanation always added

# LM type -> i18n display label (domain knowledge about method names)
LM_TYPE_LABELS: Dict[int, Dict[str, str]] = {
    0: {'de': 'Erklärung', 'en': 'Explanation'},
    1: {'de': 'Schritt für Schritt', 'en': 'Step by Step'},
    5: {'de': 'Rechenaufgaben', 'en': 'Math Exercises'},
    6: {'de': 'Lernkarten', 'en': 'Flashcards'},
    7: {'de': 'Zuordnung', 'en': 'Matching'},
    8: {'de': 'Lückentext', 'en': 'Cloze Test'},
    10: {'de': 'IHK-Prüfungsaufgaben', 'en': 'Exam Tasks'},
    11: {'de': 'Fallstudien', 'en': 'Case Studies'},
}


def get_lm_label(lm_type: int, language: str = 'de') -> str:
    """Get display label for an LM type in the given language."""
    labels = LM_TYPE_LABELS.get(lm_type, {})
    return labels.get(language, labels.get('de', f'Methode {lm_type}'))


def _extract_correct_answer(item: Dict) -> str:
    """Extract the correct answer from a question item's options or answer field."""
    if 'answer' in item:
        return str(item['answer'])
    options = item.get('options', [])
    for opt in options:
        if isinstance(opt, dict) and opt.get('correct'):
            return opt.get('text', '')
    return ''


class LMContentMapper:
    """Maps exam questions to Learning Method content structures."""

    @staticmethod
    def select_lm_types(
        questions: List[Dict], exam_mode: bool = False,
    ) -> List[int]:
        """Pick 3-5 LM types based on question types present.

        When exam_mode=True, prioritises Active Recall methods
        (IHK-Tasks, Cloze, Math) over passive recognition (Flashcards,
        Drag & Drop). Based on testing-effect research: retrieval
        practice produces stronger long-term retention than re-study.
        """
        q_types = {q.get('question_type', '') for q in questions}
        mapping = EXAM_QUESTION_TYPE_TO_LM if exam_mode else QUESTION_TYPE_TO_LM
        lm_set = set(ALWAYS_INCLUDE)
        for qt in q_types:
            lm_set.update(mapping.get(qt, []))
        result = sorted(lm_set)
        if len(result) > 5:
            result = sorted(ALWAYS_INCLUDE) + sorted(lm_set - set(ALWAYS_INCLUDE))[:4]
        return result

    @staticmethod
    def question_hash(question_id: str) -> str:
        """SHA-256 hash of a question ID."""
        return hashlib.sha256(question_id.encode('utf-8')).hexdigest()

    @staticmethod
    def map_to_flashcards(questions: List[Dict]) -> Dict:
        """MCQ questions -> flashcard cards."""
        cards = []
        for q in questions:
            if q.get('question_type') != 'mcq':
                continue
            data = q.get('data', {})
            for item in data.get('questions', [data]):
                cards.append({
                    'front': item.get('question', item.get('text', '')),
                    'back': _extract_correct_answer(item),
                    'source_question_id': q.get('question_id', ''),
                })
        return {'cards': cards}

    @staticmethod
    def map_to_cloze(questions: List[Dict]) -> Dict:
        """Fill-blank questions -> cloze sentences.

        Two formats:
        - Multi-sentence: data.sentences[] with per-item text + answers
        - Single-sentence: question_text at question level
        """
        sentences = []
        for q in questions:
            if q.get('question_type') != 'fill_blank':
                continue
            data = q.get('data', {})
            sub_sentences = data.get('sentences')

            if sub_sentences:
                for item in sub_sentences:
                    sentences.append({
                        'text': item.get('text', ''),
                        'answers': item.get('answers', [_extract_correct_answer(item)]),
                        'source_question_id': q.get('question_id', ''),
                    })
            else:
                # Single sentence: build from question_text + answer
                sentences.append({
                    'text': q.get('question_text', ''),
                    'answers': [_extract_correct_answer(data)],
                    'source_question_id': q.get('question_id', ''),
                })
        return {'sentences': sentences}

    @staticmethod
    def map_to_drag_drop(questions: List[Dict]) -> Dict:
        """MCQ assignment questions -> drag-and-drop pairs."""
        pairs = []
        for q in questions:
            if q.get('question_type') != 'mcq':
                continue
            data = q.get('data', {})
            for item in data.get('questions', [data]):
                pairs.append({
                    'question': item.get('question', item.get('text', '')),
                    'answer': _extract_correct_answer(item),
                    'source_question_id': q.get('question_id', ''),
                })
        return {'pairs': pairs}

    @staticmethod
    def map_to_math_interactive(questions: List[Dict]) -> Dict:
        """Calculation questions -> math interactive problems.

        Two question formats exist:
        - Multi-problem: data.problems[] array with per-item question text
        - Single-problem: question_text at question level, no sub-items

        Results are sorted by scenario_title so the frontend can group
        all problems of the same scenario together.
        """
        problems = []
        for q in questions:
            if q.get('question_type') != 'calculation':
                continue
            shared = {
                'scenario_title': q.get('scenario_title') or '',
                'scenario_text': q.get('scenario_text') or '',
                'points': float(q.get('points', 0) or 0),
                'source_question_id': q.get('question_id', ''),
            }
            data = q.get('data', {})
            sub_problems = data.get('problems')

            if sub_problems:
                # Multi-problem: each sub-item has its own question text
                for item in sub_problems:
                    problems.append({
                        'question': item.get('question', item.get('text', '')),
                        'answer': _extract_correct_answer(item),
                        'hint': item.get('hint', ''),
                        **shared,
                    })
            else:
                # Single-problem: question text lives at question level
                problems.append({
                    'question': q.get('question_text', ''),
                    'answer': _extract_correct_answer(data),
                    'hint': data.get('hint', ''),
                    **shared,
                })

        problems.sort(key=lambda p: p['scenario_title'])
        return {'problems': problems}

    @staticmethod
    def map_to_ihk_tasks(
        questions: List[Dict], include_mcq: bool = False,
    ) -> Dict:
        """Essay/code/case_study questions -> IHK-style tasks.

        Two question formats:
        - Multi-item: data contains tasks/questions/problems sub-array
        - Single-item: question_text at question level, data has solution only

        When include_mcq=True (exam prep mode), also converts MCQ
        questions into active-recall tasks.
        """
        tasks = []
        valid_types = {'essay', 'code', 'case_study'}
        if include_mcq:
            valid_types.update({'mcq', 'fill_blank', 'calculation'})
        for q in questions:
            qt = q.get('question_type', '')
            if qt not in valid_types:
                continue
            data = q.get('data', {})
            sub_items = (
                data.get('tasks')
                or data.get('questions')
                or data.get('problems')
            )

            if sub_items:
                # Multi-item: each sub-item has its own question text
                for item in sub_items:
                    q_text = item.get('question') or item.get('text', '')
                    if not q_text:
                        continue
                    tasks.append({
                        'question': q_text,
                        'points': item.get('points', q.get('points', 0)),
                        'solution': item.get('solution', item.get('answer', _extract_correct_answer(item))),
                        'question_type': qt,
                        'source_question_id': q.get('question_id', ''),
                    })
            else:
                # Single-item: question text at question level
                q_text = q.get('question_text', '')
                if not q_text:
                    continue
                tasks.append({
                    'question': q_text,
                    'points': q.get('points', 0),
                    'solution': data.get('solution', data.get('answer', _extract_correct_answer(data))),
                    'question_type': qt,
                    'source_question_id': q.get('question_id', ''),
                })
        return {'tasks': tasks}

    @staticmethod
    def map_to_multi_step(questions: List[Dict]) -> Dict:
        """Case study questions -> multi-step practical steps."""
        steps = []
        for q in questions:
            if q.get('question_type') != 'case_study':
                continue
            data = q.get('data', {})
            steps.append({
                'scenario': data.get('scenario', data.get('text', '')),
                'questions': data.get('questions', []),
                'source_question_id': q.get('question_id', ''),
            })
        return {'steps': steps}
