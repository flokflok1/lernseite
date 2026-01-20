<template>
  <div :class="avatarClasses">
    <img
      v-if="src"
      :src="src"
      :alt="alt || name"
      class="avatar-image"
      @error="handleImageError"
    />
    <span v-else-if="name" class="avatar-initials">
      {{ initials }}
    </span>
    <svg v-else class="avatar-icon" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
    </svg>
    <span v-if="badge" :class="badgeClasses" :title="badgeTitle">
      {{ badge }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface Props {
  src?: string
  name?: string
  alt?: string
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'
  rounded?: boolean
  badge?: string | number
  badgeColor?: 'success' | 'warning' | 'danger' | 'info'
  badgeTitle?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  rounded: true,
  badgeColor: 'success',
})

const imageError = ref(false)

const initials = computed(() => {
  if (!props.name) return ''

  const parts = props.name.trim().split(' ')
  if (parts.length === 1) {
    return parts[0].substring(0, 2).toUpperCase()
  }

  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
})

const avatarClasses = computed(() => {
  return [
    'avatar',
    `avatar-${props.size}`,
    {
      'avatar-rounded': props.rounded,
      'avatar-square': !props.rounded,
    },
  ]
})

const badgeClasses = computed(() => {
  return [
    'avatar-badge',
    `badge-${props.badgeColor}`,
  ]
})

const handleImageError = () => {
  imageError.value = true
}
</script>

<style scoped>
.avatar {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-background-secondary);
  color: var(--color-text-primary);
  font-weight: 600;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar-rounded { border-radius: 9999px; }
.avatar-square { border-radius: 0.375rem; }

/* Sizes */
.avatar-xs {
  width: 1.5rem;
  height: 1.5rem;
  font-size: 0.625rem;
}

.avatar-sm {
  width: 2rem;
  height: 2rem;
  font-size: 0.75rem;
}

.avatar-md {
  width: 2.5rem;
  height: 2.5rem;
  font-size: 0.875rem;
}

.avatar-lg {
  width: 3rem;
  height: 3rem;
  font-size: 1rem;
}

.avatar-xl {
  width: 4rem;
  height: 4rem;
  font-size: 1.25rem;
}

.avatar-2xl {
  width: 5rem;
  height: 5rem;
  font-size: 1.5rem;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-initials {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
}

.avatar-icon {
  width: 60%;
  height: 60%;
  color: var(--color-text-secondary);
}

/* Badge */
.avatar-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  min-width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 0.25rem;
  border-radius: 9999px;
  font-size: 0.625rem;
  font-weight: 700;
  color: white;
  border: 2px solid white;
}

.badge-success { background-color: #10b981; }
.badge-warning { background-color: #f59e0b; }
.badge-danger { background-color: #ef4444; }
.badge-info { background-color: #3b82f6; }
</style>
