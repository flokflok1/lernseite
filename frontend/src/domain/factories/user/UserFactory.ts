/**
 * User Factory
 *
 * Transforms API responses into UserModel domain objects.
 * Handles both single-user and list-based transformations.
 *
 * Example:
 *   const user = UserFactory.fromApiResponse(apiData, groups, permissions)
 *   const users = UserFactory.fromApiList(apiListResponse)
 */

import { UserModel } from '@/domain/models/user/User.model'
import type { UserGroup } from '@/domain/models/user/types'

export class UserFactory {
  /**
   * Create UserModel from API response.
   * Delegates to UserModel.fromAPI — provides a clean factory interface.
   */
  static fromApiResponse(
    data: Record<string, unknown>,
    groups?: UserGroup[],
    permissions?: string[]
  ): UserModel {
    return UserModel.fromAPI(data, groups, permissions)
  }

  /**
   * Create list of UserModel instances from API list response.
   * Handles both `{ users: [...] }` and raw array formats.
   */
  static fromApiList(
    data: Record<string, unknown>[] | Record<string, unknown>
  ): UserModel[] {
    const items = Array.isArray(data)
      ? data
      : (data.users as Record<string, unknown>[]) || []

    return items.map(item => UserModel.fromAPI(item))
  }
}
