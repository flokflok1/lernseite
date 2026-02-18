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
    """Exam standards for AI generation (09_KI-Pipeline.md:1032-1040)"""
    IHK_FISI_AP1 = "IHK_FISI_AP1"
    IHK_FIAE_AP1 = "IHK_FIAE_AP1"
    COMPTIA_A_PLUS = "CompTIA_A+"
    COMPTIA_NETWORK_PLUS = "CompTIA_Network+"
    ABITUR_INFORMATIK = "Abitur_Informatik"
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
