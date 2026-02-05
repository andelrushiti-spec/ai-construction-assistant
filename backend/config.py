"""
Construction Legal Assistant
Configuration Settings

Developer: Andel Albdesk
Copyright (c) 2026 Andel Albdesk. All rights reserved.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent

# Persistent storage root.  On Render this points to the mounted disk
# (/mnt/data).  Locally it falls back to the project root so nothing changes
# for development.
PERSISTENT_ROOT = Path(os.getenv("PERSISTENT_VOLUME_PATH", str(BASE_DIR)))

UPLOADS_DIR = PERSISTENT_ROOT / "uploads"
LOGS_DIR = PERSISTENT_ROOT / "logs"
VECTOR_DB_DIR = PERSISTENT_ROOT / "vector_db_storage"

# Create directories if they don't exist (parents=True handles the case where
# the persistent volume root itself hasn't been created yet, e.g. local dev
# with a custom PERSISTENT_VOLUME_PATH).
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

# Flask Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "construction-legal-assistant-secret-key-change-in-production")
DEBUG = os.getenv("DEBUG", "False") == "True"

# Database Configuration — lives on the persistent volume
SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{PERSISTENT_ROOT / 'construction_legal_assistant.db'}"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Embedding Model
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIMENSIONS = 3072

# LLM Model
LLM_MODEL = "gpt-4-turbo-preview"  # or "gpt-4-1106-preview"

# Document Processing
MAX_FILE_SIZE_MB = 50
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'pages'}  # PDF, Word, and Apple Pages
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "/usr/local/bin/tesseract")  # Update path as needed

# Chunking Configuration
CHUNK_SIZE = 800  # words per chunk
CHUNK_OVERLAP = 100  # word overlap between chunks

# RAG Configuration
TOP_K_RESULTS = 5  # Number of relevant chunks to retrieve

# Encryption
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")  # For AES encryption of embeddings

# Session Configuration
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour in seconds

# Auto-delete uploads after processing
AUTO_DELETE_UPLOADS = True

# Supported Languages
SUPPORTED_LANGUAGES = ['sq', 'en']  # Albanian and English

# System Prompt for RAG
RAG_SYSTEM_PROMPT = """You are an expert construction contract and Albanian construction law assistant. You help construction companies understand their contracts, Albanian construction laws, and general construction practices.

Instructions:
1. PRIORITIZE information from the provided contract and law documents when available
2. When answering from documents, ALWAYS cite sources: [Contract Name, Page X] or [Law Number, Article Y]
3. For general construction questions NOT in the documents:
   - Provide helpful answers based on common construction practices
   - Clearly state: "Based on general construction practices (not from your documents):"
   - Be accurate and practical
4. Answer in the SAME language as the question (Albanian or English)
5. Use clear, practical construction terminology
6. Be concise and actionable

Example responses:
- Document-based: "According to your contract [ContractName.pdf, Page 5], payment is due within 30 days..."
- General knowledge: "Based on general construction practices (not from your documents): Concrete typically cures in 28 days..."
- Mixed: "Your contract [Name, Page 3] specifies X. Generally in construction, this means Y..."
"""

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
