import os
import asyncio
from evermemos import AsyncEverMemOS
from datetime import datetime, timezone

client = AsyncEverMemOS(
    api_key=os.environ.get(
        "EVERMEMOS_API_KEY",
    ),
    base_url=os.environ.get(
        "EVER_MEM_OS_CLIENT_BASE_URL",
    ),
)


async def main() -> None:
    # Create or update user custom profile
    # This interface will merge existing data, overlapping fields will be overwritten by input
    user_id = os.environ.get("EVERMEMOS_USER_ID", "user_001")
    
    custom_profile_response = await client.v1.global_user_profile.custom.upsert(
        user_id=user_id,
        custom_profile_data={
            "initial_profile": [
                "User is a software engineer",
                "User is proficient in Python programming",
                "User is interested in AI technology",
                "User likes to read technical documentation",
            ],
        },
    )
    
    print(f"message: {custom_profile_response.message}")
    print(f"success: {custom_profile_response.success}")
    
    if custom_profile_response.data:
        print(f"\nProfile data:")
        print(f"  id: {custom_profile_response.data.get('id')}")
        print(f"  user_id: {custom_profile_response.data.get('user_id')}")
        print(f"  confidence: {custom_profile_response.data.get('confidence')}")
        print(f"  memcell_count: {custom_profile_response.data.get('memcell_count')}")
        print(f"  created_at: {custom_profile_response.data.get('created_at')}")
        print(f"  updated_at: {custom_profile_response.data.get('updated_at')}")
        
        custom_profile_data = custom_profile_response.data.get('custom_profile_data')
        if custom_profile_data:
            print(f"  custom_profile_data:")
            initial_profile = custom_profile_data.get('initial_profile', [])
            if initial_profile:
                for idx, profile_item in enumerate(initial_profile, 1):
                    print(f"    {idx}. {profile_item}")
    else:
        print("\nProfile data: (none)")


if __name__ == "__main__":
    asyncio.run(main())
