#!/bin/bash
# Wave 2: Create stub components for new feature domains

cd /home/pascal/Lernsystem/frontend/src/components

# Function to create a stub component
create_stub() {
  local domain=$1
  local component=$2
  local description=$3
  
  cat > "${domain}/${component}.vue" <<EOF
<template>
  <div class="${component,,}">
    <div class="coming-soon-container">
      <div class="icon">🚧</div>
      <h3>{{ \$t('common.comingSoon') }}</h3>
      <p class="component-name">${component}</p>
      <p class="description">${description}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ${component} Component (Stub)
 * ${description}
 * 
 * TODO: Implement full functionality in future phase
 * Created: Wave 2 - Feature Domain Stubs
 */

// Component will be implemented when social/compliance/moderation features are built
</script>

<style scoped>
.coming-soon-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 1rem;
  color: white;
  text-align: center;
  min-height: 300px;
}

.icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.coming-soon-container h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.component-name {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  opacity: 0.9;
}

.description {
  font-size: 0.875rem;
  opacity: 0.8;
  max-width: 500px;
}
</style>
EOF
  echo "✓ Created: ${domain}/${component}.vue"
}

echo "🚀 Creating Wave 2 stub components..."
echo ""

# SOCIAL (20 components)
echo "📱 Creating Social components..."
create_stub "social" "PostCard" "Display individual post with content and metadata"
create_stub "social" "PostComposer" "Create and edit new posts"
create_stub "social" "PostList" "List of posts in feed format"
create_stub "social" "CommentSection" "Display and manage post comments"
create_stub "social" "CommentInput" "Input field for writing comments"
create_stub "social" "LikeButton" "Like/unlike button with count"
create_stub "social" "ShareButton" "Share post functionality"
create_stub "social" "FollowButton" "Follow/unfollow user button"
create_stub "social" "FollowersList" "List of user followers"
create_stub "social" "FollowingList" "List of users being followed"
create_stub "social" "UserCard" "User profile card component"
create_stub "social" "UserBadge" "User achievement badge display"
create_stub "social" "HashtagChip" "Hashtag display chip"
create_stub "social" "MentionInput" "@mention autocomplete input"
create_stub "social" "TrendingCard" "Trending posts card"
create_stub "social" "SuggestedUsers" "User follow suggestions"
create_stub "social" "ActivityFeed" "User activity notification feed"
create_stub "social" "BookmarkButton" "Bookmark/save post button"
create_stub "social" "RepostButton" "Repost/share functionality"
create_stub "social" "PollCard" "Poll display and voting"

# COMPLIANCE (15 components)
echo "⚖️ Creating Compliance components..."
create_stub "compliance" "CookieConsent" "GDPR cookie consent banner"
create_stub "compliance" "CookieSettings" "Granular cookie preference controls"
create_stub "compliance" "AgeGate" "Age verification gate (COPPA)"
create_stub "compliance" "ParentalConsent" "Parental consent form for minors"
create_stub "compliance" "PrivacyDashboard" "User privacy settings dashboard"
create_stub "compliance" "DataExport" "GDPR data export functionality"
create_stub "compliance" "DataDeletion" "Right to erasure (GDPR Art. 17)"
create_stub "compliance" "ConsentManager" "Manage user consents"
create_stub "compliance" "ReportContent" "Report inappropriate content (DSA Art. 14)"
create_stub "compliance" "ReportStatus" "Track content report status"
create_stub "compliance" "ContentWarning" "Content warning overlay"
create_stub "compliance" "SafeMode" "Child-safe mode toggle"
create_stub "compliance" "ParentalControls" "Parental control dashboard"
create_stub "compliance" "ScreenTimeWidget" "Usage time tracking widget"
create_stub "compliance" "TransparencyReport" "Public transparency reports"

# MODERATION (8 components)
echo "🛡️ Creating Moderation components..."
create_stub "moderation" "ModerationQueue" "Content review queue"
create_stub "moderation" "ContentReview" "Single content review interface"
create_stub "moderation" "ReportDetails" "Detailed report view"
create_stub "moderation" "ModerationActions" "Moderation action buttons"
create_stub "moderation" "UserHistory" "User violation history"
create_stub "moderation" "ModerationStats" "Moderation statistics dashboard"
create_stub "moderation" "SLAMonitor" "24h/7d deadline tracker (DSA)"
create_stub "moderation" "AppealReview" "Appeal review interface (DSA Art. 17)"

# SECURITY (6 components)
echo "🔒 Creating Security components..."
create_stub "security" "TwoFactorAuth" "2FA setup and management"
create_stub "security" "SessionManager" "Active sessions management"
create_stub "security" "SecurityLog" "Security event log viewer"
create_stub "security" "DRMLicenseDisplay" "DRM license information"
create_stub "security" "Watermark" "Visible content watermark"
create_stub "security" "AccessGate" "DRM access control gate"

# FEATURE-FLAGS (4 components)
echo "🎚️ Creating Feature Flag components..."
create_stub "feature-flags" "FeatureGate" "Feature flag wrapper component"
create_stub "feature-flags" "FeatureFlagBadge" "Beta/preview badge"
create_stub "feature-flags" "RolloutProgress" "Feature rollout statistics"
create_stub "feature-flags" "ABTestBanner" "A/B test information banner"

echo ""
echo "✅ All 53 stub components created!"
