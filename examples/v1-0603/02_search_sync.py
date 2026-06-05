#!/usr/bin/env python3
"""
02_search_sync.py — 同步 search 记忆

先运行 01_add_sync.py 写入数据，再运行本脚本查询。
"""
import os, time
from everos_cloud import EverOS

API_KEY  = os.getenv("EVEROS_API_KEY", "ddcf3ffb-df31-4c9c-9d30-fb2ee67aed26")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://dev-gateway.aws.evermind.ai")
USER_ID  = "everos-cloud-example-001"

client = EverOS(api_key=API_KEY, base_url=BASE_URL)

# add 是异步入队，等待索引完成
print("等待 3s 让记忆索引完成...")
time.sleep(3)

resp = client.v1.memories.search(
    filters={"user_id": USER_ID},
    query="思考快与慢 双过程理论",
    top_k=5,
    method="hybrid",
)

print("search response:", resp)
print("episodes:", resp.data.episodes)
print("profiles:", resp.data.profiles)
