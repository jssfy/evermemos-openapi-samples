# pip install evermemos
# Groups / Senders / Settings CRUD
from pprint import pprint
from evermemos import EverMemOS

client = EverMemOS()
groups = client.v1.groups
senders = client.v1.senders
settings = client.v1.settings

# ======================== Groups ========================

print("=== create group ===")
resp = groups.create(
    group_id="group_demo_001",
    name="Demo Group",
    description="A sample group for SDK testing",
)
pprint(resp)

print("\n=== retrieve group ===")
resp = groups.retrieve("group_demo_001")
pprint(resp)

print("\n=== patch group ===")
resp = groups.patch(
    "group_demo_001",
    name="Demo Group (updated)",
    description="Updated via SDK",
)
pprint(resp)

# ======================== Senders ========================

print("\n=== create sender ===")
resp = senders.create(
    sender_id="sender_alice",
    name="Alice",
)
pprint(resp)

print("\n=== retrieve sender ===")
resp = senders.retrieve("sender_alice")
pprint(resp)

print("\n=== patch sender ===")
resp = senders.patch(
    "sender_alice",
    name="Alice (updated)",
)
pprint(resp)

# ======================== Settings ========================

print("\n=== retrieve settings ===")
resp = settings.retrieve()
pprint(resp)

print("\n=== update settings ===")
resp = settings.update(
    timezone="Asia/Shanghai",
    extraction_mode="default",
    boundary_detection_timeout=300,
)
pprint(resp)
