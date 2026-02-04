# Quick Start Guide - Construction Legal Assistant

## ✅ Setup Complete!

Your Construction Legal Assistant is now **running** and ready to test!

## 🌐 Access the Application

**Open your web browser and go to:**
```
http://localhost:5000
```

## 📝 Testing Workflow

### Step 1: Register a User
1. Open http://localhost:5000
2. Click "Register here"
3. Create an account:
   - Username: `test`
   - Email: `test@example.com`
   - Password: `test123`
4. Click "Register"

### Step 2: Login
1. After registration, you'll be redirected to login
2. Login with your credentials
3. You'll be redirected to the Dashboard

### Step 3: Create a Project
1. Click "+ Create New Project"
2. Fill in:
   - Project Name: `Test Construction Project`
   - Description: `Testing the AI assistant`
3. Click "Create Project"

### Step 4: Upload a Contract (PDF)
1. Click "View Details" on your project
2. Click "Upload Contract"
3. Drag & drop a PDF or click to browse
   - **Note**: For now, only digital PDFs work (OCR is disabled)
4. Wait for processing (may take 5-15 minutes)

### Step 5: Upload Laws (PDF)
1. Click "Upload Law"
2. Optionally fill in metadata:
   - Law Number: `32/5`
   - Law Title: `Albanian Construction Safety Law`
   - Year: `2025`
3. Upload PDF
4. Wait for processing

### Step 6: Ask Questions
1. Once documents are processed, click "Ask Questions"
2. Type a question:
   ```
   Who is responsible for concrete delivery delays?
   ```
   Or in Albanian:
   ```
   Kush është përgjegjës për vonesën e dorëzimit të betonit?
   ```
3. Click "Ask Question"
4. View the AI-generated answer with citations!

## 🔑 Your OpenAI API Key

Set your key in the `.env` file:
```
OPENAI_API_KEY=sk-proj-...
```

## 🎯 What Works

✅ User authentication (register/login/logout)
✅ Project creation and management
✅ Digital PDF upload (contracts & laws)
✅ Text extraction from PDFs
✅ Embeddings generation (OpenAI)
✅ Vector search (NumPy-based)
✅ RAG question answering (GPT-4)
✅ Albanian + English support
✅ Citation tracking
✅ Mobile-responsive UI
✅ Query history

## ⚠️ Current Limitations

❌ **OCR Not Available** - Scanned PDFs won't work (only digital PDFs)
  - To enable: Install Tesseract OCR
  - macOS: `brew install tesseract`
  - Then: `pip install pytesseract pdf2image`

❌ **FAISS Not Available** - Using NumPy for vector search (slower but functional)
  - For production: Install FAISS
  - `pip install faiss-cpu` (requires proper build tools)

## 🛑 Stopping the Server

Press `Ctrl+C` in the terminal where the app is running

## 🚀 Restarting the Server

If you stopped the server, restart with:
```bash
cd /Users/lastl/ai_construction_assistant
./run.sh
```

Or manually:
```bash
source venv/bin/activate
PYTHONPATH=$(pwd) python backend/app.py
```

## 📖 Sample Test Documents

You can test with ANY PDF files you have. For construction contracts:
- Construction agreements
- Delivery contracts
- Subcontractor agreements

For laws:
- Albanian construction law PDFs
- Building codes
- Safety regulations

## 🐛 Troubleshooting

**Q: "Upload fails"**
- A: Make sure the PDF is digital (not scanned)
- Check file size < 50MB

**Q: "Processing takes forever"**
- A: First upload takes 5-15 min (creating embeddings)
- Check backend logs for progress

**Q: "No answer to my question"**
- A: Make sure documents finished processing (status: completed)
- Try rephrasing the question

**Q: "OpenAI API errors"**
- A: Check your API key has credits
- Visit: https://platform.openai.com

## 📁 Project Location

```
/Users/lastl/ai_construction_assistant
```

## 📚 Full Documentation

See `README.md` for complete documentation, deployment guides, and API reference.

---

**Happy Testing! 🏗️**

For issues: Check the terminal logs where Flask is running
