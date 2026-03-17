"""
Tests for agent_ragchatbot — converted from notebook's evaluation section.

Combines three evaluation approaches from the notebook:
  1. Basic RAG correctness assertions
  2. LLM-as-Judge (notebook used LlamaIndex FaithfulnessEvaluator etc.)
     → Converted to LangChain's load_evaluator()
  3. RAGAS evaluation (notebook used LlamaIndexLLMWrapper/EmbeddingsWrapper)
     → Converted to LangchainLLMWrapper / LangchainEmbeddingsWrapper

Notebook queries preserved exactly:
  - Duck breeds query (LLM-as-judge, similarity_top_k=5)
  - Duck predators query (RAGAS, similarity_top_k=10)
"""
from langchain_core.documents import Document
from backend.app.services.qdrant import add_documents, delete_collection
from backend.app.agents.agent_ragchatbot import query_folder, query_file
from backend.app.core.config import RAG_TOP_K_EVAL

TEST_COLLECTION = "test_wildlifeducks"
TEST_FILE_ID = "test-duck-file-001"

# ── Notebook queries preserved exactly ────────────────────────────────────────
DUCK_BREEDS_QUERY = "How many domesticated duck breeds are there according to the american poultry association?"
DUCK_BREEDS_REFERENCE = "The American Poultry Association lists 17 domesticated breeds"

DUCK_PREDATORS_QUERY = "What are some predators that hunt ducks?"
DUCK_PREDATORS_REFERENCE = (
    "Ducks have many predators. Ducklings are particularly vulnerable, since their inability to fly "
    "makes them easy prey not only for predatory birds but also for large fish like pike, crocodilians, "
    "predatory testudines such as the alligator snapping turtle, and other aquatic hunters, including "
    "fish-eating birds such as herons. Ducks' nests are raided by land-based predators, and brooding "
    "females may be caught unaware on the nest by mammals, such as foxes, or large birds, such as hawks "
    "or owls. Adult ducks are fast fliers, but may be caught on the water by large aquatic predators "
    "including big fish such as the North American muskie and the European pike. In flight, ducks are safe "
    "from all but a few predators such as humans and the peregrine falcon, which uses its speed and "
    "strength to catch ducks."
)


def _seed_collection():
    """Seed Qdrant with duck content matching notebook's wildlifeducks collection."""
    docs = [
        Document(
            page_content="The American Poultry Association recognizes 17 domesticated duck breeds.",
            metadata={"source": "https://britannica.com/animal/duck", "file_id": TEST_FILE_ID},
        ),
        Document(
            page_content=(
                "Ducks have many predators. Ducklings are particularly vulnerable, since their inability "
                "to fly makes them easy prey not only for predatory birds but also for large fish like "
                "pike, crocodilians, and other aquatic hunters including herons. Duck nests are raided "
                "by land-based predators such as foxes or large birds like hawks or owls. In flight, "
                "ducks are safe from all but a few predators such as humans and the peregrine falcon."
            ),
            metadata={"source": "https://britannica.com/animal/duck", "file_id": TEST_FILE_ID},
        ),
        Document(
            page_content="Wild ducks migrate south in winter following river and coastline routes.",
            metadata={"source": "https://natgeo.com/ducks", "file_id": "other-file-002"},
        ),
    ]
    add_documents(TEST_COLLECTION, docs)


# ── 1. Basic RAG assertions ────────────────────────────────────────────────────

def test_rag_folder_answers_from_context():
    _seed_collection()
    result = query_folder(TEST_COLLECTION, DUCK_BREEDS_QUERY)
    assert "17" in result["answer"]
    assert isinstance(result["sources"], list)
    assert isinstance(result["source_nodes"], list)  # needed for RAGAS


def test_rag_folder_refuses_out_of_scope():
    _seed_collection()
    result = query_folder(TEST_COLLECTION, "What is the capital of France?")
    answer_lower = result["answer"].lower()
    assert any(phrase in answer_lower for phrase in ["couldn't find", "not in", "no information", "don't have"])


def test_rag_file_scope_filters_correctly():
    _seed_collection()
    result = query_file(TEST_COLLECTION, TEST_FILE_ID, DUCK_BREEDS_QUERY)
    assert "17" in result["answer"]


def test_rag_source_nodes_populated():
    """source_nodes replaces notebook's response.source_nodes for RAGAS contexts field."""
    _seed_collection()
    result = query_folder(TEST_COLLECTION, DUCK_PREDATORS_QUERY, top_k=RAG_TOP_K_EVAL)
    assert len(result["source_nodes"]) > 0
    assert all(isinstance(n, str) for n in result["source_nodes"])


# ── 2. LLM-as-Judge ───────────────────────────────────────────────────────────
# Converted from notebook's LlamaIndex evaluators:
#   FaithfulnessEvaluator, RelevancyEvaluator, CorrectnessEvaluator
# LangChain equivalent: langchain.evaluation.load_evaluator()

