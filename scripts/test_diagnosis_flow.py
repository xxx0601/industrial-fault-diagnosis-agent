#!/usr/bin/env python3

"""

工业设备故障诊断 Agent — 本地端到端验证脚本（时间线 logs[] 场景）



用法（先启动后端）:

    cd backend

    .venv\\Scripts\\uvicorn app.main:app --reload --port 8001



另开终端（项目根目录）:

    backend\\.venv\\Scripts\\python.exe scripts\\test_diagnosis_flow.py



可选环境变量:

    API_BASE_URL=http://127.0.0.1:8001

    LOG_FILE_PATH=backend/data/samples/timeline_fault_chain.json

    FAULT_CODE=          # 留空则从时间线推断 Primary；填 E204 等则覆盖

    WORK_ORDERS_INDEX=backend/data/work_orders_index.json

"""



from __future__ import annotations



import json

import os

import sys

from datetime import datetime

from pathlib import Path



try:

    import requests

except ImportError:

    print("请先安装: pip install requests")

    sys.exit(1)



PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_LOG = PROJECT_ROOT / "backend" / "data" / "samples" / "timeline_fault_chain.json"



API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8001").rstrip("/")

LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", str(DEFAULT_LOG))

# 默认不传故障码，验证多码时间线与 Primary=E410

FAULT_CODE = os.getenv("FAULT_CODE", "").strip() or None



WORK_ORDERS_INDEX = Path(

    os.getenv(

        "WORK_ORDERS_INDEX",

        str(PROJECT_ROOT / "backend" / "data" / "work_orders_index.json"),

    )

)





def banner(title: str) -> None:

    width = 60

    print()

    print("=" * width)

    print(f"  {title}")

    print("=" * width)





def sub_banner(title: str) -> None:

    print()

    print(f"--- {title} ---")





def pretty_json(data: object) -> str:

    return json.dumps(data, ensure_ascii=False, indent=2)





def check_api_health() -> None:

    sub_banner("0. 健康检查")

    url = f"{API_BASE_URL}/api/v1/health"

    print(f"GET {url}")

    resp = requests.get(url, timeout=10)

    resp.raise_for_status()

    print(pretty_json(resp.json()))

    print("✓ API 可用")





def upload_log(file_path: Path) -> str:

    sub_banner("1. 上传设备日志")

    if not file_path.is_file():

        raise FileNotFoundError(f"日志文件不存在: {file_path}")



    url = f"{API_BASE_URL}/api/v1/uploads"

    print(f"POST {url}")

    print(f"文件: {file_path}")



    suffix = file_path.suffix.lower()

    content_type = "application/json" if suffix == ".json" else "text/plain"



    with file_path.open("rb") as f:

        files = {"file": (file_path.name, f, content_type)}

        resp = requests.post(url, files=files, timeout=60)



    if not resp.ok:

        print(f"上传失败 HTTP {resp.status_code}: {resp.text}")

        resp.raise_for_status()



    body = resp.json()

    print(pretty_json(body))

    file_id = body["file_id"]

    print(f"✓ 上传成功, file_id = {file_id}")

    return file_id





def run_diagnosis(file_id: str, fault_code: str | None) -> dict:

    sub_banner("2. 故障诊断 (LangGraph v4 Timeline)")

    url = f"{API_BASE_URL}/api/v1/diagnosis"

    payload: dict = {"file_id": file_id}

    if fault_code:

        payload["fault_code"] = fault_code

    print(f"POST {url}")

    print(pretty_json(payload))



    resp = requests.post(

        url,

        json=payload,

        headers={"Content-Type": "application/json", "Accept": "application/json"},

        timeout=120,

    )

    if not resp.ok:

        print(f"诊断失败 HTTP {resp.status_code}: {resp.text}")

        resp.raise_for_status()



    body = resp.json()

    print("✓ 诊断完成")

    return body





