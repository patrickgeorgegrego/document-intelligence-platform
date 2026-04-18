import os
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
from django.conf import settings

# Usually it's better to store ChromaDB in the data/ or backend/ directory.
CHROMA_DB_DIR = os.path.join(settings.BASE_DIR, 'chroma_db')

class BookVectorStore:
    def __init__(self):
        # We use a PersistentClient so embeddings are saved across server restarts.
        self.client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        
        # Default embedding function runs sentence-transformers all-MiniLM-L6-v2 model 
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        self.collection = self.client.get_or_create_collection(
            name="books_collection",
            embedding_function=self.embedding_function
        )
        
        # 500-char window with 50-char overlap as specified
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            is_separator_regex=False,
        )

    def add_book(self, book):
        """Chunks a book description and adds it to ChromaDB."""
        if not book.description or book.description == "No description available.":
            return
            
        chunks = self.text_splitter.split_text(book.description)
        
        ids = [f"book_{book.id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "book_id": book.id,
                "title": book.title, 
                "author": book.author,
                "url": book.url
            } for _ in range(len(chunks))
        ]
        
        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )

    def search(self, query, top_k=3):
        """Searches for top 3 matching chunks in the vector store."""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        return results
