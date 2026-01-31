import asyncio
from evermemos import AsyncEverMemOS

memories = AsyncEverMemOS().v1.memories


async def main() -> None:
    # Get memories
    response = await memories.get(
        extra_query={
            "user_id": "天下霸唱",
            "memory_type": "profile",
        }
    )
    print(f"message: {response.message}")
    print(f"status: {response.status}")
    
    if not response.result:
        return
    
    print(f"total_count: {response.result.total_count}")
    
    if not response.result.memories:
        return
    
    print(f"Found {len(response.result.memories)} memories")
    
    # Helper function to print field if exists and has value
    def print_field(memory, name: str):
        value = getattr(memory, name, None)
        if value:
            print(f"  {name}: {value}")
    
    for idx, memory in enumerate(response.result.memories[:5], 1):  # Show at most 5
        print(f"\nMemory {idx}:")
        
        # All memory types have id
        print_field(memory, 'id')
        print_field(memory, 'user_id')
        
        # Profile type specific attributes
        print_field(memory, 'profile_data')
        print_field(memory, 'scenario')
        confidence = getattr(memory, 'confidence', None)
        if confidence is not None:
            print(f"  confidence: {confidence}")
        
        # EpisodicMemory type specific attributes
        print_field(memory, 'episode_id')
        print_field(memory, 'title')
        print_field(memory, 'summary')
        
        # EventLog type specific attributes
        print_field(memory, 'atomic_fact')
        print_field(memory, 'event_type')
        
        # Foresight type specific attributes
        print_field(memory, 'content')
        
        # Common attributes
        print_field(memory, 'group_id')
        print_field(memory, 'group_name')
        print_field(memory, 'timestamp')
        print_field(memory, 'created_at')
        print_field(memory, 'updated_at')


if __name__ == "__main__":
    asyncio.run(main())
