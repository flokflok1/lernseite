/**
 * Subscription Domain Model
 *
 * Encapsulates subscription state and token balance logic.
 * Extracts business rules from widget components (PlanTokensWidget, etc.)
 *
 * Data source: ProfileResponse in infrastructure/api/clients/panel/user/types.ts
 *
 * Example:
 *   const sub = SubscriptionModel.fromProfile(profileData)
 *   sub.isActive           // true if status is 'active' or 'trial'
 *   sub.tokenUsagePercent  // 0-100
 *   sub.getStatusColor()   // { bg, text } Tailwind classes
 */

export type SubscriptionStatus = 'active' | 'trial' | 'cancelled' | 'expired' | 'none'

export class SubscriptionModel {
  constructor(
    public readonly planName: string,
    public readonly status: SubscriptionStatus,
    public readonly tokensRemaining: number,
    public readonly tokensTotal: number,
    public readonly expiresAt: Date | null
  ) {}

  // ── Status Checks ─────────────────────────────────────────────

  get isActive(): boolean {
    return this.status === 'active' || this.status === 'trial'
  }

  get isExpired(): boolean {
    if (this.status === 'expired') return true
    if (this.expiresAt && new Date() > this.expiresAt) return true
    return false
  }

  get isTrial(): boolean {
    return this.status === 'trial'
  }

  // ── Token Logic ───────────────────────────────────────────────

  get isLowBalance(): boolean {
    return this.tokensRemaining < 1000
  }

  get tokenUsagePercent(): number {
    if (this.tokensTotal === 0) return 0
    return Math.round((this.tokensRemaining / this.tokensTotal) * 100)
  }

  // ── Display Helpers ───────────────────────────────────────────

  getStatusColor(): { bg: string; text: string } {
    const colors: Record<SubscriptionStatus, { bg: string; text: string }> = {
      active: { bg: 'bg-green-100', text: 'text-green-800' },
      trial: { bg: 'bg-blue-100', text: 'text-blue-800' },
      cancelled: { bg: 'bg-yellow-100', text: 'text-yellow-800' },
      expired: { bg: 'bg-red-100', text: 'text-red-800' },
      none: { bg: 'bg-gray-100', text: 'text-gray-800' },
    }
    return colors[this.status] || colors.none
  }

  getBalanceColor(): string {
    if (this.tokensRemaining < 1000) return 'text-red-600'
    if (this.tokensRemaining < 5000) return 'text-yellow-600'
    return 'text-green-600'
  }

  // ── Factory ───────────────────────────────────────────────────

  /**
   * Create from ProfileResponse data.
   *
   * Maps: subscription_plan, subscription_status, token_balance, tokens_remaining
   */
  static fromProfile(data: Record<string, unknown>): SubscriptionModel {
    const status = (data.subscription_status as string) || 'none'
    const validStatuses: SubscriptionStatus[] = ['active', 'trial', 'cancelled', 'expired', 'none']
    const safeStatus: SubscriptionStatus = validStatuses.includes(status as SubscriptionStatus)
      ? (status as SubscriptionStatus)
      : 'none'

    return new SubscriptionModel(
      (data.subscription_plan as string) || (data.plan_name as string) || 'Free',
      safeStatus,
      (data.tokens_remaining as number) ?? (data.token_balance as number) ?? 0,
      (data.tokens_total as number) ?? 10000,
      data.expires_at ? new Date(data.expires_at as string) : null
    )
  }

  /** Free-tier placeholder for unauthenticated or free users. */
  static free(): SubscriptionModel {
    return new SubscriptionModel('Free', 'none', 0, 0, null)
  }

  toJSON(): Record<string, unknown> {
    return {
      planName: this.planName,
      status: this.status,
      tokensRemaining: this.tokensRemaining,
      tokensTotal: this.tokensTotal,
      tokenUsagePercent: this.tokenUsagePercent,
      isActive: this.isActive,
    }
  }
}
