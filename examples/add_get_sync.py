# EverMemOS should've been installed (pip install evermemos -U)
import time
from evermemos import EverMemOS
from datetime import datetime, timezone

client = EverMemOS()
memories = client.v1.memories
request_stats = client.v1.status.request

sender = "user_015"

# 1. Add a memory
add_response = memories.add(
    content="I went to the dentist today. I was scared of the dentist.",
    create_time=datetime.now(timezone.utc).isoformat(),
    message_id=f"msg_{int(datetime.now(timezone.utc).timestamp() * 1000)}",
    sender=sender,
    flush=True,  # Force memory extraction immediately; not recommended for production
)

print("=== add response ===")
print(add_response)

request_id = add_response.request_id

# 2. Poll request status until success or timeout before calling get
poll_interval = 3  # seconds
elapsed = 0
while elapsed < 600:  # seconds
    status_response = request_stats.get(request_id=request_id)
    s = (status_response.data or {}).get("status") or getattr(status_response, "status", None) or "unknown"
    print(f"  [polling] status={s}")
    if s == "success":
        break
    time.sleep(poll_interval)
    elapsed += poll_interval
else:
    print("  Poll timeout; still calling get (result may not include this memory yet).")

# 3. Get memories for this user (add & get combined flow)
get_response = memories.get(
    extra_query={
        "user_id": sender,
        "memory_type": "episodic_memory",
    },
)

print("\n=== get response ===")
print(get_response)
