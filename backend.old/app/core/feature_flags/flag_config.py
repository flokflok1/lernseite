"""
Feature Flag Configuration - Default State

All flags listed here with their initial state.
Based on Dark Launch Strategy: Build 100%, Enable 0% (gradually)

Status Legend:
- False: Not enabled (0% rollout)
- True: Enabled globally
- 'beta': Enabled for beta users only
- {'percentage': N}: Percentage-based rollout
"""

FEATURE_FLAGS = {
    # ===== SOCIAL CORE =====
    'user_posts': False,              # User can create posts
    'feed_system': False,             # Personalized feed generation
    'follow_system': False,           # Follow/Unfollow users
    'likes_reactions': False,         # Like/React to content
    'comments': True,                 # Comments (partially enabled for courses)
    'shares': False,                  # Share/Repost content
    'bookmarks': False,               # Save posts for later
    
    # ===== DISCOVERY =====
    'trending_discovery': False,      # Trending page
    'hashtags': False,                # Hashtag system
    'mentions': False,                # @mentions system
    'explore_page': False,            # Explore feed
    
    # ===== MESSAGING =====
    'direct_messages': False,         # 1-on-1 DMs
    'group_chat': True,               # Group chat (already enabled for study groups)
    
    # ===== ADVANCED SOCIAL =====
    'stories': False,                 # Instagram-style stories
    'live_streams': False,            # Live streaming
    'polls': False,                   # Poll posts
    
    # ===== MODERATION FEATURES =====
    'ai_moderation': True,            # AI pre-screening (always on)
    'human_moderation': False,        # Human review queue
    'community_moderation': False,    # Community reporting
    
    # ===== ANALYTICS =====
    'social_analytics': False,        # Post analytics for users
    'audience_insights': False,       # Follower demographics
    
    # ===== COMPLIANCE FEATURES =====
    'dsa_transparency': False,        # DSA transparency features
    'netzdg_reporting': False,        # NetzDG reporting system
    'child_safety_strict': True,      # Child safety (always on)
    
    # ===== DRM FEATURES =====
    'drm_protection': False,          # DRM content protection
    'watermarking': False,            # Forensic watermarking
    'license_management': False,      # License validation
    
    # ===== GDPR FEATURES =====
    'gdpr_consent': True,             # GDPR consent management (always on)
    'data_portability': False,        # GDPR Art. 20 data export
    'right_to_erasure': False,        # GDPR Art. 17 deletion
}


def get_feature_flag_status(feature_name: str) -> dict:
    """
    Get detailed status of a feature flag

    Returns:
        dict: {
            'name': str,
            'default_state': bool,
            'description': str
        }
    """
    descriptions = {
        'user_posts': 'Users can create text/media posts on their profile',
        'feed_system': 'Personalized algorithmic feed generation',
        'follow_system': 'Follow/unfollow other users, followers list',
        'likes_reactions': 'Like and react to posts, comments, content',
        'comments': 'Comment system (partially enabled for course discussions)',
        'shares': 'Share/repost content to own feed',
        'bookmarks': 'Save posts/content for later',
        'trending_discovery': 'Trending content discovery page',
        'hashtags': 'Hashtag tagging and search',
        'mentions': '@mention users in posts and comments',
        'explore_page': 'Explore feed with recommended content',
        'direct_messages': '1-on-1 direct messaging',
        'group_chat': 'Group chat rooms (enabled for study groups)',
        'stories': 'Instagram-style ephemeral stories',
        'live_streams': 'Live video streaming',
        'polls': 'Poll posts and voting',
        'ai_moderation': 'AI-powered content pre-screening (DSA compliance)',
        'human_moderation': 'Human review queue for reported content',
        'community_moderation': 'Community-driven content reporting',
        'social_analytics': 'Post performance analytics for users',
        'audience_insights': 'Follower demographics and insights',
        'dsa_transparency': 'DSA-mandated transparency features',
        'netzdg_reporting': 'NetzDG-compliant illegal content reporting',
        'child_safety_strict': 'Child safety features (COPPA, age verification)',
        'drm_protection': 'DRM content protection (Denuvo-style)',
        'watermarking': 'Forensic watermarking for content',
        'license_management': 'License validation and management',
        'gdpr_consent': 'GDPR consent management',
        'data_portability': 'GDPR Art. 20 data export',
        'right_to_erasure': 'GDPR Art. 17 right to deletion',
    }

    return {
        'name': feature_name,
        'default_state': FEATURE_FLAGS.get(feature_name, False),
        'description': descriptions.get(feature_name, 'No description available')
    }


def get_all_feature_flags() -> dict:
    """Get all feature flags with descriptions"""
    return {
        name: get_feature_flag_status(name)
        for name in FEATURE_FLAGS.keys()
    }


# Feature flag groups for batch operations
FEATURE_GROUPS = {
    'social_core': [
        'user_posts', 'feed_system', 'follow_system',
        'likes_reactions', 'comments', 'shares', 'bookmarks'
    ],
    'discovery': [
        'trending_discovery', 'hashtags', 'mentions', 'explore_page'
    ],
    'messaging': [
        'direct_messages', 'group_chat'
    ],
    'advanced_social': [
        'stories', 'live_streams', 'polls'
    ],
    'moderation': [
        'ai_moderation', 'human_moderation', 'community_moderation'
    ],
    'analytics': [
        'social_analytics', 'audience_insights'
    ],
    'compliance': [
        'dsa_transparency', 'netzdg_reporting', 'child_safety_strict',
        'gdpr_consent', 'data_portability', 'right_to_erasure'
    ],
    'drm': [
        'drm_protection', 'watermarking', 'license_management'
    ]
}


def get_feature_group(group_name: str) -> list:
    """Get all feature flags in a group"""
    return FEATURE_GROUPS.get(group_name, [])
