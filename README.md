# Construction Legal Assistant

A privacy-first AI assistant designed for Albanian construction companies to manage contracts and construction laws with intelligent question-answering capabilities.

## Features

- **Contract & Law Management**: Upload construction contracts and Albanian construction laws (PDFs)
- **Dual Language Support**: Ask questions in Albanian or English
- **RAG-Powered Answers**: Get precise, citation-backed answers using GPT-4 and vector search
- **Privacy-First**: PDFs are automatically deleted after processing; only encrypted embeddings are stored
- **Mobile-Friendly**: Responsive design optimized for on-site mobile queries
- **Desktop-First Uploads**: Optimized upload experience for large construction PDFs
- **Citation Tracking**: Every answer includes contract page/clause and law article references

## Tech Stack

### Backend
- **Python 3.9+** with Flask
- **OpenAI GPT-4** for question answering
- **FAISS** for vector similarity search
- **pdfplumber** for PDF text extraction
- **Tesseract OCR** for scanned documents
- **SQLite/PostgreSQL** for data storage
- **Flask-Login** for authentication

### Frontend
- **HTML5/CSS3/JavaScript** (vanilla)
- **Responsive design** with mobile-first approach
- **Drag & drop** file uploads

## Installation

### Prerequisites

1. **Python 3.9+**
   ```bash
   python --version
   ```

2. **Tesseract OCR** (for scanned PDFs)

   **macOS (Homebrew):**
   ```bash
   brew install tesseract
   brew install tesseract-lang  # For Albanian language support
   ```

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install tesseract-ocr tesseract-ocr-sqi
   ```

   **Windows:**
   Download from: https://github.com/UB-Mannheim/tesseract/wiki

3. **OpenAI API Key**
   Get your API key from: https://platform.openai.com/api-keys

### Setup Instructions

1. **Clone or Download the Project**
   ```bash
   cd ai_construction_assistant
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv

   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate

   # On Windows:
   venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your configuration:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=your-secret-key-change-in-production
   TESSERACT_CMD=/usr/local/bin/tesseract  # Update path for your OS
   DEBUG=True
   ```

5. **Initialize Database**
   ```bash
   cd backend
   python app.py
   ```

   The database will be automatically created on first run.

6. **Access the Application**
   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### 1. Register & Login
- Create an account at the homepage
- Login with your credentials

### 2. Create a Project
- Click "Create New Project" on the dashboard
- Give it a descriptive name (e.g., "Tirana Construction Project")

### 3. Upload Documents

**Upload Contracts:**
- Navigate to your project
- Click "Upload Contract"
- Drag & drop or select a PDF file
- Wait for processing (5-15 minutes depending on size)

**Upload Laws:**
- Click "Upload Law"
- Optionally add metadata (law number, title, year)
- Upload the PDF
- Wait for processing

### 4. Ask Questions
- Click "Ask Questions" on your project
- Type your question in Albanian or English
- Examples:
  - "Who is responsible for concrete delivery delays?"
  - "Kush është përgjegjës për vonesën e dorëzimit të betonit?"
  - "What penalties apply for late completion according to Law 32/5?"

### 5. View Answers
- Get precise answers with citations
- See contract references (page + clause)
- See law references (article + page)
- Review query history

## Project Structure

```
ai_construction_assistant/
├── backend/
│   ├── app.py                  # Main Flask application
│   ├── config.py               # Configuration settings
│   ├── routes/                 # API endpoints
│   │   ├── auth.py
│   │   ├── projects.py
│   │   ├── upload_contract.py
│   │   ├── upload_law.py
│   │   └── query.py
│   ├── processing/             # PDF & text processing
│   │   ├── pdf_extractor.py
│   │   ├── chunker.py
│   │   └── embeddings.py
│   ├── db/                     # Database models
│   │   └── database.py
│   └── vector_db/              # FAISS vector database
│       └── faiss_handler.py
├── frontend/
│   ├── index.html              # Login/Register
│   ├── dashboard.html          # Projects dashboard
│   ├── upload_contract.html    # Contract upload
│   ├── upload_law.html         # Law upload
│   ├── query.html              # Ask questions
│   └── static/
│       ├── css/styles.css
│       └── js/scripts.js
├── logs/                       # Application logs
├── uploads/                    # Temporary PDF storage
├── requirements.txt
├── .env.example
└── README.md
```

## Common Albanian Construction Laws

Here are some Albanian construction laws you might want to upload:

1. **Law No. 107/2014** - On Planning and Development of Territory
2. **Law No. 10433/2011** - On Construction Inspection
3. **Law No. 9780/2007** - On Construction Inspections
4. **Law No. 10131/2009** - On Fire Protection Service
5. **VKM No. 433/2015** - Construction Technical Standards
6. **Labor Code** - Construction Worker Safety Regulations

## Deployment (Production)

### Option 1: Linux VPS (DigitalOcean, Hetzner, OVH)

1. **Install Dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip python3-venv tesseract-ocr tesseract-ocr-sqi nginx
   ```

