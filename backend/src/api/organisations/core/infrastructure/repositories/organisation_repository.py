"""Organisation Repository"""
from typing import Optional, List
from src.infrastructure.database.connection import get_db_connection
from src.api.organisations.core.domain.entities.organisation import Organisation

class OrganisationRepository:
    @staticmethod
    def find_by_id(org_id: str) -> Optional[Organisation]:
        query = "SELECT * FROM organisations.organisations WHERE organization_id = %s AND deleted_at IS NULL"
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (org_id,))
                row = cur.fetchone()
                if not row:
                    return None
                return Organisation(
                    organization_id=str(row[0]), name=row[1], type=row[2], domain=row[3],
                    logo_url=row[4], billing_email=row[5], phone=row[6],
                    address_street=row[7], address_city=row[8], address_state=row[9],
                    address_country=row[10], address_postal_code=row[11], tax_id=row[12],
                    token_pool=row[13], token_pool_limit=row[14], billing_rate=row[15],
                    max_users=row[16], max_courses=row[17], status=row[18],
                    created_at=row[19], updated_at=row[20], deleted_at=row[21]
                )
    
    @staticmethod
    def list_organisations(limit: int = 100) -> List[Organisation]:
        query = "SELECT * FROM organisations.organisations WHERE deleted_at IS NULL LIMIT %s"
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (limit,))
                rows = cur.fetchall()
                orgs = []
                for row in rows:
                    orgs.append(Organisation(
                        organization_id=str(row[0]), name=row[1], type=row[2], domain=row[3],
                        logo_url=row[4], billing_email=row[5], phone=row[6],
                        address_street=row[7], address_city=row[8], address_state=row[9],
                        address_country=row[10], address_postal_code=row[11], tax_id=row[12],
                        token_pool=row[13], token_pool_limit=row[14], billing_rate=row[15],
                        max_users=row[16], max_courses=row[17], status=row[18],
                        created_at=row[19], updated_at=row[20], deleted_at=row[21]
                    ))
                return orgs
