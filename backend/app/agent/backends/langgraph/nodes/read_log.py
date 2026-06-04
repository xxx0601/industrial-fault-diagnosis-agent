from langchain_core.runnables import RunnableConfig

from app.agent.backends.langgraph.context import get_upload_service
from app.agent.backends.langgraph.state import DiagnosisState
from app.agent.backends.langgraph.trace_helpers import make_trace_entry
from app.agent.trace.mapper import NODE_READ_LOG


def read_log_node(state: DiagnosisState, config: RunnableConfig) -> dict:
    upload_service = get_upload_service(config)
    file_id = state["file_id"]
    log_content = upload_service.read_log_content(file_id)
    line_count = len([line for line in log_content.splitlines() if line.strip()])
    return {
        "log_content": log_content,
        "trace": [
            make_trace_entry(
                NODE_READ_LOG,
                "读取日志文件",
                metadata={"file_id": file_id, "line_count": line_count},
            )
        ],
    }
