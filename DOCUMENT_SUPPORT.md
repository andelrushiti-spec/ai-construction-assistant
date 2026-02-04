# 📄 Document Format Support

## Supported Formats

The Construction Legal Assistant now supports multiple document formats for contracts and laws:

### ✅ **PDF Documents** (.pdf)
- **Digital PDFs**: Best performance, instant text extraction
- **Scanned PDFs**: Requires Tesseract OCR installation
- **Features**: Full metadata extraction, page-by-page processing

### ✅ **Microsoft Word** (.docx, .doc)
- **DOCX**: Modern Word format (2007+)
- **DOC**: Legacy Word format (limited support)
- **Features**: Extracts text from paragraphs and tables
- **Auto-pagination**: Documents are split into ~500-word "pages" for consistency

### ✅ **Apple Pages** (.pages)
- **Pages Documents**: macOS native format
- **How it works**: Extracts embedded PDF preview
- **Fallback**: XML extraction if no PDF preview available
- **Compatibility**: Works on all platforms (macOS, Linux, Windows)

## Format Comparison

| Format | Speed | Quality | Best For |
|--------|-------|---------|----------|
| **PDF (Digital)** | ⚡ Fast | ⭐⭐⭐⭐⭐ | Official documents, contracts |
| **PDF (Scanned)** | 🐢 Slow | ⭐⭐⭐ | Old paper documents (requires OCR) |
| **Word (.docx)** | ⚡ Fast | ⭐⭐⭐⭐ | Editable contracts, drafts |
| **Word (.doc)** | ⚡ Fast | ⭐⭐⭐ | Legacy documents |
| **Pages (.pages)** | ⚡ Fast | ⭐⭐⭐⭐ | macOS users, modern documents |

## Processing Details

### PDF Processing
1. **Primary Method**: pdfplumber (digital PDFs)
2. **Fallback**: Tesseract OCR (scanned/image PDFs)
3. **Languages Supported**: English + Albanian (sqi)
4. **Metadata Extracted**: Title, author, page count

### Word Document Processing
1. **Library**: python-docx
2. **Extraction**: Paragraphs + tables
3. **Pagination**: Auto-split into ~500-word chunks
4. **Metadata**: Title, author, estimated pages

### Pages Document Processing
1. **Method**: Extract embedded PDF from .pages archive
2. **Fallback**: Parse index.xml for text content
3. **Compatibility**: Cross-platform (Pages files are ZIP archives)
4. **Limitation**: Complex formatting may be lost

## File Size Limits

- **Maximum**: 50 MB per file
- **Recommended**: Under 10 MB for faster processing
- **Large files**: May take 5-15 minutes to process

## Recommendations

### For Contracts
✅ **Best**: PDF (digital) - Official, signed documents
✅ **Good**: Word (.docx) - Drafts, editable contracts
⚠️ **OK**: Pages - macOS users
❌ **Avoid**: Scanned PDFs without OCR installed

### For Laws
✅ **Best**: PDF (digital) - Official government documents
✅ **Good**: Word (.docx) - Unofficial law summaries
⚠️ **OK**: Pages - macOS legal documents

## Technical Implementation

### Backend
```python
# New document_extractor.py module
- PDF: pdfplumber + pytesseract (OCR)
- Word: python-docx
- Pages: zipfile + XML parsing
```

### Configuration
```python
# config.py
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'pages'}
```

### Frontend
```html
<!-- Updated file input -->
<input accept=".pdf,.docx,.doc,.pages">
```

## Installation Notes

### Required (Already Installed)
- `pdfplumber` - PDF text extraction
- `python-docx` - Word document support
- `lxml` - XML parsing

### Optional (For Scanned PDFs)
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-sqi

# Python packages
pip install pytesseract pdf2image
```

## Usage Examples

### Upload Contract (PDF)
```bash
curl -X POST http://localhost:5000/api/upload/contract/1 \
  -H "Content-Type: multipart/form-data" \
  -F "file=@contract.pdf"
```

### Upload Contract (Word)
```bash
curl -X POST http://localhost:5000/api/upload/contract/1 \
  -F "file=@contract.docx"
```

### Upload Law (Pages)
```bash
curl -X POST http://localhost:5000/api/upload/law/1 \
  -F "file=@law.pages" \
  -F "law_number=32/5" \
  -F "law_title=Construction Safety Law"
```

## Error Handling

### Common Issues

**"Unsupported file format"**
- Solution: Ensure file has correct extension (.pdf, .docx, .doc, .pages)

**"OCR not available"**
- Issue: Trying to process scanned PDF without Tesseract
- Solution: Install Tesseract OCR or use digital PDF

**"Could not find text content in Pages document"**
- Issue: Pages document doesn't have embedded PDF
- Solution: Export to PDF or Word from Pages app

**"File too large"**
- Issue: File exceeds 50MB limit
- Solution: Compress document or split into sections

## Future Enhancements

🔮 **Planned Features**:
- [ ] Google Docs support (.gdoc)
- [ ] OpenDocument Format (.odt)
- [ ] Rich Text Format (.rtf)
- [ ] HTML documents (.html)
- [ ] Markdown documents (.md)

## Performance Tips

1. **Use digital PDFs** when possible (10x faster than OCR)
2. **Compress large documents** before uploading
3. **Word documents** process faster than scanned PDFs
4. **Pages documents** work best when created on newer versions of Pages

## Security Notes

- ✅ All uploaded files are automatically deleted after processing
- ✅ Only text content and embeddings are stored
- ✅ File format validation prevents malicious uploads
- ✅ 50MB size limit prevents DoS attacks

---

**Document support added**: January 2026
**Formats supported**: PDF, Word (.docx, .doc), Apple Pages (.pages)
