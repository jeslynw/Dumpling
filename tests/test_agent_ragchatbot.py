from pathlib import Path
import sys
import types
import importlib

import pytest


# Ensure backend/app imports resolve when pytest runs from SmartNotebook root.
ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
	sys.path.insert(0, str(BACKEND_DIR))


def _clear_test_modules():
	for name in [
		"app.tools.tools_ragchatbot",
		"app.agents.agent_ragchatbot",
		"app.api.routers.chat",
		"app.core.config",
	]:
		if name in sys.modules:
			del sys.modules[name]


def _install_service_stubs(monkeypatch):
	config_mod = types.ModuleType("app.core.config")
	config_mod.RAG_TOP_K_EVAL = 10
	config_mod.TAVILY_API_KEY = None
	monkeypatch.setitem(sys.modules, "app.core.config", config_mod)

	openai_mod = types.ModuleType("app.services.openai")

	class _LLM:
		def invoke(self, _prompt):
			class _Resp:
				content = ""

			return _Resp()

	openai_mod.openai_llm = _LLM()
	openai_mod.openai_vision = _LLM()
	openai_mod.openai_embeddings = object()
	monkeypatch.setitem(sys.modules, "app.services.openai", openai_mod)

	qdrant_mod = types.ModuleType("app.services.qdrant")

	class _QdrantClientStub:
		def collection_exists(self, _name):
			return True

	def _sanitize_name(name: str) -> str:
		return "".join(c for c in name.lower() if c.isalnum() or c == "_")

	qdrant_mod.qdrant = _QdrantClientStub()
	qdrant_mod.sanitize_name = _sanitize_name
	qdrant_mod.get_existing_collections = lambda: ["notes"]
	qdrant_mod.search_hybrid_qdrant_with_sources = (
		lambda query, top_k=5, collection_name="default", file_id=None: []
	)
	monkeypatch.setitem(sys.modules, "app.services.qdrant", qdrant_mod)


def _import_tools(monkeypatch):
	_clear_test_modules()
	_install_service_stubs(monkeypatch)
	return importlib.import_module("app.tools.tools_ragchatbot")


def _import_rag(monkeypatch):
	_clear_test_modules()
	_install_service_stubs(monkeypatch)
	return importlib.import_module("app.agents.agent_ragchatbot")


def test_pick_relevant_folders_parses_json_array(monkeypatch):
	tools = _import_tools(monkeypatch)

	class _Resp:
		content = '["wildlife_ducks", "tokyo_travel"]'

	monkeypatch.setattr(tools.openai_llm, "invoke", lambda _prompt: _Resp())

	registry = {
		"wildlife_ducks": {"description": "duck sightings and notes"},
		"tokyo_travel": {"description": "japan trip itinerary"},
	}
	folders = tools.pick_relevant_folders("ducks in parks", registry)
	assert folders == ["wildlife_ducks", "tokyo_travel"]


def test_search_folder_missing_collection_returns_message(monkeypatch):
	tools = _import_tools(monkeypatch)

	monkeypatch.setattr(tools.qdrant, "collection_exists", lambda _name: False)
	result = tools.search_folder("what is this", "missing_folder", top_k=3)
	assert result == "Folder 'missing_folder' does not exist."


def test_query_notebook_no_results_returns_empty_sources(monkeypatch):
	rag = _import_rag(monkeypatch)

	monkeypatch.setattr(
		rag,
		"build_rag_chatbot",
		lambda top_k=5: {
			"top_k": top_k,
			"folder_registry": {},
			"existing": {"notes"},
			"state": {"relevant_folders": [], "results": []},
			"executor": None,
			"tools": {},
		},
	)
	monkeypatch.setattr(rag, "pick_relevant_folders", lambda _q, _r: [])
	monkeypatch.setattr(rag, "_retrieve_across_folders", lambda _q, _f, _k: [])

	out = rag.query_notebook("where is my note?")
	assert out["answer"] == "I could not find relevant notes for this query."
	assert out["sources"] == []


def test_query_notebook_builds_answer_and_sources(monkeypatch):
	rag = _import_rag(monkeypatch)

	limited = [{"text": "alpha chunk", "source": "a.txt", "collection": "notes"}]

	monkeypatch.setattr(
		rag,
		"build_rag_chatbot",
		lambda top_k=5: {
			"top_k": top_k,
			"folder_registry": {"notes": {"description": "all notes"}},
			"existing": {"notes"},
			"state": {"relevant_folders": ["notes"], "results": limited},
			"executor": None,
			"tools": {},
		},
	)
	monkeypatch.setattr(rag, "_grade_chunks", lambda _q, _r: True)

	class _Resp:
		content = "answer from context"

	monkeypatch.setattr(rag.openai_llm, "invoke", lambda _prompt: _Resp())

	out = rag.query_notebook("what is alpha?")
	assert out["answer"] == "answer from context"
	assert out["sources"] == [{"source": "a.txt", "collection": "notes"}]


def test_query_notebook_does_not_use_web_if_notebook_had_hits(monkeypatch):
	rag = _import_rag(monkeypatch)

	calls = {"retrieve": 0, "web": 0}

	monkeypatch.setattr(
		rag,
		"build_rag_chatbot",
		lambda top_k=5: {
			"top_k": top_k,
			"folder_registry": {"notes": {"description": "all notes"}},
			"existing": {"notes"},
			"state": {"relevant_folders": ["notes"], "results": []},
			"executor": None,
			"tools": {},
		},
	)

	def _retrieve(_query, _folders, _top_k):
		calls["retrieve"] += 1
		if calls["retrieve"] == 1:
			return [{"text": "initial hit", "source": "n.md", "collection": "notes"}]
		return []

	monkeypatch.setattr(rag, "_retrieve_across_folders", _retrieve)
	monkeypatch.setattr(rag, "_grade_chunks", lambda _q, _rows: False)
	monkeypatch.setattr(rag, "_broaden_query", lambda q: f"broader: {q}")

	def _web(_query):
		calls["web"] += 1
		return [{"text": "web", "source": "https://x", "collection": "web_search"}]

	monkeypatch.setattr(rag, "_tavily_search", _web)

	out = rag.query_notebook("hard question")
	assert calls["web"] == 0
	assert out["answer"] == "I could not find relevant notes for this query."


def test_chat_router_smoke(monkeypatch):
	pytest.importorskip("fastapi")
	from fastapi import FastAPI
	from fastapi.testclient import TestClient

	_clear_test_modules()
	_install_service_stubs(monkeypatch)
	from app.api.routers import chat

	monkeypatch.setattr(
		chat,
		"search_rag_across_folders",
		lambda query, top_k=5: {
			"answer": f"ok: {query}",
			"sources": [{"source": "s.txt", "collection": "notes"}],
		},
	)

	app = FastAPI()
	app.include_router(chat.router)

	client = TestClient(app)
	resp = client.post("/chat/rag", json={"query": "hello", "top_k": 2})
	assert resp.status_code == 200
	payload = resp.json()
	assert payload["answer"] == "ok: hello"
	assert payload["sources"] == [{"source": "s.txt", "collection": "notes"}]