def print_timeline_summary(result: dict) -> None:

    """打印时间线诊断扩展字段。"""

    codes = result.get("fault_codes") or []

    if codes:

        print(f"  fault_codes      : {' → '.join(codes)}")



    primary = result.get("primary_fault")

    if primary:

        print(

            f"  primary_fault    : {primary.get('code')} {primary.get('description')}"

        )



    related = result.get("related_faults") or []

    if related:

        print("  related_faults   :")

        for item in related:

            print(f"    - {item.get('code')} {item.get('description')}")



    evolution = result.get("fault_evolution") or []

    if evolution:

        print("  fault_evolution  :")

        for i, step in enumerate(evolution):

            prefix = "    ↓ " if i > 0 else "    • "

            print(f"{prefix}{step}")



    temp = result.get("temperature_trend")

    vib = result.get("vibration_trend")

    if temp:

        print(

            f"  temperature      : {temp.get('direction')} "

            f"({temp.get('from_value')} → {temp.get('to_value')})"

        )

    if vib:

        print(

            f"  vibration        : {vib.get('direction')} "

            f"({vib.get('from_value')} → {vib.get('to_value')})"

        )





def print_diagnosis_summary(result: dict) -> None:

    sub_banner("3. 诊断结果摘要")

    print(f"  diagnosis_id     : {result.get('diagnosis_id')}")

    print(f"  risk_level       : {result.get('risk_level')}")

    print()

    print_timeline_summary(result)

    print()

    print("  可能原因:")

    for cause in result.get("possible_causes") or []:

        print(f"    • {cause}")

    print()

    print("  维修建议:")

    for rec in result.get("recommendations") or []:

        print(f"    • {rec}")





def assert_timeline_expectations(result: dict, fault_code_override: str | None) -> None:

    """时间线样例下的基本断言（无覆盖故障码时）。"""

    if fault_code_override:

        print("  （已指定 FAULT_CODE，跳过时间线自动推断断言）")

        return



    codes = result.get("fault_codes") or []

    expected_chain = ["E101", "E305", "E204", "E410"]

    if codes != expected_chain:

        print(f"  ⚠ fault_codes 期望 {expected_chain}，实际 {codes}")

    else:

        print(f"  ✓ fault_codes 序列正确: {' → '.join(codes)}")



    primary = result.get("primary_fault") or {}

    if primary.get("code") != "E410":

        print(f"  ⚠ primary_fault 期望 E410，实际 {primary.get('code')}")

    else:

        print(f"  ✓ primary_fault = E410 {primary.get('description', '')}")



    evolution = result.get("fault_evolution") or []

    if evolution and "轴承磨损" in evolution[0]:

        print("  ✓ fault_evolution 以轴承磨损起始")

    elif evolution:

        print(f"  ⚠ fault_evolution 首步: {evolution[0]}")





def print_trace(result: dict) -> None:

    sub_banner("4. Agent Trace（全流程）")

    trace = result.get("trace") or []

    if not trace:

        print("  （无 trace 数据）")

        return



    tool_steps = [s for s in trace if s.get("node") == "tool_call"]

    other_steps = [s for s in trace if s.get("node") != "tool_call"]



    if tool_steps:

        print(f"\n  [Tool Calling] 共 {len(tool_steps)} 次工具调用:\n")

        for step in tool_steps:

            meta = step.get("metadata") or {}

            print(f"  Step {step.get('step')} | {step.get('message')}")

            print(f"    Status   : {step.get('status')}")

            print(f"    Duration : {meta.get('duration_ms')} ms")

            print(f"    Input    : {pretty_json(meta.get('tool_input', {}))}")

            print(f"    Output   : {pretty_json(meta.get('tool_output', {}))}")

            if meta.get("error"):

                print(f"    Error    : {meta.get('error')}")

            print()



    if other_steps:

        print(f"  [其他节点] 共 {len(other_steps)} 步:\n")

        for step in other_steps:

            label = (step.get("metadata") or {}).get("node_label", step.get("node"))

            print(f"  Step {step.get('step')} | {label}")

            print(f"    {step.get('message')} [{step.get('status')}]")

        print()





