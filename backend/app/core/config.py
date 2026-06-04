"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="Industrial Fault Diagnosis API", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")

    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8001, alias="API_PORT")

    cors_origins: str = Field(
        default="http://localhost:3001,http://127.0.0.1:3001",
        alias="CORS_ORIGINS",
    )

    upload_dir: str = Field(default="uploads", alias="UPLOAD_DIR")
    upload_index_path: str = Field(
        default="data/uploads_index.json",
        alias="UPLOAD_INDEX_PATH",
    )
    upload_max_bytes: int = Field(default=10 * 1024 * 1024, alias="UPLOAD_MAX_BYTES")
    allowed_upload_extensions: str = Field(
        default="txt,csv,json",
        alias="ALLOWED_UPLOAD_EXTENSIONS",
    )

    agent_backend: str = Field(default="langgraph", alias="AGENT_BACKEND")
    diagnosis_index_path: str = Field(
        default="data/diagnosis_index.json",
        alias="DIAGNOSIS_INDEX_PATH",
    )
    work_order_index_path: str = Field(
        default="data/work_orders_index.json",
        alias="WORK_ORDER_INDEX_PATH",
    )

    rag_enabled: bool = Field(default=True, alias="RAG_ENABLED")
    chroma_persist_dir: str = Field(default="data/chroma", alias="CHROMA_PERSIST_DIR")
    chroma_collection: str = Field(
        default="fault_diagnosis_knowledge",
        alias="CHROMA_COLLECTION",
    )
    knowledge_files_dir: str = Field(default="knowledge_files", alias="KNOWLEDGE_FILES_DIR")
    knowledge_index_path: str = Field(
        default="data/knowledge_index.json",
        alias="KNOWLEDGE_INDEX_PATH",
    )
    knowledge_max_bytes: int = Field(default=20 * 1024 * 1024, alias="KNOWLEDGE_MAX_BYTES")
    rag_chunk_size: int = Field(default=800, alias="RAG_CHUNK_SIZE")
    rag_chunk_overlap: int = Field(default=100, alias="RAG_CHUNK_OVERLAP")
    rag_default_top_k: int = Field(default=5, alias="RAG_DEFAULT_TOP_K")
    knowledge_allowed_extensions: str = Field(
        default="pdf,txt",
        alias="KNOWLEDGE_ALLOWED_EXTENSIONS",
    )
    vector_store_backend: str = Field(default="auto", alias="VECTOR_STORE_BACKEND")
    memory_vector_index_path: str = Field(
        default="data/memory_vectors.json",
        alias="MEMORY_VECTOR_INDEX_PATH",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def allowed_extension_set(self) -> set[str]:
        return {
            ext.strip().lower().lstrip(".")
            for ext in self.allowed_upload_extensions.split(",")
            if ext.strip()
        }

    @property
    def knowledge_extension_set(self) -> set[str]:
        return {
            ext.strip().lower().lstrip(".")
            for ext in self.knowledge_allowed_extensions.split(",")
            if ext.strip()
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
