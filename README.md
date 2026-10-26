# CyberIncident AI – Cybersecurity Incident Analysis Report System

## Overview

CyberIncident AI is an AI-powered cybersecurity incident analysis system developed to help users analyze security incidents and generate structured incident reports.

The system combines Natural Language Processing (NLP), Named Entity Recognition (NER), information retrieval, Retrieval-Augmented Generation (RAG), and a Large Language Model (LLM) to extract important information from incident reports, identify potential security threats, and provide recommendations.

The application provides an interactive web interface built using Streamlit.

## Live Application

Try the deployed application here:

https://cyberincident-ai.streamlit.app/

## Objectives

- Analyze cybersecurity incident reports.
- Extract important entities and security indicators.
- Identify attack types and affected systems.
- Retrieve relevant cybersecurity guidance.
- Generate AI-assisted incident summaries and recommendations.
- Evaluate information extraction and retrieval performance.

## Key Features

### 1. Incident Analysis
Analyzes cybersecurity incident descriptions and uploaded reports to identify important information.

### 2. Named Entity Recognition
Uses spaCy NER to extract relevant entities from incident descriptions.

### 3. TF-IDF Retrieval
Uses TF-IDF-based text retrieval to identify relevant information from available incident data.

### 4. Retrieval-Augmented Generation
Uses a cybersecurity knowledge base to retrieve relevant guidance that supports incident analysis.

### 5. Gemini AI Integration
Uses the Gemini API to generate structured incident analysis and security recommendations.

### 6. File Upload
Supports incident-report inputs through the formats implemented in the application, including PDF, TXT, CSV, and JSON.

### 7. Risk and Impact Analysis
Presents incident severity, attack information, possible impacts, and recommended actions.

### 8. Evaluation Dashboard
Provides evaluation information related to entity extraction, attack classification, retrieval quality, and response performance, according to the implemented evaluation pipeline.

## Technologies Used

- Python
- Streamlit
- Google Gemini API
- spaCy
- Scikit-learn
- TF-IDF
- Retrieval-Augmented Generation (RAG)
- Natural Language Processing (NLP)
- ChromaDB and FAISS for vector-based retrieval components
- PyPDF for PDF processing

## System Workflow

1. The user enters an incident description or uploads an incident report.
2. The application preprocesses the input.
3. NLP and NER techniques extract relevant information.
4. TF-IDF and retrieval components identify relevant information.
5. The RAG component retrieves relevant cybersecurity guidance.
6. Gemini AI generates an incident analysis and recommendations.
7. The application displays the results through the Streamlit interface.
8. Evaluation components present relevant performance metrics.

## Project Structure

```text
Cybersecurity-Incident-Report-System/
│
├── app.py
├── app_backup.py
├── evaluation.py
├── evaluation_results.json
├── requirements.txt
│
├── src/
│   ├── gemini_connection_test.py
│   ├── gemini_llm.py
│   ├── ner.py
│   ├── preprocessing.py
│   ├── rag.py
│   └── tfidf_retrieval.py
│
├── data/
├── assets/
└── .streamlit/