def fetch_diagnosis_detail(diagnosis_id: str) -> dict:

    sub_banner("5. 诊断详情 GET /api/v1/diagnosis/{id}")

    url = f"{API_BASE_URL}/api/v1/diagnosis/{diagnosis_id}"

    print(f"GET {url}")

    resp = requests.get(url, timeout=30)

    resp.raise_for_status()

    detail = resp.json()

    print(f"  risk_score    : {detail.get('risk_score')}")

    print(f"  work_order_id : {detail.get('work_order_id')}")

    print(f"  fault_code    : {detail.get('fault_code')}")



    dr = detail.get("diagnosis_result") or {}

    print_timeline_summary(dr)



    entries = detail.get("log_entries") or []

    if entries:

        print(f"  log_entries   : {len(entries)} 条")

    if detail.get("rag_sources"):

        print(f"  RAG 引用      : {len(detail['rag_sources'])} 条")

    if detail.get("tool_results"):

        print(f"  tool_results  : {len(detail['tool_results'])} 条")

    return detail





def check_work_orders(

    risk_level: str,

    work_order_id: str | None,

    diagnosis_id: str,

) -> None:

    sub_banner("6. 维修工单检查")

    print(f"  risk_level = {risk_level}")



    if risk_level != "HIGH":

        print("  风险未达 HIGH，预期不创建工单（流程正常）。")

        return



    print(f"  索引文件: {WORK_ORDERS_INDEX}")

    if not WORK_ORDERS_INDEX.is_file():

        print("  ⚠ 未找到工单索引文件（请确认从 backend/ 目录启动 API）")

        return



    orders = json.loads(WORK_ORDERS_INDEX.read_text(encoding="utf-8"))

    if not isinstance(orders, list):

        print("  ⚠ 工单索引格式异常")

        return



    print(f"  索引中工单总数: {len(orders)}")



    matched = []

    if work_order_id:

        matched = [o for o in orders if o.get("work_order_id") == work_order_id]

    if not matched and orders:

        latest = max(orders, key=lambda o: o.get("created_at", ""))

        matched = [latest]



    if matched:

        print("  ✓ 找到工单记录:\n")

        for o in matched:

            print(pretty_json(o))

    else:

        print("  ⚠ HIGH 风险但未在索引中匹配到工单，请检查 create_work_order 节点。")



    recent = sorted(orders, key=lambda o: o.get("created_at", ""), reverse=True)[:3]

    if recent:

        print("\n  最近工单（最多 3 条）:")

        for o in recent:

            print(

                f"    - {o.get('work_order_id')} | {o.get('device_id')} | "

                f"{o.get('fault_type')} | {o.get('risk_level')} | {o.get('status')}"

            )





def main() -> int:

    banner("Industrial Fault Diagnosis Agent — Timeline E2E")

    print(f"  时间     : {datetime.now().isoformat(timespec='seconds')}")

    print(f"  API      : {API_BASE_URL}")

    print(f"  日志文件 : {LOG_FILE_PATH}")

    print(f"  故障码   : {FAULT_CODE or '(空，从时间线推断)'}")



    try:

        check_api_health()

        file_id = upload_log(Path(LOG_FILE_PATH))

        result = run_diagnosis(file_id, FAULT_CODE)

        print_diagnosis_summary(result)

        sub_banner("3b. 时间线断言")

        assert_timeline_expectations(result, FAULT_CODE)

        print_trace(result)



        diagnosis_id = result.get("diagnosis_id")

        detail = {}

        if diagnosis_id:

            detail = fetch_diagnosis_detail(diagnosis_id)



        check_work_orders(

            risk_level=result.get("risk_level", ""),

            work_order_id=detail.get("work_order_id"),

            diagnosis_id=diagnosis_id or "",

        )



        banner("测试完成")

        print("  链路: 上传时间线日志 → parse_timeline → 趋势 → 多码 Tool → 演化 → RAG → 工单(可选)")

        print(f"  前端详情页: http://localhost:3001/diagnosis/{diagnosis_id}")

        return 0



    except requests.ConnectionError:

        print("\n✗ 无法连接 API，请先启动后端:")

        print("  cd backend && .venv\\Scripts\\uvicorn app.main:app --reload --port 8001")

        return 1

    except FileNotFoundError as e:

        print(f"\n✗ {e}")

        return 1

    except requests.HTTPError as e:

        print(f"\n✗ HTTP 错误: {e}")

        return 1

    except Exception as e:

        print(f"\n✗ 未预期错误: {e}")

        raise





if __name__ == "__main__":

    sys.exit(main())

