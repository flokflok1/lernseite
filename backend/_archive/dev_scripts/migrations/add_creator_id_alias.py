"""
Add creator_id as an alias for creator_user_id and fix other column mismatches
"""
import psycopg

DB_CONFIG = {
    'host': '10.0.10.222',
    'port': 5432,
    'user': 'lernsystem',
    'password': '***REMOVED***',
    'dbname': 'lernsystemx_dev'
}

def add_aliases():
    """Add column aliases for backward compatibility"""
    conn_string = f"host={DB_CONFIG['host']} port={DB_CONFIG['port']} dbname={DB_CONFIG['dbname']} user={DB_CONFIG['user']} password={DB_CONFIG['password']}"

    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                print("Adding column aliases for backward compatibility...")

                # Option 1: Add computed columns (views would be better but let's try this)
                # Actually, we should use a VIEW instead to properly alias columns

                # Drop existing view if any
                print("  - Dropping old view if exists...")
                cur.execute("DROP VIEW IF EXISTS courses_view CASCADE")

                # Rename the actual table
                print("  - Renaming courses table to courses_base...")
                cur.execute("ALTER TABLE IF EXISTS courses RENAME TO courses_base")

                # Create a VIEW with proper column names
                print("  - Creating courses VIEW with aliased columns...")
                cur.execute("""
                    CREATE VIEW courses AS
                    SELECT
                        course_id,
                        creator_user_id,
                        creator_user_id AS creator_id,
                        organisation_id,
                        organisation_id AS organization_id,
                        course_type,
                        title,
                        slug,
                        description,
                        long_description,
                        category_id,
                        level,
                        language_default AS language,
                        duration_hours,
                        thumbnail_url,
                        video_preview_url,
                        tags,
                        is_published,
                        published_at,
                        featured,
                        price,
                        original_price,
                        currency,
                        enrollment_count,
                        average_rating,
                        review_count,
                        view_count,
                        status,
                        created_at,
                        updated_at,
                        is_public,
                        archived_at,
                        category,
                        preview_video_url
                    FROM courses_base
                """)

                # Make it updatable
                print("  - Creating INSTEAD OF triggers for INSERT, UPDATE, DELETE...")

                # INSERT trigger
                cur.execute("""
                    CREATE OR REPLACE FUNCTION courses_insert()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        INSERT INTO courses_base (
                            course_id, creator_user_id, organisation_id, course_type,
                            title, slug, description, long_description, category_id,
                            level, language_default, duration_hours, thumbnail_url,
                            video_preview_url, tags, is_published, published_at,
                            featured, price, original_price, currency, enrollment_count,
                            average_rating, review_count, view_count, status,
                            created_at, updated_at, is_public, archived_at, category,
                            preview_video_url
                        ) VALUES (
                            COALESCE(NEW.course_id, gen_random_uuid()),
                            NEW.creator_user_id,
                            NEW.organisation_id,
                            COALESCE(NEW.course_type, 'standard'),
                            NEW.title,
                            NEW.slug,
                            NEW.description,
                            NEW.long_description,
                            NEW.category_id,
                            NEW.level,
                            NEW.language,
                            NEW.duration_hours,
                            NEW.thumbnail_url,
                            NEW.video_preview_url,
                            NEW.tags,
                            NEW.is_published,
                            NEW.published_at,
                            NEW.featured,
                            NEW.price,
                            NEW.original_price,
                            NEW.currency,
                            NEW.enrollment_count,
                            NEW.average_rating,
                            NEW.review_count,
                            NEW.view_count,
                            NEW.status,
                            COALESCE(NEW.created_at, NOW()),
                            COALESCE(NEW.updated_at, NOW()),
                            NEW.is_public,
                            NEW.archived_at,
                            NEW.category,
                            NEW.preview_video_url
                        )
                        RETURNING * INTO NEW;
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                """)

                cur.execute("""
                    CREATE TRIGGER courses_insert_trigger
                    INSTEAD OF INSERT ON courses
                    FOR EACH ROW
                    EXECUTE FUNCTION courses_insert();
                """)

                # UPDATE trigger
                cur.execute("""
                    CREATE OR REPLACE FUNCTION courses_update()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        UPDATE courses_base SET
                            creator_user_id = NEW.creator_user_id,
                            organisation_id = NEW.organisation_id,
                            course_type = NEW.course_type,
                            title = NEW.title,
                            slug = NEW.slug,
                            description = NEW.description,
                            long_description = NEW.long_description,
                            category_id = NEW.category_id,
                            level = NEW.level,
                            language_default = NEW.language,
                            duration_hours = NEW.duration_hours,
                            thumbnail_url = NEW.thumbnail_url,
                            video_preview_url = NEW.video_preview_url,
                            tags = NEW.tags,
                            is_published = NEW.is_published,
                            published_at = NEW.published_at,
                            featured = NEW.featured,
                            price = NEW.price,
                            original_price = NEW.original_price,
                            currency = NEW.currency,
                            enrollment_count = NEW.enrollment_count,
                            average_rating = NEW.average_rating,
                            review_count = NEW.review_count,
                            view_count = NEW.view_count,
                            status = NEW.status,
                            updated_at = NOW(),
                            is_public = NEW.is_public,
                            archived_at = NEW.archived_at,
                            category = NEW.category,
                            preview_video_url = NEW.preview_video_url
                        WHERE course_id = OLD.course_id;
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                """)

                cur.execute("""
                    CREATE TRIGGER courses_update_trigger
                    INSTEAD OF UPDATE ON courses
                    FOR EACH ROW
                    EXECUTE FUNCTION courses_update();
                """)

                # DELETE trigger
                cur.execute("""
                    CREATE OR REPLACE FUNCTION courses_delete()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        DELETE FROM courses_base WHERE course_id = OLD.course_id;
                        RETURN OLD;
                    END;
                    $$ LANGUAGE plpgsql;
                """)

                cur.execute("""
                    CREATE TRIGGER courses_delete_trigger
                    INSTEAD OF DELETE ON courses
                    FOR EACH ROW
                    EXECUTE FUNCTION courses_delete();
                """)

                conn.commit()
                print("SUCCESS: courses VIEW created with proper column aliases!")
                print("The repository can now use:")
                print("  - creator_id (alias for creator_user_id)")
                print("  - language (alias for language_default)")
                print("  - organization_id and organisation_id (both work)")

    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == '__main__':
    add_aliases()
