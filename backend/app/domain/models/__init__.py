"""
LernsystemX Models Package

Provides Pydantic models for data validation and serialization:
- User models (registration, login, profile)
- Course models (create, update, enrollment)
- Organisation models (setup, management)
- Learning method models (configuration)

Uses Pydantic for:
- Request validation
- Response serialization
- Type safety
- Data transformation

ISO 9001:2015 compliant - Data modeling standards
"""

from app.domain.models.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserLogin,
    UserResponse,
    UserProfile,
    PasswordChange,
    EmailVerification,
    TwoFactorSetup
)

from app.domain.models.content.course import (
    CourseBase,
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    CourseListResponse,
    ModuleBase,
    ModuleCreate,
    ModuleUpdate,
    EnrollmentCreate
)

from app.domain.models.schemas.organisation import (
    OrganisationBase,
    OrganisationCreate,
    OrganisationUpdate,
    OrganisationResponse,
    BrandingConfig,
    OrganisationSettings
)

from app.domain.models.content.learning_method import (
    LearningMethodBase,
    LearningMethodCreate,
    LearningMethodUpdate,
    LearningMethodResponse,
    LearningMethodConfig
)

from app.domain.models.curriculum import (
    CurriculumObjective,
    CurriculumPosition,
    CurriculumSection,
    CurriculumFramework
)

__all__ = [
    # User models
    'UserBase',
    'UserCreate',
    'UserUpdate',
    'UserLogin',
    'UserResponse',
    'UserProfile',
    'PasswordChange',
    'EmailVerification',
    'TwoFactorSetup',

    # Course models
    'CourseBase',
    'CourseCreate',
    'CourseUpdate',
    'CourseResponse',
    'CourseListResponse',
    'ModuleBase',
    'ModuleCreate',
    'ModuleUpdate',
    'EnrollmentCreate',

    # Organisation models
    'OrganisationBase',
    'OrganisationCreate',
    'OrganisationUpdate',
    'OrganisationResponse',
    'BrandingConfig',
    'OrganisationSettings',

    # Learning method models
    'LearningMethodBase',
    'LearningMethodCreate',
    'LearningMethodUpdate',
    'LearningMethodResponse',
    'LearningMethodConfig',

    # Curriculum models
    'CurriculumObjective',
    'CurriculumPosition',
    'CurriculumSection',
    'CurriculumFramework',
]
