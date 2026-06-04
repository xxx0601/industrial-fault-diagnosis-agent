# Agent Trace

## Trace step schema

| Field | Description |
|-------|-------------|
| `step` | Order index |
| `node` | e.g. `parse_timeline`, `tool_call` |
| `message` | Human-readable summary |
| `status` | `success` / error |
| `metadata` | Params, tool I/O, RAG hits |

## Implementation

- **Mapper:** `app/agent/trace/mapper.py`
- **Mock builder:** `app/agent/trace/builder.py`
- **LangGraph helpers:** `app/agent/backends/langgraph/trace_helpers.py`
- **UI:** `frontend/src/components/agent-trace/trace-timeline.tsx`

Persisted in `execution_meta.final_state` on each diagnosis record.