2. **Clone Project & Setup**
   ```bash
   git clone <your-repo>
   cd ai_construction_assistant
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
   ```

4. **Setup Nginx as Reverse Proxy**
   Create `/etc/nginx/sites-available/construction-legal-assistant`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Setup SSL with Let's Encrypt**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

### Option 2: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-sqi

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:app"]
```

Build and run:
```bash
docker build -t construction-legal-assistant .
docker run -p 5000:5000 -e OPENAI_API_KEY=your_key construction-legal-assistant
```

## Security Considerations

1. **Change SECRET_KEY** in production
2. **Use PostgreSQL** instead of SQLite for production
3. **Enable HTTPS/TLS** (required for production)
4. **Set DEBUG=False** in production
5. **Use strong passwords** for user accounts
6. **Regular backups** of database and vector indexes
7. **Rate limiting** for API endpoints (consider using Flask-Limiter)

## Troubleshooting

### Issue: Tesseract not found
**Solution:** Update `TESSERACT_CMD` in `.env` with correct path
```bash
# Find tesseract path
which tesseract  # macOS/Linux
where tesseract  # Windows
```

### Issue: OpenAI API errors
**Solution:** Check your API key and billing status at https://platform.openai.com

### Issue: Upload fails with large PDFs
**Solution:** Increase `MAX_FILE_SIZE_MB` in `config.py`

### Issue: Processing takes too long
**Solution:**
- Check if OCR is being used (slower for scanned PDFs)
- Consider using digital PDFs when possible
- Increase server resources for production

### Issue: Database locked errors
**Solution:** Switch to PostgreSQL for production use

## Performance Tips

1. **Use digital PDFs** when possible (faster than OCR)
2. **Batch upload** laws at project creation
3. **PostgreSQL** for better concurrent access
4. **Redis** for caching query results (advanced)
5. **GPU** for faster OCR processing (optional)

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/check` - Check authentication status

### Projects
- `GET /api/projects/` - List projects
- `POST /api/projects/` - Create project
- `GET /api/projects/<id>` - Get project details
- `DELETE /api/projects/<id>` - Delete project

### Uploads
- `POST /api/upload/contract/<project_id>` - Upload contract
- `GET /api/upload/contract/<contract_id>/status` - Check processing status
- `POST /api/upload/law/<project_id>` - Upload law
- `GET /api/upload/law/<law_id>/status` - Check processing status

### Queries
- `POST /api/query/<project_id>` - Ask question
- `GET /api/query/history/<project_id>` - Get query history

## Contributing

This is an MVP built for Albanian construction companies. Contributions welcome:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - See LICENSE file for details

## Disclaimer

This tool interprets text from uploaded documents only. It is **not a substitute for professional legal advice**. Always consult with a qualified construction lawyer for critical decisions.

## Support

For issues or questions:
- Create an issue on GitHub
- Email: support@yourcompany.com

## Roadmap (Future Features)

- [ ] Multi-contract comparison
- [ ] Automated law library updates
- [ ] Export reports to PDF
- [ ] Mobile app (iOS/Android)
- [ ] Multi-language support (Greek, Italian)
- [ ] Integration with construction management tools
- [ ] Advanced analytics dashboard

---

Built with ❤️ for Albanian Construction Industry
