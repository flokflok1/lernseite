<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const subscription = ref({
  tier: 'free' as 'free' | 'creator' | 'pro',
  nextBillingDate: '2024-03-01',
  autoRenew: true
})

const subscriptionOptions = computed(() => [
  {
    id: 'free',
    name: t('subscription.free'),
    price: t('subscription.priceFree'),
    features: [
      t('subscription.feature1'),
      t('subscription.feature2'),
      t('subscription.feature3')
    ]
  },
  {
    id: 'creator',
    name: t('subscription.creator'),
    price: '$9.99/mo',
    features: [
      t('subscription.feature1'),
      t('subscription.feature2'),
      t('subscription.feature3'),
      t('subscription.feature4')
    ]
  },
  {
    id: 'pro',
    name: t('subscription.pro'),
    price: '$19.99/mo',
    features: [
      t('subscription.feature1'),
      t('subscription.feature2'),
      t('subscription.feature3'),
      t('subscription.feature4'),
      t('subscription.feature5')
    ]
  }
])

function handleSubscriptionChange(tier: string): void {
  subscription.value.tier = tier as 'free' | 'creator' | 'pro'
  console.log('Changing subscription to:', tier)
}
</script>

<template>
  <div class="settings__content">
    <h2>{{ $t('settings.subscriptionSettings') }}</h2>

    <div class="subscription-info">
      <p>
        {{ $t('settings.currentPlan') }}:
        <strong>{{ subscription.tier.toUpperCase() }}</strong>
      </p>
      <p>
        {{ $t('settings.nextBillingDate') }}:
        <strong>{{ new Date(subscription.nextBillingDate).toLocaleDateString() }}</strong>
      </p>
    </div>

    <div class="subscription-plans">
      <div
        v-for="plan in subscriptionOptions"
        :key="plan.id"
        :class="['plan-card', { 'plan-card--active': subscription.tier === plan.id }]"
      >
        <h3>{{ plan.name }}</h3>
        <p class="plan-card__price">{{ plan.price }}</p>

        <ul class="plan-card__features">
          <li v-for="(feature, idx) in plan.features" :key="idx">
            &#x2713; {{ feature }}
          </li>
        </ul>

        <button
          :disabled="subscription.tier === plan.id"
          class="btn btn--primary"
          @click="handleSubscriptionChange(plan.id)"
        >
          {{
            subscription.tier === plan.id
              ? $t('subscription.current')
              : $t('subscription.upgrade')
          }}
        </button>
      </div>
    </div>

    <div class="auto-renew">
      <label>
        <input v-model="subscription.autoRenew" type="checkbox" />
        {{ $t('settings.autoRenew') }}
      </label>
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

.subscription-info {
  background: var(--color-background-secondary);
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin-bottom: 2rem;

  p {
    margin: 0.5rem 0;
    color: var(--color-text-primary);
  }

  strong {
    color: var(--color-primary);
  }
}

.subscription-plans {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.plan-card {
  padding: 1.5rem;
  border: 2px solid var(--color-border);
  border-radius: 0.5rem;
  transition: all 0.2s ease-in-out;

  &:hover {
    border-color: var(--color-primary);
  }

  &--active {
    border-color: var(--color-primary);
    background: rgba(var(--color-primary-rgb), 0.05);
  }

  h3 {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0 0 0.5rem 0;
  }

  &__price {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--color-primary);
    margin: 0 0 1rem 0;
  }

  &__features {
    list-style: none;
    padding: 0;
    margin: 0 0 1.5rem 0;

    li {
      padding: 0.5rem 0;
      color: var(--color-text-secondary);
      font-size: 0.9rem;
    }
  }
}

.auto-renew {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
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
