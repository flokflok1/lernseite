/**
 * Admin translations index
 * Merges main admin.json with editor sub-modules
 */

import adminBase from '../admin.json'
import editorsModule from './editors'

export default {
  admin: {
    ...adminBase.admin,
    ...editorsModule
  }
}
