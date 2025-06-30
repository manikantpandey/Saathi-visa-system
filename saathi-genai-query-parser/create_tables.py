import asyncio
from app.visa_requirements import Base, engine

async def create():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(create())