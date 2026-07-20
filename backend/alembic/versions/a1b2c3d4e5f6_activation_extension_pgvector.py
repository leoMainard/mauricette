"""activation extension pgvector

Revision ID: a1b2c3d4e5f6
Revises: b5efcff605cf
Create Date: 2026-07-19 18:00:00.000000

Prérequis Windows (pas de Docker) : PostgreSQL 16 natif + Visual Studio Build
Tools (workload "Développement Desktop en C++"). Depuis un "x64 Native Tools
Command Prompt for VS" :
    set "PGROOT=C:\\Program Files\\PostgreSQL\\16"
    git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
    cd pgvector
    nmake /F Makefile.win
    nmake /F Makefile.win install
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'b5efcff605cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector")
