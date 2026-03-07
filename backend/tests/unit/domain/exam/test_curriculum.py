"""Tests for curriculum framework domain models."""

import pytest

from app.domain.models.curriculum import (
    CurriculumFramework,
    CurriculumObjective,
    CurriculumPosition,
    CurriculumSection,
)


class TestCurriculumObjective:
    """Tests for CurriculumObjective value object."""

    def test_from_dict_valid(self):
        data = {
            'id': 1,
            'objective_code': 'OBJ-01',
            'description': {'de': 'Beschreibung', 'en': 'Description'},
            'order_index': 2,
            'competency_level': 'anwenden',
        }
        obj = CurriculumObjective.from_dict(data)
        assert obj.id == 1
        assert obj.objective_code == 'OBJ-01'
        assert obj.description == {'de': 'Beschreibung', 'en': 'Description'}
        assert obj.order_index == 2
        assert obj.competency_level == 'anwenden'

    def test_invalid_competency_defaults_to_none(self):
        data = {
            'id': 2,
            'objective_code': 'OBJ-02',
            'competency_level': 'invalid_level',
        }
        obj = CurriculumObjective.from_dict(data)
        assert obj.competency_level is None

    def test_immutable(self):
        obj = CurriculumObjective.from_dict({
            'id': 1,
            'objective_code': 'OBJ-01',
        })
        with pytest.raises(AttributeError):
            obj.id = 99

    def test_roundtrip(self):
        data = {
            'id': 3,
            'objective_code': 'OBJ-03',
            'description': {'de': 'Test'},
            'order_index': 1,
            'competency_level': 'kennen',
        }
        obj = CurriculumObjective.from_dict(data)
        result = obj.to_dict()
        assert result == data
        obj2 = CurriculumObjective.from_dict(result)
        assert obj == obj2


class TestCurriculumPosition:
    """Tests for CurriculumPosition value object."""

    def test_from_dict_with_objectives(self):
        data = {
            'id': 10,
            'position_number': '1.1',
            'display_name': {'de': 'Position 1.1'},
            'description': {'de': 'Beschreibung'},
            'order_index': 0,
            'training_period': '1. Ausbildungsjahr',
            'objectives': [
                {'id': 1, 'objective_code': 'OBJ-01', 'competency_level': 'kennen'},
                {'id': 2, 'objective_code': 'OBJ-02', 'competency_level': 'beherrschen'},
            ],
        }
        pos = CurriculumPosition.from_dict(data)
        assert pos.id == 10
        assert pos.position_number == '1.1'
        assert len(pos.objectives) == 2
        assert isinstance(pos.objectives, tuple)
        assert pos.objectives[0].objective_code == 'OBJ-01'
        assert pos.objectives[1].competency_level == 'beherrschen'

    def test_roundtrip(self):
        data = {
            'id': 10,
            'position_number': '2.3',
            'display_name': {'de': 'Pos'},
            'description': {},
            'order_index': 5,
            'training_period': None,
            'objectives': [
                {
                    'id': 1,
                    'objective_code': 'A',
                    'description': {},
                    'order_index': 0,
                    'competency_level': 'anwenden',
                },
            ],
        }
        pos = CurriculumPosition.from_dict(data)
        result = pos.to_dict()
        assert result == data


class TestCurriculumSection:
    """Tests for CurriculumSection value object."""

    def test_applies_to(self):
        data = {
            'id': 100,
            'section_code': 'SEC-A',
            'display_name': {'de': 'Abschnitt A'},
            'applies_to': ['Teil1', 'Teil2'],
            'positions': [],
        }
        sec = CurriculumSection.from_dict(data)
        assert sec.applies_to == ('Teil1', 'Teil2')
        assert isinstance(sec.applies_to, tuple)

    def test_applies_to_none(self):
        data = {
            'id': 101,
            'section_code': 'SEC-B',
            'applies_to': None,
        }
        sec = CurriculumSection.from_dict(data)
        assert sec.applies_to == ()


