"""Tests for Plan domain value objects."""
import pytest
from app.domain.ai.models.plan import CourseMeta, ChapterDraft, PlanChatMessage, PlanData


class TestCourseMeta:
    def test_from_dict_valid(self):
        raw = {
            'title': 'Python Basics', 'description': 'Learn Python',
            'target_audience': 'Beginners', 'difficulty': 'beginner', 'language': 'de',
        }
        meta = CourseMeta.from_dict(raw)
        assert meta.title == 'Python Basics'
        assert meta.difficulty == 'beginner'
        assert meta.language == 'de'

    def test_from_dict_with_extras(self):
        raw = {
            'title': 'Advanced ML', 'description': 'Deep learning',
            'target_audience': 'Data Scientists', 'difficulty': 'advanced',
            'language': 'en', 'subtitle': 'Neural Networks',
            'prerequisites': ['Python', 'Math'], 'estimated_duration_hours': 40,
            'tags': ['ml', 'ai'],
        }
        meta = CourseMeta.from_dict(raw)
        assert meta.subtitle == 'Neural Networks'
        assert meta.prerequisites == ('Python', 'Math')
        assert meta.estimated_duration_hours == 40
        assert meta.tags == ('ml', 'ai')

    def test_from_dict_defaults(self):
        raw = {'title': 'T', 'description': 'D', 'target_audience': 'A', 'difficulty': 'beginner'}
        meta = CourseMeta.from_dict(raw)
        assert meta.language == 'de'
        assert meta.subtitle == ''
        assert meta.prerequisites == ()
        assert meta.estimated_duration_hours == 0
        assert meta.tags == ()

    def test_from_dict_invalid_difficulty(self):
        raw = {'title': 'T', 'description': 'D', 'target_audience': 'A', 'difficulty': 'banane'}
        with pytest.raises(ValueError, match='difficulty'):
            CourseMeta.from_dict(raw)

    def test_from_dict_empty_title(self):
        raw = {'title': '', 'description': 'D', 'target_audience': 'A', 'difficulty': 'beginner'}
        with pytest.raises(ValueError, match='title'):
            CourseMeta.from_dict(raw)

    def test_to_dict_roundtrip(self):
        raw = {'title': 'Python', 'description': 'Desc', 'target_audience': 'All',
               'difficulty': 'beginner', 'language': 'de'}
        meta = CourseMeta.from_dict(raw)
        result = meta.to_dict()
        assert result['title'] == 'Python'
        assert result['difficulty'] == 'beginner'
        assert isinstance(result, dict)
        # lists not tuples in output
        assert isinstance(result['prerequisites'], list)

    def test_frozen(self):
        meta = CourseMeta.from_dict({
            'title': 'T', 'description': 'D', 'target_audience': 'A', 'difficulty': 'beginner',
        })
        with pytest.raises(AttributeError):
            meta.title = 'Changed'


class TestChapterDraft:
    def test_from_dict_valid(self):
        raw = {'id': 'ch-1', 'title': 'Intro', 'description': 'Introduction', 'order': 1}
        chapter = ChapterDraft.from_dict(raw)
        assert chapter.id == 'ch-1'
        assert chapter.order == 1

    def test_from_dict_with_extras(self):
        raw = {
            'id': 'ch-1', 'title': 'Intro', 'description': 'Intro',
            'order': 1, 'estimated_lessons': 5, 'learning_goals': ['Goal 1'],
        }
        chapter = ChapterDraft.from_dict(raw)
        assert chapter.estimated_lessons == 5
        assert chapter.learning_goals == ('Goal 1',)

    def test_from_dict_invalid_order(self):
        raw = {'id': 'ch-1', 'title': 'Intro', 'description': 'Desc', 'order': 0}
        with pytest.raises(ValueError, match='order'):
            ChapterDraft.from_dict(raw)

    def test_to_dict_roundtrip(self):
        raw = {'id': 'ch-1', 'title': 'Intro', 'description': 'Desc', 'order': 1}
        chapter = ChapterDraft.from_dict(raw)
        result = chapter.to_dict()
        assert result == {
            'id': 'ch-1', 'title': 'Intro', 'description': 'Desc',
            'order': 1, 'estimated_lessons': 0, 'learning_goals': [],
        }


class TestPlanChatMessage:
    def test_from_dict_valid(self):
        msg = PlanChatMessage.from_dict({'role': 'user', 'content': 'Hello'})
        assert msg.role == 'user'
        assert msg.content == 'Hello'

    def test_from_dict_invalid_role(self):
        with pytest.raises(ValueError, match='role'):
            PlanChatMessage.from_dict({'role': 'system', 'content': 'X'})

    def test_to_dict(self):
        msg = PlanChatMessage.from_dict({'role': 'assistant', 'content': 'Hi', 'timestamp': '2026-01-01'})
        d = msg.to_dict()
        assert d == {'role': 'assistant', 'content': 'Hi', 'timestamp': '2026-01-01'}


class TestPlanData:
    def test_from_dict_valid(self):
        raw = {
            'course_meta': {
                'title': 'Python', 'description': 'D', 'target_audience': 'A',
                'difficulty': 'beginner',
            },
            'chapters': [
                {'id': 'ch-1', 'title': 'Intro', 'description': 'D', 'order': 1},
            ],
            'phases': [{'phase_id': 'p1', 'steps': []}],
        }
        pd = PlanData.from_dict(raw)
        assert isinstance(pd.course_meta, CourseMeta)
        assert len(pd.chapters) == 1
        assert isinstance(pd.chapters[0], ChapterDraft)

    def test_from_dict_empty(self):
        pd = PlanData.from_dict({})
        assert pd.course_meta is None
        assert pd.chapters == []
        assert pd.phases == []

    def test_to_dict_roundtrip(self):
        raw = {
            'course_meta': {
                'title': 'T', 'description': 'D', 'target_audience': 'A',
                'difficulty': 'beginner',
            },
            'chapters': [
                {'id': 'ch-1', 'title': 'C', 'description': 'D', 'order': 1},
            ],
            'phases': [],
        }
        pd = PlanData.from_dict(raw)
        result = pd.to_dict()
        assert result['course_meta']['title'] == 'T'
        assert len(result['chapters']) == 1
