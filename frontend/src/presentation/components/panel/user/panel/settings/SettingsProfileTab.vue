<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface Props {
  initialName: string
  initialEmail: string
}

const props = defineProps<Props>()

const profileForm = ref({
  name: props.initialName,
  email: props.initialEmail,
  bio: '',
  avatar: null as File | null
})

const profileErrors = ref<Record<string, string>>({})

async function handleProfileSubmit(): Promise<void> {
  profileErrors.value = {}

  if (!profileForm.value.name) {
    profileErrors.value.name = t('validation.nameRequired')
  }

  if (!profileForm.value.email) {
    profileErrors.value.email = t('validation.emailRequired')
  }

  if (Object.keys(profileErrors.value).length === 0) {
    console.log('Updating profile:', profileForm.value)
  }
}
</script>

<template>
  <div class="settings__content">
    <h2>{{ $t('settings.profileSettings') }}</h2>

    <form class="form" @submit.prevent="handleProfileSubmit">
      <div class="form__group">
        <label for="name" class="form__label">{{ $t('form.name') }}</label>
        <input
          id="name"
          v-model="profileForm.name"
          type="text"
          class="form__input"
          :class="{ 'form__input--error': profileErrors.name }"
        />
        <span v-if="profileErrors.name" class="form__error">{{ profileErrors.name }}</span>
      </div>

      <div class="form__group">
        <label for="email" class="form__label">{{ $t('form.email') }}</label>
        <input
          id="email"
          v-model="profileForm.email"
          type="email"
          class="form__input"
          :class="{ 'form__input--error': profileErrors.email }"
        />
        <span v-if="profileErrors.email" class="form__error">{{ profileErrors.email }}</span>
      </div>

      <div class="form__group">
        <label for="bio" class="form__label">{{ $t('form.bio') }}</label>
        <textarea
          id="bio"
          v-model="profileForm.bio"
          rows="4"
          class="form__textarea"
          :placeholder="$t('form.bioPlaceholder')"
        ></textarea>
      </div>

      <div class="form__group">
        <label for="avatar" class="form__label">{{ $t('form.profilePicture') }}</label>
        <div class="file-upload">
          <input
            id="avatar"
            type="file"
            accept="image/*"
            class="file-upload__input"
            @change="profileForm.avatar = ($event.target as HTMLInputElement).files?.[0] || null"
          />
          <label for="avatar" class="file-upload__label">
            {{ profileForm.avatar ? profileForm.avatar.name : $t('form.chooseFile') }}
          </label>
        </div>
      </div>

      <div class="form__actions">
        <button type="submit" class="btn btn--primary">{{ $t('common.save') }}</button>
      </div>
    </form>
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

.form {
  max-width: 600px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;

  &__group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  &__label {
    font-weight: 500;
    color: var(--color-text-primary);
    font-size: 0.95rem;
  }

  &__input,
  &__textarea {
    padding: 0.75rem 1rem;
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    font-size: 0.95rem;
    background: var(--color-background-primary);
    color: var(--color-text-primary);
    font-family: inherit;

    &:focus {
      outline: none;
      border-color: var(--color-primary);
      box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
    }

    &--error {
      border-color: var(--color-error);
    }
  }

  &__textarea {
    resize: vertical;
    min-height: 120px;
  }

  &__error {
    color: var(--color-error);
    font-size: 0.85rem;
  }

  &__actions {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
  }
}

.file-upload {
  position: relative;

  &__input {
    display: none;
  }

  &__label {
    display: block;
    padding: 1rem;
    border: 2px dashed var(--color-border);
    border-radius: 0.5rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
    background: var(--color-background-secondary);

    &:hover {
      border-color: var(--color-primary);
      background: var(--color-background-primary);
    }
  }
}

.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease-in-out;

  &--primary {
    background: var(--color-primary);
    color: white;

    &:hover:not(:disabled) {
      background: var(--color-primary-hover);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
}
</style>
