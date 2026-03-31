#!/bin/bash
# curl equivalents for all 10 Python SDK samples
# 每段 curl 命令均可独立拷贝执行，只需提前设置两个环境变量：
#
#   export EVERMEMOS_API_KEY="your_api_key"
#   export EVER_MEM_OS_BASE_URL="https://dev-gateway.aws.evermind.ai"
#
# 完整执行：bash curl_samples.sh

set -x

fmt() { python3 -m json.tool 2>/dev/null || cat; }

# ============================================================
# 01 — 同步写入个人记忆 (msg 1)
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"user_010\",\"messages\":[{\"role\":\"user\",\"timestamp\":$(($(date +%s) * 1000)),\"content\":\"I went to the dentist today. I was scared of the dentist.\"}]}" | fmt

# ============================================================
# 01 — 同步写入个人记忆 (msg 2)
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"user_010\",\"messages\":[{\"role\":\"user\",\"timestamp\":$(($(date +%s) * 1000)),\"content\":\"I admire the beauty of the sea.\"}]}" | fmt

# ============================================================
# 02 — 异步写入（async_mode=true）
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"user_010\",\"async_mode\":true,\"messages\":[{\"role\":\"user\",\"timestamp\":$(($(date +%s) * 1000)),\"content\":\"I love hiking on weekends, especially in the mountains.\"},{\"role\":\"assistant\",\"timestamp\":$(($(date +%s) * 1000 + 1000)),\"content\":\"That sounds wonderful! Do you have a favorite trail?\"},{\"role\":\"user\",\"timestamp\":$(($(date +%s) * 1000 + 2000)),\"content\":\"Yes, the mountain trails near the lake.\"}]}" | fmt

# ============================================================
# 02 — 轮询任务状态（替换 <task_id>）
# ============================================================
curl -s "${EVER_MEM_OS_BASE_URL}/api/v1/tasks/<task_id>" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" | fmt

# ============================================================
# 03 — 查询 episodic_memory（分页 + 时间倒序）
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/get" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"filters":{"user_id":"user_010"},"memory_type":"episodic_memory","page":1,"page_size":10,"rank_by":"timestamp","rank_order":"desc"}' | fmt

# ============================================================
# 03 — 查询 profile
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/get" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"filters":{"user_id":"user_010"},"memory_type":"profile"}' | fmt

# ============================================================
# 03 — 查询 episodic_memory（最近 24h）
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/get" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"filters\":{\"user_id\":\"user_010\",\"timestamp\":{\"gte\":$(($(date +%s) * 1000 - 86400000)),\"lt\":$(($(date +%s) * 1000))}},\"memory_type\":\"episodic_memory\"}" | fmt

# ============================================================
# 03 — 查询群组 episodic_memory
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/get" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"filters":{"group_id":"group_demo_001"},"memory_type":"episodic_memory"}' | fmt

# ============================================================
# 04 — vector 搜索
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/search" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"filters":{"user_id":"user_010"},"query":"outdoor activities the user enjoys","method":"vector","memory_types":["episodic_memory","profile"],"top_k":5}' | fmt

# ============================================================
# 04 — vector 搜索（radius=0.3）
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/search" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"filters":{"user_id":"user_010"},"query":"fear or anxiety experiences","method":"vector","radius":0.3,"top_k":5}' | fmt

# ============================================================
# 04 — keyword 搜索
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/search" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"filters":{"user_id":"user_010"},"query":"dentist","method":"keyword","top_k":10}' | fmt

# ============================================================
# 04 — 群组 vector 搜索
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/search" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"filters":{"group_id":"group_demo_001"},"query":"project discussion","method":"vector","memory_types":["episodic_memory"],"top_k":5}' | fmt

# ============================================================
# 04 — mrag 搜索（服务端支持，不在 OpenAPI spec 中）
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/search" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"filters":{"user_id":"user_010"},"query":"mountain hiking","method":"mrag","include_original_data":true,"top_k":3}' | fmt

