import { describe, it, expect } from 'vitest'
import { SubscriptionModel } from '../Subscription.model'

describe('SubscriptionModel', () => {
  describe('fromProfile', () => {
    it('creates from profile API data', () => {
      const sub = SubscriptionModel.fromProfile({
        subscription_plan: 'Premium',
        subscription_status: 'active',
        tokens_remaining: 5000,
        tokens_total: 10000,
        expires_at: '2026-12-31T23:59:59Z'
      })
      expect(sub.planName).toBe('Premium')
      expect(sub.status).toBe('active')
      expect(sub.tokensRemaining).toBe(5000)
      expect(sub.tokensTotal).toBe(10000)
      expect(sub.expiresAt).toBeInstanceOf(Date)
    })

    it('defaults to none status for invalid status', () => {
      const sub = SubscriptionModel.fromProfile({
        subscription_status: 'invalid_status'
      })
      expect(sub.status).toBe('none')
    })

    it('defaults planName to Free when not provided', () => {
      const sub = SubscriptionModel.fromProfile({})
      expect(sub.planName).toBe('Free')
    })

    it('handles plan_name fallback field', () => {
      const sub = SubscriptionModel.fromProfile({ plan_name: 'Enterprise' })
      expect(sub.planName).toBe('Enterprise')
    })

    it('handles token_balance fallback field', () => {
      const sub = SubscriptionModel.fromProfile({ token_balance: 3000 })
      expect(sub.tokensRemaining).toBe(3000)
    })
  })

  describe('free', () => {
    it('creates free-tier placeholder', () => {
      const sub = SubscriptionModel.free()
      expect(sub.planName).toBe('Free')
      expect(sub.status).toBe('none')
      expect(sub.tokensRemaining).toBe(0)
      expect(sub.tokensTotal).toBe(0)
      expect(sub.expiresAt).toBeNull()
    })
  })

  describe('status checks', () => {
    it('isActive for active status', () => {
      const sub = SubscriptionModel.fromProfile({ subscription_status: 'active' })
      expect(sub.isActive).toBe(true)
    })

    it('isActive for trial status', () => {
      const sub = SubscriptionModel.fromProfile({ subscription_status: 'trial' })
      expect(sub.isActive).toBe(true)
      expect(sub.isTrial).toBe(true)
    })

    it('not isActive for cancelled', () => {
      const sub = SubscriptionModel.fromProfile({ subscription_status: 'cancelled' })
      expect(sub.isActive).toBe(false)
    })

    it('isExpired for expired status', () => {
      const sub = SubscriptionModel.fromProfile({ subscription_status: 'expired' })
      expect(sub.isExpired).toBe(true)
    })

    it('isExpired when expiresAt is in the past', () => {
      const sub = SubscriptionModel.fromProfile({
        subscription_status: 'active',
        expires_at: '2020-01-01T00:00:00Z'
      })
      expect(sub.isExpired).toBe(true)
    })

    it('not isExpired when expiresAt is in the future', () => {
      const sub = SubscriptionModel.fromProfile({
        subscription_status: 'active',
        expires_at: '2099-12-31T23:59:59Z'
      })
      expect(sub.isExpired).toBe(false)
    })
  })

  describe('token logic', () => {
    it('isLowBalance when tokens < 1000', () => {
      const sub = SubscriptionModel.fromProfile({ tokens_remaining: 999 })
      expect(sub.isLowBalance).toBe(true)
    })

    it('not isLowBalance when tokens >= 1000', () => {
      const sub = SubscriptionModel.fromProfile({ tokens_remaining: 1000 })
      expect(sub.isLowBalance).toBe(false)
    })

    it('tokenUsagePercent calculates correctly', () => {
      const sub = SubscriptionModel.fromProfile({
        tokens_remaining: 7500,
        tokens_total: 10000
      })
      expect(sub.tokenUsagePercent).toBe(75)
    })

    it('tokenUsagePercent returns 0 for zero total', () => {
      const sub = SubscriptionModel.fromProfile({ tokens_total: 0 })
      expect(sub.tokenUsagePercent).toBe(0)
    })
  })

  describe('display helpers', () => {
    it('getStatusColor returns green for active', () => {
      const sub = SubscriptionModel.fromProfile({ subscription_status: 'active' })
      const color = sub.getStatusColor()
      expect(color.bg).toBe('bg-green-100')
      expect(color.text).toBe('text-green-800')
    })

    it('getStatusColor returns red for expired', () => {
      const sub = SubscriptionModel.fromProfile({ subscription_status: 'expired' })
      expect(sub.getStatusColor().bg).toBe('bg-red-100')
    })

    it('getBalanceColor returns red for < 1000', () => {
      const sub = SubscriptionModel.fromProfile({ tokens_remaining: 500 })
      expect(sub.getBalanceColor()).toBe('text-red-600')
    })

    it('getBalanceColor returns yellow for < 5000', () => {
      const sub = SubscriptionModel.fromProfile({ tokens_remaining: 3000 })
      expect(sub.getBalanceColor()).toBe('text-yellow-600')
    })

    it('getBalanceColor returns green for >= 5000', () => {
      const sub = SubscriptionModel.fromProfile({ tokens_remaining: 5000 })
      expect(sub.getBalanceColor()).toBe('text-green-600')
    })
  })

  describe('toJSON', () => {
    it('serializes all relevant fields', () => {
      const sub = SubscriptionModel.fromProfile({
        subscription_plan: 'Premium',
        subscription_status: 'active',
        tokens_remaining: 5000,
        tokens_total: 10000
      })
      const json = sub.toJSON()
      expect(json.planName).toBe('Premium')
      expect(json.isActive).toBe(true)
      expect(json.tokenUsagePercent).toBe(50)
    })
  })
})
