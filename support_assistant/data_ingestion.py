import os
import chromadb
from sentence_transformers import SentenceTransformer

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'corpus')
CHROMA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'chroma')
COLLECTION_NAME = "zepto_policies"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class DocumentIngestor:
    def __init__(self, data_dir=DATA_DIR, chroma_dir=CHROMA_DIR, collection_name=COLLECTION_NAME,
                 embedding_model=EMBEDDING_MODEL):
        self.data_dir = data_dir
        self.chroma_dir = chroma_dir
        self.collection_name = collection_name
        self.embedding_model = embedding_model

        self.client = chromadb.PersistentClient(path=self.chroma_dir)
        try:
            self.client.delete_collection(name=self.collection_name)
        except:
            pass
        self.collection = self.client.get_or_create_collection(name=self.collection_name,
                                                               metadata={"hnsw:space": "cosine"})

        self.model = SentenceTransformer(self.embedding_model)

    def load_documents(self):
        documents = []
        for file in sorted(os.listdir(self.data_dir)):
            if file.endswith(".txt"):
                with open(os.path.join(self.data_dir, file), "r", encoding="utf-8") as f:
                    text = f.read().strip()
                    if not text:
                        print(f"Skipping empty file: {file}")
                        continue
                    content = {
                        "id": os.path.splitext(file)[0],
                        "text": text
                    }
                    documents.append(content)
        return documents

    def chunk_documents(self, documents):
        chunks = []
        for doc in documents:
            chunk = {
                "id": doc["id"],
                "text": doc["text"]
            }
            chunks.append(chunk)
        return chunks

    def generate_embeddings(self, chunks):
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True
        )
        return embeddings

    def store_embeddings(self, chunks, embeddings):
        ids = [chunk["id"] for chunk in chunks]

        documents = [chunk["text"] for chunk in chunks]
        metadatas = [{
            "doc_id": chunk["id"]
        } for chunk in chunks]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

    def build_vector_database(self):
        documents = self.load_documents()
        print(f"Loaded {len(documents)} documents.")
        chunks = self.chunk_documents(documents)
        print(f"Chunked documents into {len(chunks)} chunks.")
        embeddings = self.generate_embeddings(chunks)
        print(f"Generated embeddings for {len(chunks)} document chunks.")
        self.store_embeddings(chunks, embeddings)
        print("Generated and stored embeddings in vector database.")

        return self.collection


if __name__ == "__main__":
    ingestor = DocumentIngestor()
    collection = ingestor.build_vector_database()

    print(f"\n\nVector database built with {collection.count()} documents.")