# ============================================================
# 05 — 按 memory_id 删除（不存在时预期 500，SERVER BUG 应为 404）
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/delete" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"memory_id":"mem_abc123"}' | fmt || true

# ============================================================
# 05 — 按 user_id 批量删除
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/delete" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_010"}' | fmt

# ============================================================
# 05 — 按 user_id + session_id 删除
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/delete" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_010","session_id":"session_xyz"}' | fmt

# ============================================================
# 05 — 按 group_id 删除
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/delete" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"group_id":"group_demo_001"}' | fmt

# ============================================================
# 05 — 按 user_id + sender_id 删除
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/delete" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_010","sender_id":"sender_alice"}' | fmt

# ============================================================
# 06 — Flush user
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/flush" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_010"}' | fmt

# ============================================================
# 06 — Flush user + session
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/flush" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_010","session_id":"session_xyz"}' | fmt

# ============================================================
# 06 — 写入 session 消息后手动 flush
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"user_010\",\"session_id\":\"session_abc\",\"messages\":[{\"role\":\"user\",\"timestamp\":$(($(date +%s) * 1000)),\"content\":\"Hello, let's talk about travel.\"},{\"role\":\"assistant\",\"timestamp\":$(($(date +%s) * 1000 + 500)),\"content\":\"Sure! Where have you been?\"},{\"role\":\"user\",\"timestamp\":$(($(date +%s) * 1000 + 1000)),\"content\":\"I visited Japan last month.\"}]}" | fmt

curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/flush" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_010","session_id":"session_abc"}' | fmt

# ============================================================
# 07 — Agent 记忆：基础轨迹（user/assistant/tool）
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/agent" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"user_010\",\"session_id\":\"agent_session_001\",\"messages\":[{\"role\":\"user\",\"timestamp\":$(($(date +%s) * 1000)),\"content\":\"Search for the latest news about AI.\"},{\"role\":\"assistant\",\"timestamp\":$(($(date +%s) * 1000 + 1000)),\"content\":\"I'll search the web for you.\",\"tool_calls\":[{\"id\":\"call_001\",\"type\":\"function\",\"function\":{\"name\":\"web_search\",\"arguments\":\"{\\\"query\\\": \\\"latest AI news 2026\\\"}\"}}]},{\"role\":\"tool\",\"timestamp\":$(($(date +%s) * 1000 + 2000)),\"content\":\"Found 10 results about AI in 2026...\",\"tool_call_id\":\"call_001\"},{\"role\":\"assistant\",\"timestamp\":$(($(date +%s) * 1000 + 3000)),\"content\":\"Here's a summary of the latest AI news...\"}]}" | fmt

# ============================================================
# 07 — Agent 记忆：assistant 带 tool_calls（content 用非空占位，null/"" 均报 400）
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/agent" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"user_010\",\"session_id\":\"agent_session_002\",\"messages\":[{\"role\":\"user\",\"timestamp\":$(($(date +%s) * 1000)),\"content\":\"Calculate 42 * 7.\"},{\"role\":\"assistant\",\"timestamp\":$(($(date +%s) * 1000 + 500)),\"content\":\"[tool call]\",\"tool_calls\":[{\"id\":\"call_002\",\"type\":\"function\",\"function\":{\"name\":\"calculator\",\"arguments\":\"{\\\"a\\\": 42, \\\"b\\\": 7, \\\"op\\\": \\\"multiply\\\"}\"}}]},{\"role\":\"tool\",\"timestamp\":$(($(date +%s) * 1000 + 1000)),\"content\":\"294\",\"tool_call_id\":\"call_002\"},{\"role\":\"assistant\",\"timestamp\":$(($(date +%s) * 1000 + 1500)),\"content\":\"42 × 7 = 294\"}]}" | fmt

# ============================================================
# 07 — Agent flush
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/agent/flush" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_010","session_id":"agent_session_001"}' | fmt