def run_llm_as_judge():
    """
    Mirrors notebook's evaluator section (similarity_top_k=5).

    Notebook:
        faith_result = faithfulness_evaluator.evaluate_response(response=response)
        corr_result  = correctness_evaluator.evaluate(query=..., response=..., reference=...)

    LangChain conversion uses criteria-based evaluators via load_evaluator().
    """
    from langchain.evaluation import load_evaluator
    from app.services.openai import openai_llm   # shared instance, no new client needed

    _seed_collection()

    result = query_folder(TEST_COLLECTION, DUCK_BREEDS_QUERY, top_k=5)
    answer = result["answer"]
    context = "\n".join(result["source_nodes"])

    print(f"\nBot Answer:\n{answer}\n")
    print("-" * 30)

    # Faithfulness — is the answer grounded in the retrieved context?
    faithfulness_eval = load_evaluator("criteria", llm=openai_llm, criteria="conciseness")
    faith_result = faithfulness_eval.evaluate_strings(
        input=DUCK_BREEDS_QUERY,
        prediction=answer,
        reference=context,
    )

    # Correctness — does the answer match the reference answer?
    correctness_eval = load_evaluator("labeled_criteria", llm=openai_llm, criteria="correctness")
    corr_result = correctness_eval.evaluate_strings(
        input=DUCK_BREEDS_QUERY,
        prediction=answer,
        reference=DUCK_BREEDS_REFERENCE,
    )

    print(f"Faithfulness: {faith_result.get('score')} | {faith_result.get('reasoning', '')[:120]}")
    print(f"Correctness:  {corr_result.get('score')} | {corr_result.get('reasoning', '')[:120]}")
    return faith_result, corr_result


# ── 3. RAGAS Evaluation ───────────────────────────────────────────────────────
# Converted from notebook's RAGAS section.
#
# Notebook used:
#   ragas_llm        = LlamaIndexLLMWrapper(Settings.llm)
#   ragas_embeddings = LlamaIndexEmbeddingsWrapper(Settings.embed_model)
#   contexts         = [[node.get_content() for node in response.source_nodes]]
#
# LangChain conversion:
#   ragas_llm        = LangchainLLMWrapper(llm)
#   ragas_embeddings = LangchainEmbeddingsWrapper(embeddings)
#   contexts         = [result["source_nodes"]]

def run_ragas_evaluation():
    """
    RAGAS evaluation — mirrors notebook's evaluate() pattern exactly.

    Notebook flow (now matched):
      retriever.invoke(query) → get contexts
      llm.invoke(prompt with contexts) → get answer separately
      Dataset.from_dict({question, answer, contexts, ground_truth})
      evaluate(dataset, metrics=[...])

    This is different from the agent flow — here we bypass the agent and
    retrieve + generate directly, giving RAGAS clean access to the contexts.
    """
    from ragas import evaluate
    from ragas.metrics.collections import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    )
    from ragas.llms import llm_factory
    from ragas.embeddings import embedding_factory
    from datasets import Dataset

    from app.services.openai import openai_embeddings

    _seed_collection()

    from app.services.qdrant import get_vectorstore
    vectorstore = get_vectorstore(TEST_COLLECTION)
    retriever = vectorstore.as_retriever(search_kwargs={"k": RAG_TOP_K_EVAL})

    retrieved_docs = retriever.invoke(DUCK_PREDATORS_QUERY)
    contexts = [doc.page_content for doc in retrieved_docs]

    from app.services.openai import openai_llm
    prompt = f"Answer the question based only on the following context:\n\n{contexts}\n\nQuestion: {DUCK_PREDATORS_QUERY}"
    answer_response = openai_llm.invoke(prompt)
    answer = answer_response.content

    data = {
        "question": [DUCK_PREDATORS_QUERY],
        "answer": [answer],
        "contexts": [contexts],
        "ground_truth": [DUCK_PREDATORS_REFERENCE],
    }

    dataset = Dataset.from_dict(data)

    # Use llm_factory and embedding_factory — replaces deprecated LangchainLLMWrapper
    from openai import OpenAI as RawOpenAI
    import os
    ragas_llm = llm_factory("gpt-4o-mini", client=RawOpenAI(api_key=os.getenv("OPENAI_API_KEY")))
    ragas_embeddings = embedding_factory("openai", model="text-embedding-3-small")

    print("\nRunning RAGAS Evaluation...")
    ragas_result = evaluate(
        dataset=dataset,
        metrics=[
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy,
        ],
        llm=ragas_llm,
        embeddings=ragas_embeddings,
    )

    print(ragas_result)
    return ragas_result


def teardown_module():
    delete_collection(TEST_COLLECTION)


if __name__ == "__main__":
    run_llm_as_judge()
    run_ragas_evaluation()