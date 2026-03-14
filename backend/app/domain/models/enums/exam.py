"""
Exam domain enumerations
"""

from enum import Enum


class ExamType(str, Enum):
    """Exam types as defined in 04_Kurs-Architektur.md"""
    PRACTICE = "practice"
    AI_SIMULATION = "ai_simulation"
    FINAL = "final"


class ExamStandard(str, Enum):
    """Exam standards for AI generation — matches exam_type_registry keys."""
    FI_AP1 = "FI_AP1"
    FI_AP2_FISI = "FI_AP2_FISI"
    FI_AP2_FIAE = "FI_AP2_FIAE"
    COMPTIA_APLUS = "COMPTIA_APLUS_CORE1"
    COMPTIA_NETPLUS = "COMPTIA_NETPLUS_N10"
    AWS_SAA = "AWS_SAA_C03"
    CUSTOM = "Custom"


class QuestionType(str, Enum):
    """Question types"""
    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    FILL_BLANKS = "fill_blanks"
    MATCHING = "matching"
    SHORT_ANSWER = "short_answer"
    MATH_PROBLEM = "math_problem"
    CASE_QUESTION = "case_question"
