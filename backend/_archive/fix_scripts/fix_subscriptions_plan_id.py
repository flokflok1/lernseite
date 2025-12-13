"""
Fix subscriptions table by adding plan_id column
"""
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'lernsystemx_dev'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

conn_string = f"dbname={DB_CONFIG['dbname']} user={DB_CONFIG['user']} password={DB_CONFIG['password']} host={DB_CONFIG['host']} port={DB_CONFIG['port']}"

try:
    print("Connecting to database...")
    with psycopg.connect(conn_string) as conn:
        with conn.cursor() as cur:
            print("Adding plan_id column to subscriptions table...")

            # Add plan_id column
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'subscriptions' AND column_name = 'plan_id'
                    ) THEN
                        ALTER TABLE subscriptions ADD COLUMN plan_id UUID;
                        RAISE NOTICE 'Column plan_id added to subscriptions table';
                    ELSE
                        RAISE NOTICE 'Column plan_id already exists';
                    END IF;
                END$$;
            """)

            print("Updating existing subscriptions with plan_id...")

            # Update existing subscriptions
            cur.execute("""
                UPDATE subscriptions s
                SET plan_id = sp.plan_id
                FROM subscription_plans sp
                WHERE s.plan_type = sp.plan_type
                  AND s.plan_id IS NULL;
            """)
            updated_rows = cur.rowcount
            print(f"Updated {updated_rows} subscriptions with plan_id")

            print("Adding foreign key constraint...")

            # Add foreign key
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.table_constraints
                        WHERE constraint_name = 'fk_subscriptions_plan_id'
                          AND table_name = 'subscriptions'
                    ) THEN
                        ALTER TABLE subscriptions
                        ADD CONSTRAINT fk_subscriptions_plan_id
                        FOREIGN KEY (plan_id) REFERENCES subscription_plans(plan_id) ON DELETE SET NULL;
                        RAISE NOTICE 'Foreign key constraint added';
                    ELSE
                        RAISE NOTICE 'Foreign key constraint already exists';
                    END IF;
                END$$;
            """)

            print("Creating index on plan_id...")

            # Create index
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_subscriptions_plan_id ON subscriptions(plan_id);
            """)

            print("Adding comment...")

            # Add comment
            cur.execute("""
                COMMENT ON COLUMN subscriptions.plan_id IS 'Foreign key reference to subscription_plans table';
            """)

            conn.commit()
            print("\n✅ Migration completed successfully!")

            # Verify
            print("\nVerifying subscriptions table structure...")
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'subscriptions'
                ORDER BY ordinal_position;
            """)

            print("\nSubscriptions table columns:")
            for row in cur.fetchall():
                print(f"  - {row[0]}: {row[1]} (nullable: {row[2]})")

except Exception as e:
    print(f"\n❌ Error: {e}")
    raise
