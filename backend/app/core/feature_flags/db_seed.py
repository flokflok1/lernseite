"""
Database Seed for Feature Flags

Initializes all feature flags with their default state.
Run this after database tables are created.

Tables Required:
- feature_flags
- feature_flag_user_overrides
- feature_flag_org_overrides
- feature_flag_segments
- feature_flag_rollouts
"""

from app.core.bootstrap import extensions
from app.core.feature_flags.flag_config import FEATURE_FLAGS, FEATURE_GROUPS
from datetime import datetime


def seed_feature_flags():
    """
    Seed database with all feature flags

    Inserts all flags from flag_config.py with their default state
    """
    with extensions.db_pool.connection() as conn:
        with conn.cursor() as cur:
            print("🌱 Seeding feature flags...")

            for feature_name, default_state in FEATURE_FLAGS.items():
                # Insert feature flag
                cur.execute("""
                    INSERT INTO feature_flags (name, is_enabled, created_at, updated_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE
                    SET is_enabled = EXCLUDED.is_enabled, updated_at = EXCLUDED.updated_at
                """, (feature_name, default_state, datetime.utcnow(), datetime.utcnow()))

                print(f"  ✓ {feature_name}: {'ENABLED' if default_state else 'DISABLED'}")

            conn.commit()
            print(f"\n✅ Seeded {len(FEATURE_FLAGS)} feature flags")


def seed_feature_groups():
    """
    Seed feature flag groups (optional - for admin UI)
    """
    with extensions.db_pool.connection() as conn:
        with conn.cursor() as cur:
            print("\n🌱 Seeding feature flag groups...")

            for group_name, feature_list in FEATURE_GROUPS.items():
                for feature_name in feature_list:
                    cur.execute("""
                        INSERT INTO feature_flag_groups (group_name, feature_name, created_at)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (group_name, feature_name) DO NOTHING
                    """, (group_name, feature_name, datetime.utcnow()))

                print(f"  ✓ {group_name}: {len(feature_list)} features")

            conn.commit()
            print(f"\n✅ Seeded {len(FEATURE_GROUPS)} feature groups")


def enable_feature_for_beta_users(feature_name: str):
    """
    Enable a feature for all beta users

    Args:
        feature_name: Feature flag name
    """
    with extensions.db_pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO feature_flag_segments (feature_name, segment, is_enabled, created_at)
                VALUES (%s, 'beta', TRUE, %s)
                ON CONFLICT (feature_name, segment) DO UPDATE
                SET is_enabled = TRUE
            """, (feature_name, datetime.utcnow()))

            conn.commit()
            print(f"✅ Enabled '{feature_name}' for beta users")


def set_percentage_rollout(feature_name: str, percentage: int):
    """
    Set percentage rollout for a feature

    Args:
        feature_name: Feature flag name
        percentage: 0-100
    """
    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100")

    with extensions.db_pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO feature_flag_rollouts (feature_name, percentage, created_at, updated_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (feature_name) DO UPDATE
                SET percentage = EXCLUDED.percentage, updated_at = EXCLUDED.updated_at
            """, (feature_name, percentage, datetime.utcnow(), datetime.utcnow()))

            conn.commit()
            print(f"✅ Set '{feature_name}' to {percentage}% rollout")


if __name__ == '__main__':
    """
    Run this script directly to seed the database

    Usage:
        python -m app.core.feature_flags.db_seed
    """
    print("=" * 60)
    print("FEATURE FLAGS DATABASE SEED")
    print("=" * 60)

    try:
        seed_feature_flags()
        # seed_feature_groups()  # Uncomment if you have feature_flag_groups table

        print("\n" + "=" * 60)
        print("✅ SEEDING COMPLETE")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
