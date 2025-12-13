#!/usr/bin/env python3
"""Check token wallets"""

import psycopg

conn = psycopg.connect(
    host='10.0.10.222',
    port='5432',
    dbname='lernsystemx_dev',
    user='lernsystem',
    password='***REMOVED***'
)

cur = conn.cursor()
cur.execute('SELECT wallet_id, user_id, organization_id, balance FROM token_wallets ORDER BY created_at DESC LIMIT 5')
rows = cur.fetchall()

print(f'Total wallets: {len(rows)}')
for row in rows:
    print(f'  Wallet: {row[0]}, User: {row[1]}, Org: {row[2]}, Balance: {row[3]}')

conn.close()
