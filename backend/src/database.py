from typing import AsyncGenerator
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from src.config import settings

# El pooler de Supabase (pgbouncer) en modo "transaction" no soporta prepared
# statements reutilizables: asyncpg los nombra de forma incremental
# ("_asyncpg_stmt_1_") y al reciclar la conexion el pooler los ve duplicados,
# fallando con DuplicatePreparedStatementError. Desactivamos ambas cachas de
# statements y generamos nombres unicos, para que la app funcione igual contra
# el pooler en modo transaction (:6543), en modo session (:5432) o directo.
ASYNCPG_CONNECT_ARGS = {
    "statement_cache_size": 0,
    "prepared_statement_cache_size": 0,
    "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
}

# Create async engine for PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    # El pooling real lo hace pgbouncer del lado de Supabase; mantener un pool
    # propio encima es lo que provoca el choque de prepared statements.
    poolclass=NullPool,
    connect_args=ASYNCPG_CONNECT_ARGS
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
