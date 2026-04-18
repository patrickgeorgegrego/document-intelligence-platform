import json
from openai import OpenAI
from .vector_store import BookVectorStore

# Memory cache for identical repeated LLM queries
_QUERY_CACHE = {}

class RAGPipeline:
    def __init__(self):
        self.vector_store = BookVectorStore()
        self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio") 

    def query(self, prompt, book_id=None):
        """Processes a chat query with strict source citations and caching."""
        cache_key = f"{prompt}_{book_id}"
        if cache_key in _QUERY_CACHE:
            return _QUERY_CACHE[cache_key]

        search_results = self.vector_store.search(prompt, top_k=3)
        context_chunks = []
        sources = set()
        
        if search_results and search_results.get('documents') and len(search_results['documents'][0]) > 0:
            for idx, document in enumerate(search_results['documents'][0]):
                metadata = search_results['metadatas'][0][idx]
                if book_id and str(metadata['book_id']) != str(book_id):
                    continue
                context_chunks.append(f"Excerpt from '{metadata['title']}':\n{document}")
                sources.add(metadata['title'])
                
        context = "\n\n".join(context_chunks)
        if not context:
            context = "No relevant context found in Vector DB."
            
        system_prompt = (
            "Use only the following context to answer the question. "
            "If the answer isn't in the context, say you don't know. "
            "At the end of your answer, list the Book Title used as a source."
        )
        
        try:
            response = self.client.chat.completions.create(
                model="local-model",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {prompt}"}
                ],
                temperature=0.3
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"⚠️ Connection Error: Failed to reach LM Studio inference at localhost:1234. Details: {str(e)}"
            
        formatted_sources = ", ".join(f"[{t}]" for t in list(sources))
        
        result = {
            "answer": answer,
            "sources": formatted_sources if formatted_sources else "No direct citations found."
        }
        
        # Cache the result
        _QUERY_CACHE[cache_key] = result
        return result

    def generate_insights(self, book):
        """Generates Summary and Genre Classification automatically for a book."""
        if not book.description or len(book.description) < 20:
            return {"summary": "Description too short.", "genre": book.genre}
            
        system_prompt = (
            "You are a taxonomy AI. Output exactly a JSON object containing "
            "'summary' (2 concise sentences) and 'genre' (a strict literary genre classification) "
            "based on the provided book description."
        )
        user_message = f"Description: {book.description}"
        
        try:
            response = self.client.chat.completions.create(
                model="local-model",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.2
            )
            answer = response.choices[0].message.content
            
            cleaned = answer.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            
            # Here you could save these dynamically back to the Book model 
            # (book.genre = data['genre']; book.save())
            
            return {
                "message": "Insights generated successfully.",
                "summary": data.get("summary", ""),
                "genre": data.get("genre", "")
            }
        except Exception as e:
            return {"error": f"Failed to generate insight: {e}", "raw": answer if 'answer' in locals() else ""}
