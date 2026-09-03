import asyncio
from uuid import UUID
from arq import create_pool
from arq.connections import RedisSettings

async def main():
    fixed_inv_id = UUID("00000000-0000-0000-0000-000000000001")
    target_query = '"OpenAI" partnerships "Microsoft" 2026'

    print(f"Queueing live investigation for ID: {fixed_inv_id}")
    redis = await create_pool(RedisSettings())
    await redis.enqueue_job(
        "run_autonomous_investigation", 
        fixed_inv_id, 
        target_query
    )
    print("Job queued. Check your browser at http://localhost:3000 to view live streaming events.")

if __name__ == "__main__":
    asyncio.run(main())
