"""Pure domain service mapping exam questions to Learning Method content structures."""

import hashlib
from typing import Dict, List

# Question type -> LM type IDs
QUESTION_TYPE_TO_LM: Dict[str, List[int]] = {
    'mcq': [6, 7],          # Flashcards, Drag & Drop
    'fill_blank': [8],       # Cloze Test
    'essay': [10],           # IHK-Style Tasks
    'calculation': [5],      # Math Interactive
    'code': [10],            # IHK-Style Tasks
    'case_study': [11],      # Multi-Step Practical
}

ALWAYS_INCLUDE = [0]  # Deep Explanation always added


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
    def select_lm_types(questions: List[Dict]) -> List[int]:
        """Pick 3-5 LM types based on question types present."""
        q_types = {q.get('question_type', '') for q in questions}
        lm_set = set(ALWAYS_INCLUDE)
        for qt in q_types:
            lm_set.update(QUESTION_TYPE_TO_LM.get(qt, []))
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
        """Fill-blank questions -> cloze sentences."""
        sentences = []
        for q in questions:
            if q.get('question_type') != 'fill_blank':
                continue
            data = q.get('data', {})
            for item in data.get('sentences', [data]):
                sentences.append({
                    'text': item.get('text', ''),
                    'answers': item.get('answers', [_extract_correct_answer(item)]),
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
        """Calculation questions -> math interactive problems."""
        problems = []
        for q in questions:
            if q.get('question_type') != 'calculation':
                continue
            data = q.get('data', {})
            for item in data.get('problems', [data]):
                problems.append({
                    'question': item.get('question', item.get('text', '')),
                    'answer': _extract_correct_answer(item),
                    'hint': item.get('hint', ''),
                    'source_question_id': q.get('question_id', ''),
                })
        return {'problems': problems}

    @staticmethod
    def map_to_ihk_tasks(questions: List[Dict]) -> Dict:
        """Essay/code/case_study questions -> IHK-style tasks."""
        tasks = []
        valid_types = {'essay', 'code', 'case_study'}
        for q in questions:
            qt = q.get('question_type', '')
            if qt not in valid_types:
                continue
            data = q.get('data', {})
            for item in data.get('tasks', [data]):
                tasks.append({
                    'question': item.get('question', item.get('text', '')),
                    'points': item.get('points', 0),
                    'solution': item.get('solution', _extract_correct_answer(item)),
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
