# 🤖 AI Chatbots and Agents Repository

A comprehensive collection of production-ready AI agents and chatbots built with cutting-edge LLM technologies including Google Gemini, Groq, LangChain, CrewAI, and LangGraph.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://www.langchain.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Agents & Chatbots Directory](#agents--chatbots-directory)
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Configuration](#configuration)
- [Contributing](#contributing)

---

## Overview

This repository showcases various AI agents and chatbots designed to solve real-world problems across different domains including content generation, document analysis, data extraction, and conversational AI. Each project is self-contained with its own dependencies and can be run independently.

### Key Features
- 🚀 Production-ready implementations
- 🎨 User-friendly Streamlit interfaces
- 🔧 Modular and extensible architecture
- 📚 Multiple LLM providers (Gemini, Groq)
- 💾 Persistent storage and state management
- 🌐 Multi-modal capabilities (text, images, PDFs)

---

## Agents & Chatbots Directory

| Agent/Chatbot Name | Use Case | Description | Technologies | Folder Link |
|-------------------|----------|-------------|--------------|-------------|
| **Data Analysis Agent** | Data Science & Analytics | AI-powered data analysis agent that performs comprehensive exploratory data analysis on CSV files. Automatically generates multiple visualizations including correlation heatmaps, pairplots, violin plots, histograms, box plots, and count plots. Uses Gemini 2.0 Flash vision model to analyze visualizations and provide intelligent insights. Features streaming responses, robust error handling with retry logic, and automatic encoding detection. | Chainlit, Gemini 2.0 Flash, Pandas, Matplotlib, Seaborn | [`Data Analysis Agent/`](./Data%20Analysis%20Agent) |
| **News Reporter AI Agent** | Automated Content Generation | Multi-agent system with researcher and writer agents that collaborate to generate comprehensive tech news articles. Uses web search for current information and produces markdown formatted reports. | CrewAI, Gemini 2.0 Flash, SERP API | [`News Reporter AI Agent/`](./News%20Reporter%20AI%20Agent) |
| **Resume ATS Analyzer** | Recruitment & HR Tech | AI-powered Applicant Tracking System that analyzes resumes against job descriptions, provides match percentages, identifies missing keywords, and offers professional evaluation. Processes PDFs as images using vision-capable LLMs. | Gemini 2.0 Flash (Vision), Streamlit, pdf2image | [`Resume ATS and Score Analyzer/`](./Resume%20ATS%20and%20Score%20Analyzer) |
| **Text to SQL LLM App** | Database Query Interface | Natural language to SQL converter that allows non-technical users to query databases using plain English. Demonstrates prompt engineering for code generation with strict output formatting. | Gemini 2.0 Flash, SQLite, Streamlit | [`Text to SQL LLM App/`](./Text%20to%20SQL%20LLM%20App) |
| **MultiPDF Chat Bot** | Document Q&A & Research | RAG-based chatbot that enables conversational interaction with multiple PDF documents. Uses vector embeddings for semantic search and retrieves relevant context for accurate answers. | LangChain, Gemini 2.0 Flash, FAISS, HuggingFace Embeddings | [`Chat with MultiPDF document/`](./Chat%20with%20MultiPDF%20document) |
| **Multilanguage Invoice Extractor** | Document Processing & Automation | Vision-based AI that extracts information from invoices in any language. Supports multilingual text recognition and structured data extraction without requiring OCR. | Gemini 2.0 Flash (Vision), Streamlit, PIL | [`Multilanguage Invoice Extractor/`](./Multilanguage%20Invoice%20Extractor) |
| **YT & Web Summarizer** | Content Curation & Analysis | Universal content summarization tool that generates concise summaries from YouTube videos (via transcripts) and web articles. Configurable summary length with consistent formatting. | LangChain, Groq (Llama-3.3-70b), YouTube Transcript API, Streamlit | [`Langchain - YT & Web Summarizer/`](./Langchain%20-%20YT%20%26%20Web%20Summarizer) |
| **LangGraph Chatbot** | Conversational AI & Customer Support | Stateful chatbot with persistent conversation memory, multi-thread management, and SQLite-based checkpointing. Supports conversation history, thread switching, and streaming responses. | LangGraph, Groq (Llama-3.3-70b), SQLite, Streamlit | [`Langgraph- Chatbot/`](./Langgraph-%20Chatbot) |

---

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git

### Required API Keys
You'll need to obtain API keys for the following services:

1. **Google AI Studio** (for Gemini)
   - Visit: https://makersuite.google.com/app/apikey
   - Create API key and save as `GOOGLE_API_KEY`

2. **Groq** (for Llama models)
   - Visit: https://console.groq.com/
   - Create API key and save as `GROQ_API_KEY`

3. **SERPER** (for web search - News Agent only)
   - Visit: https://serper.dev/
   - Create API key and save as `SERPER_API_KEY`

---

## Installation

### Clone the Repository
```bash
git clone https://github.com/MasirJafri1/AI-Chatbots-and-Agents.git
cd AI-Chatbots-and-Agents
```

### Install Dependencies for a Specific Agent

Each agent/chatbot has its own `requirements.txt` file. Navigate to the desired folder and install dependencies:

```bash
# Example: Installing dependencies for MultiPDF Chat Bot
cd "Chat with MultiPDF document"
pip install -r requirements.txt
```

### System Dependencies

For **Resume ATS Analyzer** (pdf2image), install Poppler:

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**macOS:**
```bash
brew install poppler
```

**Windows:**
Download and install from: https://github.com/oschwartz10612/poppler-windows/releases/tag/v25.11.0-0

---

## Configuration

### Environment Variables Setup

Create a `.env` file in each project folder with the required API keys:

```bash
# Example .env file
GOOGLE_API_KEY=your_google_api_key_here
GROQ_API_KEY=your_groq_api_key_here
SERPER_API_KEY=your_serper_api_key_here  # Only for News Reporter Agent
```

⚠️ **Security Note:** Never commit your `.env` file to version control. Each project includes a `.gitignore` file that excludes `.env` files.

---

## 🎯 Usage Examples

Each agent can be run independently. Here are examples:

#### 1. Data Analysis Agent
```bash
cd "Data Analysis Agent"
chainlit run app.py
```

#### 2. MultiPDF Chat Bot
```bash
cd "Chat with MultiPDF document"
streamlit run app.py
```

#### 3. Resume ATS Analyzer
```bash
cd "Resume ATS and Score Analyzer"
streamlit run app.py
```

#### 4. Text to SQL App
```bash
cd "Text to SQL LLM App"
streamlit run app.py
```

#### 5. News Reporter Agent (CrewAI)
```bash
cd "News Reporter AI Agent"
python crew.py  # Modify the topic in crew.py before running
```

#### 6. LangGraph Chatbot
```bash
cd "Langgraph- Chatbot"
streamlit run streamlit_frontend.py
```

#### 7. YT & Web Summarizer
```bash
cd "Langchain - YT & Web Summarizer"
streamlit run app.py
```

#### 8. Invoice Extractor
```bash
cd "Multilanguage Invoice Extractor"
streamlit run app.py
```

---

## 🎨 Project Structure

```
AI-Chatbots-and-Agents/
├── Data Analysis Agent/
│   ├── app.py
│   ├── requirements.txt
│   └── .gitignore
├── Chat with MultiPDF document/
│   ├── app.py
│   ├── requirements.txt
│   └── .gitignore
├── Langchain - YT & Web Summarizer/
│   ├── app.py
│   ├── requirements.txt
│   └── .gitignore
├── Langgraph- Chatbot/
│   ├── streamlit_frontend.py
│   ├── langgraph_backend/
│   │   ├── __init__.py
│   │   └── chatbot.py
│   ├── requirements.txt
│   └── .gitignore
├── Multilanguage Invoice Extractor/
│   ├── app.py
│   ├── requirements.txt
│   └── .gitignore
├── News Reporter AI Agent/
│   ├── agents.py
│   ├── tasks.py
│   ├── tools.py
│   ├── crew.py
│   ├── requirements.txt
│   └── .gitignore
├── Resume ATS and Score Analyzer/
│   ├── app.py
│   ├── requirements.txt
│   └── .gitignore
├── Text to SQL LLM App/
│   ├── app.py
│   ├── sql.py
│   ├── student.db
│   ├── requirements.txt
│   └── .gitignore
└── README.md
```

---

## Contributing

Contributions are welcome! Here's how you can contribute:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/AmazingAgent
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add some AmazingAgent'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/AmazingAgent
   ```
5. **Open a Pull Request**

### Adding a New Agent

When adding a new agent to this repository:

1. Create a new folder with a descriptive name
2. Include a `requirements.txt` with all dependencies
3. Add a `.gitignore` file (copy from existing projects)
4. Update the [Agents & Chatbots Directory](#agents--chatbots-directory) table in this README
5. Ensure your code follows the existing structure:
   - Use environment variables for API keys
   - Include error handling
   - Add comments for complex logic
   - Use Streamlit for UI consistency
     
---

## Author

**Masir Jafri**
- GitHub: [@MasirJafri1](https://github.com/MasirJafri1)
- Email: masirjafri1@gmail.com
- LinkedIn: [@MasirAbbas Jafri](https://www.linkedin.com/in/masirjafri)
- Hashnode: [@MasirJafri](https://masirjafri.hashnode.dev)

---

## 🙏 Acknowledgments

- Google AI for Gemini API
- Groq for fast LLM inference
- LangChain community for excellent documentation
- CrewAI for multi-agent framework
- Streamlit for amazing UI framework
- Open source community for various libraries and tools

---

## 📊 Repository Stats

- **Total Projects**: 8
- **Created**: October 2025
- **Last Updated**: November 2025

---

## 🔗 Quick Links

- [Report Bug](https://github.com/MasirJafri1/AI-Chatbots-and-Agents/issues)
- [Request Feature](https://github.com/MasirJafri1/AI-Chatbots-and-Agents/issues)
- [GitHub Profile](https://github.com/MasirJafri1)

---

## ⭐ Star History

If you find this repository helpful, please consider giving it a star! ⭐

---

**Made By MasirJafri**