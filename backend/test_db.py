import asyncio
from src.utils.database import get_async_session
from src.models import Task
from sqlmodel import select
from sqlmodel import SQLModel
from sqlalchemy.exc import OperationalError

async def test_db_connection():
    try:
        print("Testing database connection...")

        # Get the session factory and create a session
        from src.utils.database import get_async_session_factory
        session_factory = get_async_session_factory()

        async with session_factory() as session:
            print("DB connection successful")

            # Test if tables exist by querying tasks
            try:
                result = await session.exec(select(Task))
                tasks = result.all()
                print(f"Successfully queried tasks table. Found {len(tasks)} tasks")
            except OperationalError as e:
                print(f"Table may not exist: {e}")

                # Try to create tables
                print("Attempting to create tables...")
                from src.utils.database import get_async_engine
                engine = get_async_engine()
                async with engine.begin() as conn:
                    await conn.run_sync(SQLModel.metadata.create_all)
                print("Tables created successfully")

    except Exception as e:
        print(f"Database connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_db_connection())