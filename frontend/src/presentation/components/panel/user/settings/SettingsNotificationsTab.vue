<script setup lang="ts">
import { ref } from 'vue'

const notifications = ref({
  emailCourseUpdate: true,
  emailWeeklySummary: true,
  emailPromotions: false,
  emailCommunity: true,
  pushNotifications: true
})
</script>

<template>
  <div class="settings__content">
    <h2>{{ $t('settings.notificationSettings') }}</h2>

    <div class="notifications-list">
      <div class="notification-item">
        <input
          id="email-course-update"
          v-model="notifications.emailCourseUpdate"
          type="checkbox"
        />
        <label for="email-course-update">
          <strong>{{ $t('notifications.courseUpdates') }}</strong>
          <p>{{ $t('notifications.courseUpdatesDesc') }}</p>
        </label>
      </div>

      <div class="notification-item">
        <input
          id="email-weekly-summary"
          v-model="notifications.emailWeeklySummary"
          type="checkbox"
        />
        <label for="email-weekly-summary">
          <strong>{{ $t('notifications.weeklySummary') }}</strong>
          <p>{{ $t('notifications.weeklySummaryDesc') }}</p>
        </label>
      </div>

      <div class="notification-item">
        <input
          id="email-promotions"
          v-model="notifications.emailPromotions"
          type="checkbox"
        />
        <label for="email-promotions">
          <strong>{{ $t('notifications.promotions') }}</strong>
          <p>{{ $t('notifications.promotionsDesc') }}</p>
        </label>
      </div>

      <div class="notification-item">
        <input
          id="email-community"
          v-model="notifications.emailCommunity"
          type="checkbox"
        />
        <label for="email-community">
          <strong>{{ $t('notifications.communityUpdates') }}</strong>
          <p>{{ $t('notifications.communityUpdatesDesc') }}</p>
        </label>
      </div>

      <div class="notification-item">
        <input
          id="push-notifications"
          v-model="notifications.pushNotifications"
          type="checkbox"
        />
        <label for="push-notifications">
          <strong>{{ $t('notifications.pushNotifications') }}</strong>
          <p>{{ $t('notifications.pushNotificationsDesc') }}</p>
        </label>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.settings__content {
  h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: var(--color-text-primary);
  }
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.notification-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-background-secondary);
  border-radius: 0.5rem;

  input[type='checkbox'] {
    margin-top: 0.25rem;
    cursor: pointer;
  }

  label {
    cursor: pointer;
    flex: 1;

    strong {
      display: block;
      color: var(--color-text-primary);
      margin-bottom: 0.25rem;
    }

    p {
      margin: 0;
      color: var(--color-text-secondary);
      font-size: 0.85rem;
    }
  }
}
</style>
