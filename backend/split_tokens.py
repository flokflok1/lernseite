#!/usr/bin/env python3
"""
Split tokens.py into 4 focused modules based on functionality.

Structure:
- wallet.py: Token balance queries (get_my_token_balance, get_organisation_tokens)
- transactions.py: Transaction history (get_my_transactions)
- stats.py: Usage statistics (get_my_usage, estimate_ai_cost)
- admin.py: Admin operations (manual_topup, get_token_stats)
"""
from pathlib import Path

# Read original file
tokens_original = Path("app/api/tokens.py.original").read_text()
lines = tokens_original.splitlines(keepends=True)

# Common header imports (lines 0-29)
header = "".join(lines[0:30])

# wallet.py: Lines 37-111 (get_my_token_balance) + 250-319 (get_organisation_tokens)
wallet_content = header + """

# ============================================================================
# WALLET BALANCE ENDPOINTS
# ============================================================================

""" + "".join(lines[36:111]) + """

# ============================================================================
# ORGANISATION WALLET ENDPOINTS
# ============================================================================

""" + "".join(lines[249:320])

# transactions.py: Lines 113-181 (get_my_transactions)
transactions_content = header + """

# ============================================================================
# TRANSACTION HISTORY ENDPOINTS
# ============================================================================

""" + "".join(lines[112:182])

# Remaining lines for stats and admin (read from 183 onwards)
remaining_lines = lines[182:]

# Find split points in remaining lines
stats_start = 0  # get_my_usage starts immediately
admin_start = None
estimate_start = None

for i, line in enumerate(remaining_lines):
    if "@api_v1.route('/tokens/manual-topup'" in line:
        admin_start = i
    elif "@api_v1.route('/tokens/estimate'" in line:
        estimate_start = i

# stats.py: get_my_usage (lines 183-244) + estimate_ai_cost (lines 463-end)
if estimate_start:
    stats_content = header + """

# ============================================================================
# USAGE STATISTICS ENDPOINTS
# ============================================================================

""" + "".join(remaining_lines[stats_start:admin_start]) + """

# ============================================================================
# AI COST ESTIMATION
# ============================================================================

""" + "".join(remaining_lines[estimate_start:])
else:
    stats_content = header + """

# ============================================================================
# USAGE STATISTICS ENDPOINTS
# ============================================================================

""" + "".join(remaining_lines[stats_start:admin_start if admin_start else None])

# admin.py: manual_topup + get_token_stats (lines 325-462)
if admin_start and estimate_start:
    admin_content = header + """

# ============================================================================
# ADMIN TOKEN MANAGEMENT ENDPOINTS
# ============================================================================

""" + "".join(remaining_lines[admin_start:estimate_start])
elif admin_start:
    admin_content = header + """

# ============================================================================
# ADMIN TOKEN MANAGEMENT ENDPOINTS
# ============================================================================

""" + "".join(remaining_lines[admin_start:])
else:
    admin_content = header + "\n# No admin endpoints found\n"

# Write split files
Path("app/api/tokens/wallet.py").write_text(wallet_content)
Path("app/api/tokens/transactions.py").write_text(transactions_content)
Path("app/api/tokens/stats.py").write_text(stats_content)
Path("app/api/tokens/admin.py").write_text(admin_content)

print("✅ tokens.py split into 4 files:")
print(f"   - wallet.py ({len(wallet_content.splitlines())} lines)")
print(f"   - transactions.py ({len(transactions_content.splitlines())} lines)")
print(f"   - stats.py ({len(stats_content.splitlines())} lines)")
print(f"   - admin.py ({len(admin_content.splitlines())} lines)")
