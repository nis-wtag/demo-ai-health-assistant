"""Add full-text search and trigram support for doctors

Revision ID: 852b7f8bfe53
Revises: c0d1d943977b
Create Date: 2025-10-15 09:42:57.723504

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TSVECTOR

# revision identifiers, used by Alembic.
revision: str = "852b7f8bfe53"
down_revision: Union[str, Sequence[str], None] = "c0d1d943977b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable extensions (idempotent)
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")  # Optional

    # Add search_vector column
    op.add_column("doctors", sa.Column("search_vector", TSVECTOR, nullable=True))

    # Populate with expanded fields (FIX: Cast entire concat to ::text)
    op.execute("""
        UPDATE doctors d
        SET search_vector = to_tsvector('english', (
            COALESCE(d.full_name, '') || ' ' ||
            COALESCE(array_to_string(d.degrees, ' '), '') || ' ' ||
            COALESCE(d.specialization, '') || ' ' ||
            COALESCE(d.designation, '') || ' ' ||
            COALESCE(d.affiliated_hospital, '') || ' ' ||
            COALESCE(
                (SELECT string_agg('chamber:' || ch.chamber_name || ' addr:' || ch.address, ' ; ')
                 FROM doctor_chambers dc
                 JOIN chambers ch ON dc.chamber_id = ch.id
                 WHERE dc.doctor_id = d.id),
                ''
            ) || ''
        )::text );
    """)

    # Indexes in autocommit (unchanged)
    with op.get_context().autocommit_block():
        op.execute(
            "CREATE INDEX CONCURRENTLY idx_doctors_search_vector ON doctors USING GIN(search_vector);"
        )
        op.execute(
            "CREATE INDEX CONCURRENTLY idx_doctors_name_trgm ON doctors USING GIN(full_name gin_trgm_ops);"
        )
        op.execute(
            "CREATE INDEX CONCURRENTLY idx_doctors_specialization ON doctors(specialization);"
        )
        op.execute(
            "CREATE INDEX CONCURRENTLY idx_chambers_address_trgm ON chambers USING GIN(address gin_trgm_ops);"
        )
        op.execute(
            "CREATE INDEX CONCURRENTLY idx_visiting_hours_day_time ON doctor_chamber_visiting_hours (day, start_time, end_time);"
        )

    # Updated trigger function with expanded fields (FIX: Cast entire concat to ::text)
    op.execute("""
        CREATE OR REPLACE FUNCTION update_doctor_search_vector() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector := to_tsvector('english', (
                COALESCE(NEW.full_name, '') || ' ' ||
                COALESCE(array_to_string(NEW.degrees, ' '), '') || ' ' ||
                COALESCE(NEW.specialization, '') || ' ' ||
                COALESCE(NEW.designation, '') || ' ' ||
                COALESCE(NEW.affiliated_hospital, '') || ' ' ||
                COALESCE(
                    (SELECT string_agg('chamber:' || ch.chamber_name || ' addr:' || ch.address, ' ; ')
                     FROM doctor_chambers dc
                     JOIN chambers ch ON dc.chamber_id = ch.id
                     WHERE dc.doctor_id = NEW.id),
                    ''
                ) || ''
            )::text );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Trigger in autocommit (unchanged)
    with op.get_context().autocommit_block():
        op.execute("""
            CREATE TRIGGER trig_update_doctor_search_vector
            BEFORE INSERT OR UPDATE ON doctors
            FOR EACH ROW EXECUTE FUNCTION update_doctor_search_vector();
        """)


def downgrade() -> None:
    # Drop trigger and function (unchanged)
    with op.get_context().autocommit_block():
        op.execute(
            "DROP TRIGGER IF EXISTS trig_update_doctor_search_vector ON doctors;"
        )
        op.execute("DROP FUNCTION IF EXISTS update_doctor_search_vector();")

    # Drop indexes (unchanged)
    with op.get_context().autocommit_block():
        op.execute("DROP INDEX IF EXISTS idx_doctors_search_vector;")
        op.execute("DROP INDEX IF EXISTS idx_doctors_name_trgm;")
        op.execute("DROP INDEX IF EXISTS idx_doctors_specialization;")
        op.execute("DROP INDEX IF EXISTS idx_chambers_address_trgm;")
        op.execute("DROP INDEX IF EXISTS idx_visiting_hours_day_time;")

    # Drop column (unchanged)
    op.drop_column("doctors", "search_vector")
