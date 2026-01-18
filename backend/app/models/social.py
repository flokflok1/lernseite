"""
Pydantic Models for Social Features

Models for API request/response validation
"""

from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Optional, List
from datetime import datetime


class PostCreate(BaseModel):
    """Create post request"""
    content: Optional[str] = Field(None, max_length=5000)
    content_type: str = Field('text', pattern='^(text|media|course_portfolio|achievement)$')
    visibility: str = Field('public', pattern='^(public|followers|private|unlisted)$')
    media_urls: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None

    @field_validator('content', 'media_urls', mode='after')
    @classmethod
    def content_or_media_required(cls, v, info: ValidationInfo):
        """Validate that post has either content or media"""
        # Access all field data via info.data
        data = info.data
        if not v and not data.get('media_urls'):
            raise ValueError('Post must have either content or media')
        return v


class PostUpdate(BaseModel):
    """Update post request"""
    content: Optional[str] = Field(None, max_length=5000)
    visibility: Optional[str] = Field(None, pattern='^(public|followers|private|unlisted)$')


class PostResponse(BaseModel):
    """Post response"""
    post_id: str
    user_id: str
    content: Optional[str]
    content_type: str
    visibility: str
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    is_pinned: bool = False
    created_at: datetime
    updated_at: datetime


class CommentCreate(BaseModel):
    """Create comment request"""
    content: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    """Comment response"""
    comment_id: str
    post_id: str
    user_id: str
    content: str
    likes_count: int = 0
    replies_count: int = 0
    thread_level: int = 0
    created_at: datetime


class ReactionRequest(BaseModel):
    """Add reaction request"""
    reaction_type: str = Field(
        ...,
        pattern='^(like|love|haha|wow|sad|angry|thinking|celebrate)$'
    )


class FollowStatsResponse(BaseModel):
    """Follow stats response"""
    followers_count: int
    following_count: int
    posts_count: int
    engagement_rate: Optional[float] = None
