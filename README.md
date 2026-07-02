# 🤖 AI Candidate Ranking System

An AI-powered candidate ranking system that evaluates resumes against a job description using a hybrid pipeline of rule-based scoring, embeddings, reranking, and LLM-based reasoning.

---

## 🚀 What this project does

This system automatically ranks job candidates by analyzing:

- Candidate resumes (JSONL format)
- Job description (DOCX format)

It produces a final ranked list of candidates with scores and explanations.

---

## ⚙️ Pipeline Overview

1. Parse Job Description using LLM (Gemini)
2. Extract structured requirements (skills, tools, concepts)
3. Score candidates based on:
   - Experience match
   - Skill relevance
   - Career history quality
   - Behavioral signals
   - Availability (notice period, relocation)
4. Compute average score across signals
5. Apply percentile-based filtering (reduce candidate pool)
6. Semantic reranking using BAAI reranker model
7. LLM-based reasoning for final evaluation
8. Export final ranked results as CSV

---

## 🏗️ Tech Stack

- FastAPI (Backend API)
- Streamlit (Frontend UI)
- Google Gemini (LLM reasoning)
- LangChain (LLM orchestration)
- BAAI/bge-small-en-v1.5 (Embeddings)
- BAAI/bge-reranker-v2-m3 (Reranking model)
- Pandas (data processing)
- JSONL + CSV (data format)

---

## 📁 Project Structure

Graph/
  builder.py
  response_node.py
  state.py
  prompts.py

outputs/
  intermediate scoring JSONL files

final_outputs/
  final_candidates.csv

uploads/
  candidates.jsonl
  job_description.docx

main.py
app.py
parser.py
models.py
ingestion.py
requirements.txt

---

## ▶️ How to Run

### 1. Install dependencies
pip install -r requirements.txt

### 2. Start FastAPI backend
uvicorn main:app --reload

### 3. Start Streamlit frontend
streamlit run app.py

---

## 📌 API Endpoint

POST /upload

### Input:
- candidates: JSONL file
- job_description: DOCX file

### Output:
- Ranked candidates list with scores and reasoning

---

## 📤 Output Format

final_outputs/final_candidates.csv

Columns:
- candidate_id
- rank
- score
- reasoning

---

## 💡 Key Features

- Multi-stage AI ranking pipeline
- Hybrid scoring (rules + ML + LLM)
- Semantic reranking for accuracy
- Explainable AI-based decisions
- Scalable candidate filtering system
- Modular graph-based architecture

---

## ⚠️ Notes

- Requires Google Gemini API key
- Input must follow correct JSONL format
- Works best for batch resume ranking

---

## 👨‍💻 Author

Built as an AI-powered recruitment intelligence system for automated candidate ranking and evaluation.