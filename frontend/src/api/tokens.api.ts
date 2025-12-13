import http from './http'

// ============================================================================
// Types & Interfaces
// ============================================================================

export interface TokenBalanceResponse {
  balance: number
  reserved: number
  available: number
  total_purchased: number
  total_granted: number
  total_consumed: number
  monthly_grant: number | null
  last_grant_date: string | null
  source: 'user' | 'organisation'
}

export interface TokenTransactionItem {
  transaction_id: number
  amount: number
  balance_after: number
  reason: string
  description: string
  created_at: string
}

export interface TokenUsageResponse {
  user_id: number
  current_balance: number
  total_tokens_used: number
  total_tokens_bought: number
  total_tokens_granted: number
  by_reason: Record<string, number>
  by_method: Record<string, number>
  period_start: string
  period_end: string
}

// ============================================================================
// Token API Functions
// ============================================================================

/**
 * Get current user's token balance
 */
export const getMyTokens = async (): Promise<TokenBalanceResponse> => {
  const response = await http.get<{ success: boolean; tokens: TokenBalanceResponse }>('/profile/tokens')
  return response.data.tokens
}

/**
 * Get token transaction history
 */
export const getTokenTransactions = async (limit = 50, offset = 0): Promise<{ transactions: TokenTransactionItem[]; total: number }> => {
  const response = await http.get<{ success: boolean; transactions: TokenTransactionItem[]; total: number }>('/tokens/transactions', {
    params: { limit, offset }
  })
  return {
    transactions: response.data.transactions,
    total: response.data.total
  }
}

/**
 * Get token usage analytics
 */
export const getTokenUsage = async (periodDays = 30): Promise<TokenUsageResponse> => {
  const response = await http.get<{ success: boolean; stats: TokenUsageResponse }>('/tokens/usage', {
    params: { period_days: periodDays }
  })
  return response.data.stats
}

/**
 * Estimate AI cost for a method
 */
export const estimateAICost = async (methodName: string, complexity: 'simple' | 'medium' | 'complex' = 'medium') => {
  const response = await http.post<{
    success: boolean
    estimate: {
      method_name: string
      complexity: string
      estimated_tokens: number
      can_afford: boolean
      current_balance: number
    }
  }>('/tokens/estimate', {
    method_name: methodName,
    complexity
  })
  return response.data.estimate
}
