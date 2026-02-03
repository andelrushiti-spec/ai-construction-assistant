import pdfplumber
import logging
from pathlib import Path
from typing import List, Dict, Tuple
import re

# Optional OCR support
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.warning("OCR libraries not available. Only digital PDFs will be supported.")

logger = logging.getLogger(__name__)

class PDFExtractor:
    """Extract text from PDFs using pdfplumber and Tesseract OCR"""

    def __init__(self, tesseract_cmd: str = None):
        """
        Initialize PDF extractor

        Args:
            tesseract_cmd: Path to tesseract executable
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text(self, pdf_path: str, use_ocr: bool = False) -> List[Dict[str, any]]:
        """
        Extract text from PDF, page by page

        Args:
            pdf_path: Path to PDF file
            use_ocr: Force OCR even if text is extractable

        Returns:
            List of dicts with page number and text: [{'page': 1, 'text': '...'}, ...]
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        pages = []

        try:
            # First try pdfplumber for digital PDFs
            if not use_ocr:
                pages = self._extract_with_pdfplumber(pdf_path)

                # Check if extraction was successful (not empty or mostly empty)
                if self._is_extraction_successful(pages):
                    logger.info(f"Successfully extracted text from {pdf_path.name} using pdfplumber")
                    return pages
                else:
                    logger.warning(f"pdfplumber extraction poor quality, falling back to OCR for {pdf_path.name}")

            # Fallback to OCR for scanned PDFs
            pages = self._extract_with_ocr(pdf_path)
            logger.info(f"Successfully extracted text from {pdf_path.name} using OCR")

        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path.name}: {str(e)}")
            raise

        return pages

    def _extract_with_pdfplumber(self, pdf_path: Path) -> List[Dict[str, any]]:
        """Extract text using pdfplumber (for digital PDFs)"""
        pages = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                pages.append({
                    'page': page_num,
                    'text': text.strip(),
                    'method': 'pdfplumber'
                })

        return pages

    def _extract_with_ocr(self, pdf_path: Path) -> List[Dict[str, any]]:
        """Extract text using Tesseract OCR (for scanned PDFs)"""
        if not OCR_AVAILABLE:
            logger.error("OCR not available. Please install tesseract-ocr and pytesseract.")
            raise RuntimeError("OCR libraries not installed. Please install tesseract-ocr, pytesseract, and pdf2image.")

        pages = []

        # Convert PDF to images
        images = convert_from_path(str(pdf_path), dpi=300)

        for page_num, image in enumerate(images, start=1):
            # Perform OCR on each page
            text = pytesseract.image_to_string(image, lang='eng+sqi')  # English + Albanian
            pages.append({
                'page': page_num,
                'text': text.strip(),
                'method': 'ocr'
            })

        return pages

    def _is_extraction_successful(self, pages: List[Dict[str, any]], min_chars_per_page: int = 50) -> bool:
        """
        Check if text extraction was successful

        Args:
            pages: List of page dicts
            min_chars_per_page: Minimum average characters per page

        Returns:
            True if extraction seems successful
        """
        if not pages:
            return False

        total_chars = sum(len(page['text']) for page in pages)
        avg_chars = total_chars / len(pages)

        return avg_chars >= min_chars_per_page

    def get_pdf_metadata(self, pdf_path: str) -> Dict[str, any]:
        """
        Get PDF metadata (page count, file size, etc.)

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dict with metadata
        """
        pdf_path = Path(pdf_path)

        metadata = {
            'filename': pdf_path.name,
            'file_size': pdf_path.stat().st_size,
            'pages': 0
        }

        try:
            with pdfplumber.open(pdf_path) as pdf:
                metadata['pages'] = len(pdf.pages)

                # Try to get PDF metadata
                if pdf.metadata:
                    metadata['title'] = pdf.metadata.get('Title', '')
                    metadata['author'] = pdf.metadata.get('Author', '')
                    metadata['subject'] = pdf.metadata.get('Subject', '')
                    metadata['creator'] = pdf.metadata.get('Creator', '')
        except Exception as e:
            logger.error(f"Error reading PDF metadata: {str(e)}")

        return metadata

    def extract_contract_metadata(self, pages: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Extract contract-specific metadata from text

        Args:
            pages: List of page dicts with text

        Returns:
            Dict with contract metadata (parties, dates, etc.)
        """
        # Combine first few pages for metadata extraction
        combined_text = " ".join([p['text'] for p in pages[:3]])

        metadata = {
            'parties': [],
            'dates': [],
            'contract_number': None,
            'contract_type': None
        }

        # Extract contract number patterns
        contract_num_patterns = [
            r'Contract\s+(?:No\.?|Number)\s*[:.]?\s*([A-Z0-9/-]+)',
            r'Kontratë\s+(?:Nr\.?|Numër)\s*[:.]?\s*([A-Z0-9/-]+)',
        ]

        for pattern in contract_num_patterns:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                metadata['contract_number'] = match.group(1)
                break

        # Extract date patterns (various formats)
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
            r'\d{1,2}\s+(?:Janar|Shkurt|Mars|Prill|Maj|Qershor|Korrik|Gusht|Shtator|Tetor|Nëntor|Dhjetor)\s+\d{4}',
        ]

        for pattern in date_patterns:
            dates = re.findall(pattern, combined_text, re.IGNORECASE)
            metadata['dates'].extend(dates)

        # Remove duplicates
        metadata['dates'] = list(set(metadata['dates']))[:5]  # Keep max 5 dates

        return metadata

    def extract_law_metadata(self, pages: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Extract law-specific metadata from text

        Args:
            pages: List of page dicts with text

        Returns:
            Dict with law metadata (law number, title, articles, etc.)
        """
        # Combine first page for law metadata
        first_page_text = pages[0]['text'] if pages else ""

        metadata = {
            'law_number': None,
            'law_title': None,
            'year': None,
            'articles_count': 0
        }

        # Extract law number patterns
        law_num_patterns = [
            r'Law\s+(?:No\.?|Number)\s*[:.]?\s*([0-9/]+)',
            r'Ligj\s+(?:Nr\.?|Numër)\s*[:.]?\s*([0-9/]+)',
            r'VKM\s+(?:Nr\.?)\s*[:.]?\s*([0-9/]+)',  # Albanian government decisions
        ]

        for pattern in law_num_patterns:
            match = re.search(pattern, first_page_text, re.IGNORECASE)
            if match:
                metadata['law_number'] = match.group(1)
                break

        # Extract year
        year_match = re.search(r'\b(19|20)\d{2}\b', first_page_text)
        if year_match:
            metadata['year'] = int(year_match.group(0))

        # Count articles
        all_text = " ".join([p['text'] for p in pages])
        article_patterns = [
            r'Article\s+\d+',
            r'Neni\s+\d+',
        ]

        for pattern in article_patterns:
            articles = re.findall(pattern, all_text, re.IGNORECASE)
            metadata['articles_count'] = max(metadata['articles_count'], len(articles))

        return metadata
