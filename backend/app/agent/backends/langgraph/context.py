"""Runtime dependencies injected into LangGraph nodes via RunnableConfig."""

from typing import Any

from langchain_core.runnables import RunnableConfig

from app.core.config import Settings
from app.repositories.work_order_repo import WorkOrderRepository
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.upload_service import UploadService
from app.tools.executor import ToolExecutor

CONFIG_UPLOAD_SERVICE = "upload_service"
CONFIG_KNOWLEDGE_SERVICE = "knowledge_base_service"
CONFIG_SETTINGS = "settings"
CONFIG_TOOL_EXECUTOR = "tool_executor"
CONFIG_WORK_ORDER_REPO = "work_order_repo"


def get_upload_service(config: RunnableConfig) -> UploadService:
    configurable: dict[str, Any] = config.get("configurable") or {}
    service = configurable.get(CONFIG_UPLOAD_SERVICE)
    if service is None:
        raise ValueError(f"Missing configurable '{CONFIG_UPLOAD_SERVICE}' for LangGraph run")
    return service


def get_knowledge_service(config: RunnableConfig) -> KnowledgeBaseService:
    configurable: dict[str, Any] = config.get("configurable") or {}
    service = configurable.get(CONFIG_KNOWLEDGE_SERVICE)
    if service is None:
        raise ValueError(f"Missing configurable '{CONFIG_KNOWLEDGE_SERVICE}'")
    return service


def get_settings_from_config(config: RunnableConfig) -> Settings:
    configurable: dict[str, Any] = config.get("configurable") or {}
    settings = configurable.get(CONFIG_SETTINGS)
    if settings is None:
        raise ValueError(f"Missing configurable '{CONFIG_SETTINGS}'")
    return settings


def get_tool_executor(config: RunnableConfig) -> ToolExecutor:
    configurable: dict[str, Any] = config.get("configurable") or {}
    executor = configurable.get(CONFIG_TOOL_EXECUTOR)
    if executor is None:
        raise ValueError(f"Missing configurable '{CONFIG_TOOL_EXECUTOR}'")
    return executor


def get_work_order_repo(config: RunnableConfig) -> WorkOrderRepository:
    configurable: dict[str, Any] = config.get("configurable") or {}
    repo = configurable.get(CONFIG_WORK_ORDER_REPO)
    if repo is None:
        raise ValueError(f"Missing configurable '{CONFIG_WORK_ORDER_REPO}'")
    return repo


def get_tool_run_context(state: dict, config: RunnableConfig):
    from app.tools.base import ToolContext

    upload = get_upload_service(config)
    knowledge = get_knowledge_service(config)
    work_orders = get_work_order_repo(config)
    return ToolContext(
        file_id=state.get("file_id", ""),
        device_id=state.get("device_id"),
        parsed_data=state.get("parsed_data") or {},
        fault_code=state.get("fault_code"),
        upload_service=upload,
        knowledge_service=knowledge,
        work_order_repo=work_orders,
    )


def build_run_config(
    upload_service: UploadService,
    knowledge_service: KnowledgeBaseService,
    settings: Settings,
    tool_executor: ToolExecutor,
    work_order_repo: WorkOrderRepository,
) -> RunnableConfig:
    return {
        "configurable": {
            CONFIG_UPLOAD_SERVICE: upload_service,
            CONFIG_KNOWLEDGE_SERVICE: knowledge_service,
            CONFIG_SETTINGS: settings,
            CONFIG_TOOL_EXECUTOR: tool_executor,
            CONFIG_WORK_ORDER_REPO: work_order_repo,
        }
    }
