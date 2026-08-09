import os
from typing import TypedDict
from llm_client import llm_call, llm_call_structured
import chromadb
from sentence_transformers import SentenceTransformer
from prompts import get_llm_prompt, get_direct_prompt

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'corpus')
CHROMA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'chroma')
COLLECTION_NAME = "zepto_policies"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

MOCK_LLM = os.getenv("MOCK_LLM", "1") == "1"
TOP_K = 3
SNIPPET_LENGTH = 200

POLICY_KEYWORDS = {
    "delivery", "return", "refund", "membership",
    "tracking", "cancel", "gift card", "support hours"
}

MODEL = SentenceTransformer(EMBEDDING_MODEL)
CLIENT = chromadb.PersistentClient(path=CHROMA_DIR)
COLLECTION = CLIENT.get_collection(name=COLLECTION_NAME)


class GraphState(TypedDict):
    query: str
    intent: str
    retrieved_context: list[dict]
    answer: str
    sources: list[str]
    confidence: float


def classify_intent(state: GraphState) -> GraphState:
    query = state["query"].lower()

    if MOCK_LLM:
        if any(key in query for key in POLICY_KEYWORDS):
            intent = "policy_question"
        else:
            intent = "general_question"
    else:
        system_prompt = f"""
            Classify the following query as exactly one word: either 'policy_question' (if it relates to zepto delivery,
            returns, refunds, membership, tracking, cancellations, gift cards or support hours), or 'general_question' (anything else).
            
            Query: {query}.

            Answer with only the single classification word.
        """
        intent = llm_call(system_prompt).strip().lower()

    return {
        **state,
        "intent": intent
    }


def retrieve_and_answer(state: GraphState) -> GraphState:
    model = MODEL
    query = state["query"]
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    ).tolist()

    collection = COLLECTION

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=TOP_K
    )

    retrieved_context = []
    ids = results["ids"][0]
    docs = results["documents"][0]
    metadatas = results["metadatas"][0]

    for chunk_id, text, metadata in zip(ids, docs, metadatas):
        retrieved_context.append({
            "chunk_id": chunk_id,
            "doc_id": metadata.get("doc_id", ""),
            "text": text
        })

    if not retrieved_context:
        return {
            **state,
            "answer": "No relevant policy information was found.",
            "retrieved_context": [],
            "sources": [],
            "confidence": 0.0
        }

    if MOCK_LLM:
        top_chunk_snippet = retrieved_context[0]["text"][:SNIPPET_LENGTH]
        answer = f"Based on the retrieved context: {top_chunk_snippet}..."
        sources = [chunk["chunk_id"] for chunk in retrieved_context]
        confidence = 1.0
    else:
        prompt = get_llm_prompt(
            retrieved_context=retrieved_context,
            user_query=query
        )
        llm_response = llm_call_structured(prompt)

        answer = llm_response["answer"]
        sources = llm_response["sources"]
        confidence = llm_response["confidence"]

    return {
        **state,
        "answer": answer,
        "retrieved_context": retrieved_context,
        "sources": sources,
        "confidence": confidence
    }


def direct_answer(state: GraphState) -> GraphState:
    query = state["query"]

    if MOCK_LLM:
        answer = "I can only answer questions about Zepto policies right now."
        sources = []
        confidence = 1.0

    else:
        prompt = get_direct_prompt(user_query=state["query"])
        response = llm_call_structured(prompt)
        answer = response["answer"]
        sources = response["sources"]
        confidence = response["confidence"]

    return {
        **state,
        "answer": answer,
        "retrieved_context": [],
        "sources": sources,
        "confidence": confidence
    }
