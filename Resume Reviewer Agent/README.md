# 📄 Resume Reviewer Agent

A production-grade, AI-powered resume review API that provides professional, actionable feedback on resumes. Built with FastAPI, uses Gemini 2.5 Flash for vision-based analysis, and features asynchronous job processing for scalability.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Latest-green.svg)](https://www.mongodb.com/)

---

## 🎯 Overview

The Resume Reviewer Agent is a scalable microservice that analyzes PDF resumes and provides structured, professional feedback. It uses vision-based AI (Gemini 2.5 Flash via OpenRouter) to understand resume layouts, content, and design, delivering comprehensive reviews in three focused paragraphs.

### ✨ Key Features

- 🚀 **Async Job Processing** - Redis Queue (RQ) for handling multiple resume reviews simultaneously
- 📊 **Vision-Based Analysis** - Converts PDFs to images for comprehensive visual analysis
- 🔒 **Prompt Injection Protection** - System prompts designed to ignore malicious content in resumes
- 💾 **Persistent Storage** - MongoDB for job state and results persistence
- 🐳 **Docker Ready** - Complete Docker Compose setup for easy deployment
- 📈 **Status Tracking** - Real-time job status updates throughout the review process
- 🎨 **Structured Output** - Consistent three-paragraph review format

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Resume Reviewer Agent                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────┐    ┌──────────────┐    ┌─────────────┐                │
│  │  Client  │───▶│   FastAPI    │───▶│   MongoDB   │                │
│  │          │    │   Server     │    │  (Storage)  │                │
│  └──────────┘    └──────┬───────┘    └─────────────┘                │
│                         │                                            │
│                         ▼                                            │
│                  ┌──────────────┐                                    │
│                  │    Redis     │                                    │
│                  │   (Valkey)   │                                    │
│                  └──────┬───────┘                                    │
│                         │                                            │
│                         ▼                                            │
│                  ┌──────────────┐    ┌─────────────┐                │
│                  │  RQ Worker   │───▶│  OpenRouter │                │
│                  │              │    │ (Gemini AI) │                │
│                  └──────────────┘    └─────────────┘                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Processing Flow

1. **Upload** → Client uploads PDF resume via `/upload` endpoint
2. **Save** → File saved to disk, job record created in MongoDB with status `saving`
3. **Queue** → Job enqueued to Redis Queue, status updated to `queued`
4. **Process** → Worker picks up job, status updated to `processing`
5. **Convert** → PDF converted to images, status updated to `converting to images`
6. **Analyze** → Gemini 2.5 Flash analyzes the resume image
7. **Complete** → Result saved to MongoDB, status updated to `processed`

---

## 📁 Project Structure

```
Resume Reviewer Agent/
├── 📂 app/
│   ├── 📂 db/
│   │   ├── 📂 collections/
│   │   │   ├── __init__.py
│   │   │   └── files.py          # File schema & collection
│   │   ├── __init__.py
│   │   ├── client.py             # MongoDB client connection
│   │   └── db.py                 # Database instance
│   ├── 📂 queue/
│   │   ├── __init__.py
│   │   ├── q.py                  # Redis Queue setup
│   │   └── workers.py            # AI processing worker
│   ├── 📂 utils/
│   │   ├── __init__.py
│   │   └── file.py               # File handling utilities
│   ├── main.py                   # Application entry point
│   └── server.py                 # FastAPI routes & endpoints
├── 📂 .devcontainer/             # VS Code dev container config
├── .dockerignore
├── .env                          # Environment variables (not committed)
├── .env.example                  # Example environment file
├── .gitignore
├── docker-compose.prod.yaml      # Production Docker Compose
├── Dockerfile                    # Application container
├── freeze.sh                     # Dependency freeze script
├── requirements.txt              # Python dependencies
├── run.sh                        # Server run script
├── worker.sh                     # Worker run script
└── README.md                     # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- OpenRouter API Key (get one at [openrouter.ai](https://openrouter.ai))

### Environment Setup

1. **Clone the repository**
   ```bash
   cd "Resume Reviewer Agent"
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Add your OpenRouter API key**
   ```env
   OPENROUTER_API_KEY="your_openrouter_api_key_here"
   ```

### Running with Docker Compose

```bash
# Start all services (MongoDB, Redis/Valkey, App, Worker)
docker-compose -f docker-compose.prod.yaml up --build

# Run in detached mode
docker-compose -f docker-compose.prod.yaml up -d --build
```

The API will be available at `http://localhost:8000`

---

## 📡 API Endpoints

### Health Check

```http
GET /
```

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Upload Resume

```http
POST /upload
Content-Type: multipart/form-data
```

**Request:**
- `file` (required): PDF file of the resume

**Response:**
```json
{
  "file_id": "507f1f77bcf86cd799439011"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.pdf"
```

---

### Get Review Result

```http
GET /{id}
```

**Parameters:**
- `id` (path): The file ID returned from the upload endpoint

**Response:**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "name": "resume.pdf",
  "status": "processed",
  "result": "Your resume presents a strong foundation with clear organization and relevant experience in software development. The layout is clean and professional, making it easy for recruiters to quickly scan your qualifications...\n\nHowever, there are several areas that could benefit from improvement. The bullet points under your work experience could be more impactful by quantifying achievements...\n\nTo enhance your resume's effectiveness, consider adding specific metrics and numbers to demonstrate impact. Incorporate relevant keywords from job descriptions to improve ATS compatibility..."
}
```

**Status Values:**
| Status | Description |
|--------|-------------|
| `saving` | File is being saved to disk |
| `queued` | Job is queued for processing |
| `processing` | Worker has picked up the job |
| `converting to images` | PDF is being converted to images |
| `converting to images success` | Conversion completed |
| `processed` | Review complete, result available |

---

## 🤖 AI Review Structure

The AI provides feedback in exactly **three structured paragraphs**:

| Paragraph | Focus |
|-----------|-------|
| **1. Strengths** | Overall impression, clarity, structure, and suitability for roles |
| **2. Weaknesses** | Areas for improvement, formatting issues, content clarity, missing information |
| **3. Recommendations** | Actionable steps to improve the resume, ATS optimization tips |

### Security Features

The system prompt includes protection against prompt injection:
- Treats resume content as untrusted user input
- Ignores any instructions found inside the resume
- Maintains professional, consistent output format

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI | High-performance async API framework |
| **AI Model** | Gemini 2.5 Flash (via OpenRouter) | Vision-based resume analysis |
| **Database** | MongoDB | Document storage for jobs and results |
| **Queue** | Redis (Valkey) | Task queue for async processing |
| **Worker** | RQ (Redis Queue) | Background job processing |
| **PDF Processing** | pdf2image + Poppler | PDF to image conversion |
| **Containerization** | Docker & Docker Compose | Easy deployment and scaling |

---

## 🔧 Local Development

### Without Docker

1. **Install system dependencies**
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update && sudo apt-get install -y poppler-utils
   ```
   
   **macOS:**
   ```bash
   brew install poppler
   ```
   
   **Windows:**
   Download from [poppler-windows releases](https://github.com/oschwartz10612/poppler-windows/releases)

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start MongoDB and Redis** (required)
   
4. **Run the server**
   ```bash
   python -m app.main
   ```

5. **Run the worker** (in a separate terminal)
   ```bash
   rq worker --with-scheduler --url redis://localhost:6379
   ```

---

## 📊 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| `app` | 8000 | FastAPI application server |
| `worker` | - | RQ background worker |
| `mongo` | 27017 | MongoDB database |
| `valkey` | 6379 | Redis-compatible queue (Valkey) |

### Persistent Volumes

- `mongodb_data` - MongoDB data persistence
- `valkey_data` - Redis/Valkey data persistence

---

## 🔐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | ✅ Yes | Your OpenRouter API key for Gemini access |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 👤 Author

**Masir Jafri**
- GitHub: [@MasirJafri1](https://github.com/MasirJafri1)
- LinkedIn: [@MasirAbbas Jafri](https://www.linkedin.com/in/masirjafri)
- Email: masirjafri1@gmail.com

---

## 🔗 Related Projects

Check out other AI agents and chatbots in the [main repository](../).

---

**Made By MasirJafri** ⚡
