# 📚 Document Intelligence Platform

![Dashboard Preview](dashboard-screenshot.png)
*(Note: Please drop your actual dashboard screenshot as `dashboard-screenshot.png` in the root directory prior to submitting!)*

A comprehensive enterprise-grade platform built to ingest, chunk, and intelligently question large library datasets using an offline vector RAG approach.

## 🚀 Tech Stack & Architecture
- **Frontend:** Next.js 14+ (App Router), Tailwind CSS, Lucide-React
- **Backend:** Django REST Framework (DRF), Python Threading
- **Database:** MySQL (relational metadata), ChromaDB (Vector Search)
- **AI Integration:** LM Studio Local Inference (OpenAI-compatible) using `sentence-transformers/all-MiniLM-L6-v2`

---

## 💻 Installation

### 1. Prerequisites
Ensure you have **Python 3.10+**, **Node.js 18+**, and **LM Studio** installed. Start your Local Inference Server on port `1234` inside LM Studio using any LLM (e.g. Mistral 7B).

### 2. Backend Setup (Django & AI)
```bash
cd backend
python -m venv venv
# On Windows use: .\venv\Scripts\Activate.ps1
# On Mac/Linux use: source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### 3. Frontend Setup (Next.js)
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:3000` to interact with the Dashboard!

---

## 🔌 API Specs

| Method | Endpoint | Description |
|--------|------------------|-------------|
| **GET** | `/api/books/` | Retrieves the full catalog list and metadata of scraped books. |
| **POST** | `/api/process/` | Asynchronously triggers the Selenium scraper to index and chunk data into ChromaDB. |
| **POST** | `/api/chat/` | Evaluates a user prompt against local RAG Vectors and returns the optimal cited answer. |
| **POST** | `/api/insights/` | Prompts the AI dynamically for Summary and Genre evaluation on a specific `book_id`. |

---

## 🔎 Sample RAG Queries

Interact directly with the Q&A layout by running questions like these. The AI will cross-reference ChromaDB using strict semantic chunking and cite the sources!
1. *"What is the summary of A Light in the Attic?"*
2. *"What books are recommended for fans of mystery?"*
3. *"Can you identify books dealing with classical themes or poetry?"*
