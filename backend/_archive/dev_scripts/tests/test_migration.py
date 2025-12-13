#!/usr/bin/env python
"""Test migration system"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Import and test
from setup.db_init import DatabaseInitializer

print("="*80)
print("Testing Database Initialization with Migrations")
print("="*80)

db_init = DatabaseInitializer()
print(f"\nDatabase: {db_init.db_name}")
print(f"Host: {db_init.db_host}:{db_init.db_port}")
print(f"User: {db_init.db_user}")

print("\nStarting initialization...")
results = db_init.initialize()

print("\n" + "="*80)
print("RESULTS:")
print("="*80)
print(f"Success: {results.get('success')}")
print(f"Database Created: {results.get('database_created')}")
print(f"Migrations Executed: {results.get('migrations_executed', 0)}")
print(f"Tables Created: {results.get('tables_created', 0)}")

if results.get('errors'):
    print("\nErrors:")
    for error in results['errors']:
        print(f"  - {error}")

if not results.get('success'):
    print("\nError Details:")
    print(results.get('error', 'Unknown error'))
    if 'traceback' in results:
        print("\nTraceback:")
        print(results['traceback'])

print("="*80)
