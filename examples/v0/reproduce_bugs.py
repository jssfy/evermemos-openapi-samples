"""
复现 SDK 两个 Bug:
  Bug 1: GET 请求 body 被丢弃，extra_body/extra_query 参数无法正确传递
  Bug 2: array_format="comma" 导致数组参数逗号拼接
"""
import httpx
from evermemos._qs import Querystring


def bug1_get_body_dropped():
    """Bug 1: SDK 对 GET 请求丢弃 JSON body，extra_body 不生效"""
    print("=" * 60)
    print("Bug 1: GET 请求 body 被丢弃")
    print("=" * 60)

    from evermemos._base_client import SyncAPIClient

    # 模拟 SDK 构建 GET 请求的流程
    # _base_client.py:547 => is_body_allowed = options.method.lower() != "get"
    # _base_client.py:563 => else: headers.pop("Content-Type", None); kwargs.pop("data", None)

    # 用原生 httpx 演示差异
    client = httpx.Client()

    # GET + query string (extra_query 的效果)
    req_query = client.build_request(
        "GET",
        "https://api.evermind.ai/api/v0/memories/search",
        params={"user_id": "user_011", "query": "coffee", "top_k": "10"},
    )
    print(f"\n[extra_query] GET URL: {req_query.url}")
    print(f"[extra_query] Body:    {req_query.content}")
    print("→ 参数在 URL query string 中，但服务端从 JSON body 解析 RetrieveMemRequest")

    # GET + json body (extra_body 的效果，但 SDK 会丢弃!)
    req_body = client.build_request(
        "GET",
        "https://api.evermind.ai/api/v0/memories/search",
        content=b'{"user_id": "user_011", "query": "coffee", "top_k": 10}',
        headers={"Content-Type": "application/json"},
    )
    print(f"\n[extra_body + httpx 原生] Body: {req_body.content}")
    print("→ httpx 本身支持 GET + body，但 SDK _base_client.py:563 主动丢弃了它")

    # SDK 实际行为
    print(f"\n[SDK 实际行为] _base_client.py:547:")
    print(f'  is_body_allowed = options.method.lower() != "get"  # GET → False')
    print(f"  → json_data 被忽略, Content-Type 被移除")
    print(f"  → 服务端收到空 body → user_id=None, group_ids=None → 400 报错")
    client.close()


def bug2_array_comma_format():
    """Bug 2: array_format="comma" 将数组 join 为单值"""
    print("\n" + "=" * 60)
    print("Bug 2: array_format='comma' 数组序列化错误")
    print("=" * 60)

    params = {
        "group_ids": ["sdk_tg_123", "nonexistent_group"],
        "query": "coffee",
        "top_k": 10,
    }

    # 当前 SDK 行为
    qs_comma = Querystring(array_format="comma")
    comma_result = qs_comma.stringify(params)
    print(f"\n[当前 SDK] array_format='comma':")
    print(f"  URL: ?{comma_result}")

    from urllib.parse import parse_qs
    parsed = parse_qs(comma_result)
    print(f"  服务端 parse_qs: group_ids = {parsed.get('group_ids', [])}")
    print(f"  → 1 个元素 (含逗号的字符串), 匹配不到任何 group")

    # 修复后行为
    qs_repeat = Querystring(array_format="repeat")
    repeat_result = qs_repeat.stringify(params)
    print(f"\n[修复后] array_format='repeat':")
    print(f"  URL: ?{repeat_result}")

    parsed2 = parse_qs(repeat_result)
    print(f"  服务端 parse_qs: group_ids = {parsed2.get('group_ids', [])}")
    print(f"  → 2 个独立元素, 正确匹配")


def summary():
    print("\n" + "=" * 60)
    print("总结: 两个 Bug 的叠加效应")
    print("=" * 60)
    print("""
┌─────────────────────────────────────────────────────────┐
│ 调用方式                        │ 结果                  │
├─────────────────────────────────┼───────────────────────┤
│ extra_query={group_ids:[a,b]}   │ Bug1: 参数在 URL 中,  │
│                                 │   服务端从 body 读    │
│                                 │ Bug2: 即使服务端能读   │
│                                 │   query string, 也是  │
│                                 │   逗号拼接的单值       │
├─────────────────────────────────┼───────────────────────┤
│ extra_body={group_ids:[a,b]}    │ Bug1: GET 请求 body   │
│                                 │   被 SDK 丢弃, 服务端 │
│                                 │   收到空 body → 400   │
├─────────────────────────────────┼───────────────────────┤
│ search() 无原生 group_ids 参数  │ OpenAPI 定义在        │
│                                 │   requestBody, 但     │
│                                 │   Stainless 未生成    │
│                                 │   typed 参数          │
└─────────────────────────────────┴───────────────────────┘

修复优先级:
  P0: OpenAPI 中 search/get 端点改为 POST, 或将参数移至 parameters
  P1: _client.py array_format 改为 "repeat"
""")


if __name__ == "__main__":
    bug1_get_body_dropped()
    bug2_array_comma_format()
    summary()
