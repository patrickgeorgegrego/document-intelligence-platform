import threading
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer
from .scraper import BookScraper
from .rag_service import RAGPipeline

class BookListView(viewsets.ReadOnlyModelViewSet):
    """Phase 3: Standard List/Retrieve capabilities."""
    queryset = Book.objects.all().order_by('-created_at')
    serializer_class = BookSerializer

class ProcessView(APIView):
    """Phase 3: Asynchronous Scraper Trigger to prevent API timeouts."""
    def post(self, request):
        def background_job():
            scraper = BookScraper()
            books_data = scraper.scrape_books(num_books=5)
            scraper.save_books_to_db(books_data)
            rag_pipeline = RAGPipeline()
            for book in Book.objects.all():
                try:
                    rag_pipeline.vector_store.add_book(book)
                except Exception as e:
                    print(f"Error indexing {book.id}: {e}")
        
        # Dispatch background thread
        thread = threading.Thread(target=background_job)
        thread.start()
        
        return Response({"message": "Scraping and processing started asynchronously."}, status=status.HTTP_202_ACCEPTED)

class ChatView(APIView):
    """Phase 3: Custom View that takes a prompt and optional book_id, runs RAG, and returns response."""
    def post(self, request):
        prompt = request.data.get('prompt')
        book_id = request.data.get('book_id')
        if not prompt:
            return Response({"error": "No prompt provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        rag_pipeline = RAGPipeline()
        try:
            result = rag_pipeline.query(prompt, book_id=book_id)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InsightView(APIView):
    """Phase 3: Generates Summary and Genre using LLM for a specific book."""
    def post(self, request):
        book_id = request.data.get('book_id')
        if not book_id:
            return Response({"error": "book_id required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            book = Book.objects.get(id=book_id)
            rag_pipeline = RAGPipeline()
            insight = rag_pipeline.generate_insights(book)
            return Response(insight, status=status.HTTP_200_OK)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