class TestCurriculumFramework:
    """Tests for CurriculumFramework root aggregate."""

    def test_invalid_type_defaults_to_custom(self):
        data = {
            'id': 1,
            'name': 'Test Framework',
            'framework_type': 'unknown_type',
        }
        fw = CurriculumFramework.from_dict(data)
        assert fw.framework_type == 'custom'

    def test_full_hierarchy(self):
        data = {
            'id': 1,
            'name': 'IHK Fachinformatiker',
            'framework_type': 'ihk_ausbildung',
            'source_document': 'IHK-Rahmenplan-2024.pdf',
            'version': '2024',
            'valid_from': '2024-08-01',
            'valid_until': None,
            'metadata': {'region': 'NRW'},
            'sections': [
                {
                    'id': 10,
                    'section_code': 'SEC-1',
                    'display_name': {'de': 'Abschnitt 1'},
                    'description': {},
                    'order_index': 0,
                    'applies_to': ['Teil1'],
                    'positions': [
                        {
                            'id': 100,
                            'position_number': '1.1',
                            'display_name': {'de': 'Position 1.1'},
                            'description': {},
                            'order_index': 0,
                            'training_period': '1. Jahr',
                            'objectives': [
                                {
                                    'id': 1000,
                                    'objective_code': 'OBJ-001',
                                    'description': {'de': 'Lernziel 1'},
                                    'order_index': 0,
                                    'competency_level': 'kennen',
                                },
                            ],
                        },
                    ],
                },
            ],
        }
        fw = CurriculumFramework.from_dict(data)
        assert fw.name == 'IHK Fachinformatiker'
        assert fw.framework_type == 'ihk_ausbildung'
        assert len(fw.sections) == 1
        assert len(fw.sections[0].positions) == 1
        assert len(fw.sections[0].positions[0].objectives) == 1
        assert fw.sections[0].positions[0].objectives[0].competency_level == 'kennen'

        # Roundtrip
        result = fw.to_dict()
        assert result == data

    def test_to_prompt_context(self):
        data = {
            'id': 1,
            'name': 'Test FW',
            'framework_type': 'ihk_ausbildung',
            'sections': [
                {
                    'id': 10,
                    'section_code': 'A',
                    'display_name': {'de': 'Abschnitt A', 'en': 'Section A'},
                    'positions': [
                        {
                            'id': 100,
                            'position_number': '1.1',
                            'objectives': [
                                {'id': 1, 'objective_code': 'O1'},
                                {'id': 2, 'objective_code': 'O2'},
                            ],
                        },
                        {
                            'id': 101,
                            'position_number': '1.2',
                            'objectives': [],
                        },
                    ],
                },
                {
                    'id': 11,
                    'section_code': 'B',
                    'display_name': {'de': 'Abschnitt B'},
                    'positions': [],
                },
            ],
        }
        fw = CurriculumFramework.from_dict(data)
        ctx = fw.to_prompt_context(language='de')
        assert ctx['curriculum_name'] == 'Test FW'
        assert ctx['framework_type'] == 'ihk_ausbildung'
        assert ctx['section_count'] == 2
        assert ctx['section_names_csv'] == 'Abschnitt A, Abschnitt B'
        assert ctx['total_positions'] == 2
        assert ctx['total_objectives'] == 2
        assert ctx['has_curriculum'] is True

    def test_to_prompt_context_language_fallback(self):
        data = {
            'id': 1,
            'name': 'FW',
            'sections': [
                {
                    'id': 10,
                    'section_code': 'X',
                    'display_name': {'de': 'Deutsch'},
                    'positions': [],
                },
            ],
        }
        fw = CurriculumFramework.from_dict(data)
        ctx = fw.to_prompt_context(language='en')
        # Falls back to 'de' since 'en' not present
        assert ctx['section_names_csv'] == 'Deutsch'