# ============================================================
# 08 — 群组记忆写入
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/group" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"group_id\":\"group_demo_001\",\"group_meta\":{\"name\":\"Cookbook Demo\",\"description\":\"Multi-participant demo\"},\"messages\":[{\"role\":\"user\",\"sender_id\":\"user_alice\",\"sender_name\":\"Alice\",\"timestamp\":$(($(date +%s) * 1000)),\"content\":\"Hey team, what's our plan for the weekend trip?\",\"message_id\":\"msg_001\"},{\"role\":\"user\",\"sender_id\":\"user_bob\",\"sender_name\":\"Bob\",\"timestamp\":$(($(date +%s) * 1000 + 5000)),\"content\":\"I'd love to go hiking in the mountains again.\",\"message_id\":\"msg_002\"},{\"role\":\"user\",\"sender_id\":\"user_alice\",\"sender_name\":\"Alice\",\"timestamp\":$(($(date +%s) * 1000 + 10000)),\"content\":\"Sounds great! Let's decide on a trail.\",\"message_id\":\"msg_003\"}]}" | fmt

# ============================================================
# 08 — 群组记忆异步写入
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/group" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"group_id\":\"group_demo_001\",\"async_mode\":true,\"messages\":[{\"role\":\"user\",\"sender_id\":\"user_carol\",\"sender_name\":\"Carol\",\"timestamp\":$(($(date +%s) * 1000 + 20000)),\"content\":\"I prefer the lakeside trail, it's more scenic.\"}]}" | fmt

# ============================================================
# 08 — 群组 flush
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/memories/group/flush" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"group_id":"group_demo_001"}' | fmt

# ============================================================
# 09 — 创建 group
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/groups" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"group_id":"group_demo_001","name":"Demo Group","description":"A sample group for SDK testing"}' | fmt

# ============================================================
# 09 — 查询 group
# ============================================================
curl -s "${EVER_MEM_OS_BASE_URL}/api/v1/groups/group_demo_001" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" | fmt

# ============================================================
# 09 — 更新 group
# ============================================================
curl -s -X PATCH "${EVER_MEM_OS_BASE_URL}/api/v1/groups/group_demo_001" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Demo Group (updated)","description":"Updated via curl"}' | fmt

# ============================================================
# 09 — 创建 sender
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/senders" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"sender_id":"sender_alice","name":"Alice"}' | fmt

# ============================================================
# 09 — 查询 sender
# ============================================================
curl -s "${EVER_MEM_OS_BASE_URL}/api/v1/senders/sender_alice" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" | fmt

# ============================================================
# 09 — 更新 sender
# ============================================================
curl -s -X PATCH "${EVER_MEM_OS_BASE_URL}/api/v1/senders/sender_alice" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice (updated)"}' | fmt

# ============================================================
# 09 — 查询 settings
# ============================================================
curl -s "${EVER_MEM_OS_BASE_URL}/api/v1/settings" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" | fmt

# ============================================================
# 09 — 更新 settings
# ============================================================
curl -s -X PUT "${EVER_MEM_OS_BASE_URL}/api/v1/settings" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"timezone":"Asia/Shanghai","extraction_mode":"default","boundary_detection_timeout":300}' | fmt

# ============================================================
# 10 — 签名单个图片
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/object/sign" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"object_list":[{"file_id":"file_img_001","file_name":"photo.png","file_type":"image"}]}' | fmt

# ============================================================
# 10 — 批量签名（image + file + video）
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/object/sign" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"object_list":[{"file_id":"file_img_001","file_name":"screenshot.jpg","file_type":"image"},{"file_id":"file_doc_002","file_name":"report.pdf","file_type":"file"},{"file_id":"file_vid_003","file_name":"demo.mp4","file_type":"video"}]}' | fmt

# ============================================================
# 10 — 签名无效文件（预期 422）
# ============================================================
curl -s -X POST "${EVER_MEM_OS_BASE_URL}/api/v1/object/sign" \
  -H "Authorization: Bearer ${EVERMEMOS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"object_list":[{"file_id":"bad_file","file_name":"","file_type":"image"}]}' | fmt || true
