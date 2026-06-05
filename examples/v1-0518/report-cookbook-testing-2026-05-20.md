# Cookbook 测试报告

> SDK 版本：`everos` v0.0.1 (trial whl, Stainless 生成)
> 测试时间：2026-05-20
> 测试环境：`https://test-gateway.aws.evermind.ai`
> 对比基线：`cookbook-before-0519-tests/`（旧 SDK，`client.v1.memories`，针对 production）

---

## 背景

本次测试覆盖两套 cookbook：

| 目录 | SDK | 网关 | 说明 |
|------|-----|------|------|
| `cookbook-before-0519-tests/` | `everos` PyPI（旧） | `api.evermind.ai` (prod) | 迁移基线，保留参考 |
| `cookbook-tests/` | `everos` trial whl（新 v1） | `test-gateway.aws.evermind.ai` | 本次主测对象 |

---

## 新 SDK Cookbook 测试结果

### 汇总

| Cookbook | 用例数 | 结果 | 处置 |
|----------|--------|------|------|
| quickstart | 4 | ✅ 4/4 Pass | 保留 |
| personal-assistant | 6 | ✅ 6/6 Pass | 保留 |
| customer-support | 8 | ✅ 8/8 Pass | 保留 |
| ai-tutor | 11 | ✅ 11/11 Pass | 保留 |
| python-integration | 7 | ✅ 7/7 Pass | 保留 |
| batch-processing | 8 | ✅ 8/8 Pass | 保留 |
| team-collaboration | 5 | ⚠️ Deprecated | 不发布，见下节 |

**合计：44/44 Pass（不含 deprecated）**

---

### 各套件详情

#### quickstart
```
Case 1: Store a conversation          → PASS  (message_count=1, status=processing)
Case 2: Trigger boundary detection    → PASS  (5s wait)
Case 3: Search memory                 → PASS  (2 episodes found)
Case 4: Complete working script       → PASS  (3 memories found)
```

#### personal-assistant
```
Case 1: store_message                 → PASS
Case 2: get_memory_context (search)   → PASS  (episodes=1, profiles=0)
Case 3: PersonalAssistant chat loop   → PASS  (2 turns)
Case 4: Using preferences             → PASS  (episodes=4)
Case 5: Get profile memories          → PASS  (count=0, async delay expected)
Case 6: Get episodic memories         → PASS  (count=4)
```

#### customer-support
```
Case 1: Create ticket                 → PASS
Case 2: Store customer messages       → PASS  (4 messages stored)
Case 3: Gather context                → PASS  (episodes=5, profiles=0)
Case 4: Generate context-aware resp   → PASS  (5 memory items used)
Case 5: Close ticket                  → PASS  (boundary detection automatic)
Case 6: Escalate to agent             → PASS  (6 episodes in handoff)
Case 7: Cross-ticket intelligence     → PASS  (6 past interactions found)
Case 8: CustomerSupportBot workflow   → PASS
```

#### ai-tutor
```
Case 1:  Set learning goals           → PASS
Case 2:  Store tutoring interaction   → PASS
Case 3:  Record quiz result           → PASS
Case 4:  Record explanation           → PASS
Case 5:  Identify knowledge gaps      → PASS  (2 episodes, gap filter works)
Case 6:  Get strong topics            → PASS
Case 7:  Schedule review              → PASS  (May 23)
Case 8:  Get due reviews              → PASS  (4 scheduled reviews)
Case 9:  Adaptive question context    → PASS  (profile=4, progress=5)
Case 10: Complete tutor workflow      → PASS
Case 11: Spaced repetition            → PASS  (+3/+7/+14 days)
```

#### python-integration
```
Case 1: Basic sync usage              → PASS  (add OK, search 0 ep, get 0 profile)
Case 2: Concurrent requests           → PASS  (10/10 stored, 0 errors)
Case 3: Async mode task polling       → PASS  (no task_id in new API, expected)
Case 4: Error handling                → PASS  (BadRequestError ✓, NotFoundError ✓)
Case 5: Fire-and-forget storage       → PASS  (sent=20, failed=0)
Case 6: Logging and monitoring        → PASS  (add ~306ms, search ~691ms)
Case 7: memory.feedback()             → PASS  (item_count=1, record_id returned)
```

#### batch-processing
```
Case 1: Convert Slack format          → PASS  (2 messages converted)
Case 2: Convert Discord format        → PASS  (2 messages converted)
Case 3: Batch import personal         → PASS  (5 messages, 3 chunks)
Case 4: Batch import group            → PASS  (4 messages, 2 chunks)
Case 5: Large conversation chunked    → PASS  (12 messages, 3 stages)
Case 6: Error recovery / checkpoint   → PASS  (sent=6, skip on re-run ✓)
Case 7: Import stats tracking         → PASS  (3 msgs, 2 convs)
Case 8: Async mode import             → PASS  (no task_id, expected)
```

---

## ⚠️ team-collaboration — Deprecated

**原因**：group 会话在新 v1 API 中不是一等公民。`owner_type` 仅接受 `["user", "agent"]`，无 `"group"` 类型。旧 SDK 提供的 `memories.group.add()` / `memories.group.flush()` 专用端点已不存在。新 API 需通过 workaround 模拟（共享 `owner_id` + 消息内嵌 `sender_id`/`sender_name`），不适合作为独立 cookbook 发布，会误导用户以为存在专用 group 接口。

**现有覆盖**：`batch-processing` Case 4 已包含多参与人消息导入的核心模式。

---

## 新旧 SDK 主要差异

### ❌ 旧 SDK 方法在新 SDK 中不可用

| 旧 SDK 方法 | 新 SDK 状态 | 说明 |
|------------|------------|------|
| `memories.flush(user_id, session_id)` | ❌ 无端点 | 边界检测自动进行 |
| `memories.group.add(group_id, messages)` | ❌ 无 group 端点 | 用 `memory.add(owner_type="user", owner_id=group_id)` + sender 字段模拟 |
| `memories.group.flush(group_id)` | ❌ 无端点 | N/A |
| `memories.agent.add(agent_id, messages)` | ❌ 无专用端点 | 用 `memory.add(owner_type="agent", ...)` |
| `add()` 响应中的 `task_id` | ❌ 不再返回 | `AddMemoriesData` 只含 `message_count` + `status` |

### ✅ 新 SDK 新增方法

| 方法 | 说明 |
|------|------|
| `memory.feedback(content, memory_id, memory_type, owner_id, owner_type)` | 对记忆内容提交反馈 |
| `storage.sign(object_list)` | 对象存储预签名 |

### 🔄 接口签名变更

| 概念 | 旧 SDK | 新 SDK |
|------|--------|--------|
| 用户标识 | `user_id="alice"` | `owner_id="alice", owner_type="user"` |
| 搜索过滤 | `filters={"user_id": "alice"}` | `owner_id="alice", owner_type="user"` 直接参数 |
| 记忆检索 | `memories.get(filters={...}, memory_type="profile")` | `memory.get(memory_type="profile", owner_id=..., owner_type=...)` |
