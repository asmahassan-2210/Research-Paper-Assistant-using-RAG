# 📚 Research Paper Assistant using RAG

An AI-powered **Research Paper Assistant** built with **FastAPI, FAISS, Google Gemini, and Retrieval-Augmented Generation (RAG)**.

The application allows users to upload one or multiple research papers in **PDF format** and ask questions about their content. Relevant information is retrieved from the uploaded documents and provided to the Gemini model to generate answers grounded in the source material.

---

## 🌟 Key Features

* 📄 **Multi-PDF Upload**
  Upload and process one or multiple research papers simultaneously.

* 🔍 **Retrieval-Augmented Generation (RAG)**
  Combines semantic document retrieval with generative AI to provide context-aware answers.

* 📝 **PDF Text Extraction**
  Extracts research paper content page by page using `pdfplumber`, with `pypdf` available as a fallback parser.

* 🧩 **Intelligent Text Chunking**
  Splits extracted document content into smaller meaningful chunks for efficient retrieval.

* 🧠 **Vector Embeddings**
  Converts document chunks into vector representations using Google's embedding model.

* ⚡ **FAISS Vector Search**
  Uses Facebook AI Similarity Search (FAISS) for fast semantic similarity search across uploaded documents.

* 🤖 **Google Gemini Integration**
  Uses Gemini to generate natural-language responses based on the retrieved document context.

* 🛡️ **Hallucination Control**
  Prompt instructions encourage the model to answer only from the retrieved research-paper context and indicate when the required information is unavailable.

* 📑 **Source & Page Tracking**
  Retrieved information maintains the original PDF filename and page number, making it easier to verify answers.

* 💬 **Interactive Chat Interface**
  Users can ask multiple questions through a clean and responsive web-based chat interface.

* ⚡ **FastAPI Backend**
  Provides lightweight and efficient API endpoints for document processing and question answering.

---

## 🏗️ Project Architecture

```text
Research Paper Assistant/
│
├── main.py                  # FastAPI application, API endpoints & static routes
├── rag_engine.py            # RAG pipeline, PDF parsing, chunking, embeddings & FAISS
│
├── static/
│   ├── style.css            # Application styling
│   └── script.js            # Frontend JavaScript
│
├── templates/
│   └── index.html           # Web interface
│
├── requirements.txt         # Python dependencies
├── vercel.json              # Vercel deployment configuration
└── README.md                # Project documentation
```

---

## 🔄 How It Works

The application follows a Retrieval-Augmented Generation pipeline:

```text
        📄 Research Papers
               │
               ▼
       PDF Text Extraction
               │
               ▼
        Text Chunking
               │
               ▼
      Google Text Embeddings
               │
               ▼
        FAISS Vector Index
               │
               ▼
        User Question
               │
               ▼
      Similarity Retrieval
               │
               ▼
     Relevant Document Chunks
               │
               ▼
        Google Gemini
               │
               ▼
        🤖 Generated Answer
               │
               ▼
      📑 Source & Page Info
```

---

## 🛠️ Technologies Used

| Technology            | Purpose                         |
| --------------------- | ------------------------------- |
| **Python**            | Core programming language       |
| **FastAPI**           | Backend API and web server      |
| **FAISS**             | Vector similarity search        |
| **Google Gemini**     | AI-powered answer generation    |
| **Google Embeddings** | Document vector representations |
| **pdfplumber**        | Primary PDF text extraction     |
| **pypdf**             | PDF parsing fallback            |
| **HTML5**             | Frontend structure              |
| **CSS3**              | User interface styling          |
| **JavaScript**        | Frontend interaction            |
| **Vercel**            | Deployment configuration        |

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/research-paper-assistant.git
cd research-paper-assistant
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root directory and add your Google Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

> ⚠️ Never upload your `.env` file or API key to GitHub. Add `.env` to your `.gitignore` file.

---

## ▶️ Run the Application

Start the FastAPI development server with:

```bash
uvicorn main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

Open the address in your browser to access the Research Paper Assistant.

---

## 💡 Example Use Cases

The Research Paper Assistant can be used to:

* 📖 Understand complex research papers
* 🔍 Find specific information across multiple papers
* 🧠 Ask questions about research methodologies
* 📊 Compare information from different documents
* 📝 Summarize sections of research papers
* 🎓 Assist students with academic research
* 🔬 Explore findings, methodologies, and conclusions
* 📑 Locate information and its corresponding page

### Example Questions

```text
What is the main objective of this research?

What methodology was used in the study?

What were the key findings?

What dataset was used?

What limitations did the researchers mention?

According to the paper, what are the proposed future research directions?
```

---

## 🛡️ RAG-Based Grounding

Unlike a traditional chatbot that relies primarily on its general knowledge, this project retrieves relevant information from the **uploaded research papers** before generating an answer.

This approach helps:

1. Retrieve relevant document chunks.
2. Provide those chunks as context to Gemini.
3. Generate an answer based on the retrieved context.
4. Track the source document and page.
5. Indicate when the requested information cannot be found in the available documents.

This makes the application particularly useful for **document-based question answering and academic research**.

---

## 🚀 Future Improvements

Possible future enhancements include:

* 🔐 User authentication and document management
* 💾 Persistent vector database storage
* 📚 Support for additional document formats such as DOCX and TXT
* 🔄 Conversation history
* 📊 Research paper comparison mode
* 📝 Automatic paper summarization
* 📑 Improved citation formatting
* 🌐 Multi-language document support
* ☁️ Cloud-based document storage
* 🎯 More advanced retrieval and reranking techniques

---

## 📌 Project Highlights

This project demonstrates practical implementation of:

* Retrieval-Augmented Generation (RAG)
* Large Language Models (LLMs)
* Vector databases and similarity search
* Semantic embeddings
* PDF document processing
* Prompt engineering
* FastAPI API development
* Full-stack AI application development
* Source-aware AI responses

---

## 👩‍💻 Author

**Asma Hassan**

AI & Machine Learning Enthusiast | Python Developer | AI Application Developer

---

```

### ⭐ Project Summary

> **Research Paper Assistant** is a RAG-based AI application that enables users to upload research papers and ask questions about their content. It combines PDF processing, semantic embeddings, FAISS vector search, FastAPI, and Google Gemini to deliver context-grounded answers with source and page tracking.
```
