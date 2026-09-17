import os
import io
import numpy as np
import faiss
import pdfplumber
from pypdf import PdfReader
from typing import List, Dict, Any, Tuple
from google import genai
from google.genai import types

class RAGAssistant:
    def __init__(self, google_api_key: str):
        self.client = genai.Client(api_key=google_api_key)
        self.vector_store: faiss.IndexFlatL2 = None
        self.document_chunks: List[Dict[str, Any]] = []

    def _get_embedding(self, text: str) -> List[float]:
        """
        Tries text-embedding-004 and fallbacks across valid API model formats.
        """
        candidate_models = [
            "text-embedding-004",
            "models/text-embedding-004",
            "gemini-embedding-001",
            "models/gemini-embedding-001"
        ]

        last_exception = None
        for model_name in candidate_models:
            try:
                res = self.client.models.embed_content(
                    model=model_name,
                    contents=text
                )
                
                # Extract vector values safely across SDK response structures
                if hasattr(res, 'embedding'):
                    emb = res.embedding
                    if hasattr(emb, 'values'):
                        return list(emb.values)
                    return list(emb)
                elif hasattr(res, 'embeddings') and res.embeddings:
                    emb = res.embeddings[0]
                    if hasattr(emb, 'values'):
                        return list(emb.values)
                    return list(emb)
                elif isinstance(res, dict) and 'embedding' in res:
                    return res['embedding']

            except Exception as e:
                last_exception = e
                continue

        raise RuntimeError(f"Failed to generate embeddings across all model aliases. Last error: {last_exception}")
    def _extract_text_from_pdf(self, filename: str, content: bytes) -> List[Dict[str, Any]]:
        pages_data = []
        
        # Primary parsing with pdfplumber
        try:
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for idx, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        pages_data.append({
                            "source_file": filename,
                            "page_number": idx + 1,
                            "text": text.strip()
                        })
        except Exception as e:
            print(f"pdfplumber extraction note for {filename}: {e}")

        # Fallback parsing with PyPDF
        if not pages_data:
            try:
                reader = PdfReader(io.BytesIO(content))
                for idx, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        pages_data.append({
                            "source_file": filename,
                            "page_number": idx + 1,
                            "text": text.strip()
                        })
            except Exception as e:
                print(f"PyPDF extraction error for {filename}: {e}")

        return pages_data

    def _chunk_text(self, pages_data: List[Dict[str, Any]], chunk_size: int = 1000, overlap: int = 150) -> List[Dict[str, Any]]:
        chunks = []
        for page_info in pages_data:
            text = page_info["text"]
            start = 0
            while start < len(text):
                end = start + chunk_size
                chunk_str = text[start:end]
                chunks.append({
                    "text": chunk_str,
                    "source_file": page_info["source_file"],
                    "page_number": page_info["page_number"]
                })
                start += (chunk_size - overlap)
        return chunks

    def process_pdfs(self, file_tuples: List[Tuple[str, bytes]]) -> Dict[str, Any]:
        all_pages = []
        
        for filename, content in file_tuples:
            if not filename.lower().endswith(".pdf"):
                raise ValueError(f"Unsupported file format: {filename}. Only PDFs are allowed.")
            
            pages = self._extract_text_from_pdf(filename, content)
            all_pages.extend(pages)

        if not all_pages:
            raise ValueError("Could not extract readable text from the uploaded PDF(s).")

        self.document_chunks = self._chunk_text(all_pages)

        # Generate Embeddings
        embeddings_list = []
        for chunk in self.document_chunks:
            emb = self._get_embedding(chunk["text"])
            embeddings_list.append(emb)

        embeddings_np = np.array(embeddings_list, dtype=np.float32)

        # Build FAISS vector database
        embedding_dim = embeddings_np.shape[1]
        self.vector_store = faiss.IndexFlatL2(embedding_dim)
        self.vector_store.add(embeddings_np)

        return {
            "processed_files": list(set([f[0] for f in file_tuples])),
            "total_chunks": len(self.document_chunks)
        }

    def answer_question(self, question: str) -> Dict[str, Any]:
        if not self.vector_store or not self.document_chunks:
            raise ValueError("No research papers have been uploaded or indexed yet.")

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        q_emb = self._get_embedding(question)
        q_np = np.array([q_emb], dtype=np.float32)

        # Retrieve top 5 matches
        k = min(5, len(self.document_chunks))
        _, indices = self.vector_store.search(q_np, k)

        retrieved_chunks = [self.document_chunks[i] for i in indices[0]]

        context_text = "\n\n---\n\n".join([
            f"Source: {c['source_file']} (Page {c['page_number']})\nContent: {c['text']}"
            for c in retrieved_chunks
        ])

        system_prompt = (
            "You are a strict research paper assistant. Answer the user's question USING ONLY the provided context below.\n"
            "If the information required to answer the question is not present in the provided context, state clearly:\n"
            "\"The requested information is not available in the uploaded research papers.\"\n"
            "Do NOT use external knowledge or fabricate information under any circumstances.\n\n"
            f"Context:\n{context_text}"
        )

        # Updated candidate generation models list including Gemini 3.6 and 3.5
        candidate_gen_models = [
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-2.5-flash",
            "gemini-1.5-flash-latest"
        ]

        response = None
        last_error = None
        for model_name in candidate_gen_models:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=[system_prompt, f"Question: {question}"],
                    config=types.GenerateContentConfig(temperature=0.0)
                )
                if response:
                    break
            except Exception as e:
                last_error = e
                continue

        if not response:
            raise RuntimeError(f"Could not generate answer with available Gemini models. Error: {last_error}")

        sources = [
            {
                "source_file": c["source_file"],
                "page_number": c["page_number"]
            }
            for c in retrieved_chunks
        ]
        unique_sources = [dict(t) for t in {tuple(d.items()) for d in sources}]

        return {
            "question": question,
            "answer": response.text,
            "sources": unique_sources
        }