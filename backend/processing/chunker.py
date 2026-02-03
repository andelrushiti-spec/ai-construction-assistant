import re
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class TextChunker:
    """Split text into chunks for embeddings"""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        """
        Initialize chunker

        Args:
            chunk_size: Target words per chunk
            chunk_overlap: Word overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_pages(self, pages: List[Dict[str, any]], doc_type: str = 'contract',
                    doc_name: str = '') -> List[Dict[str, any]]:
        """
        Chunk pages into smaller pieces with metadata

        Args:
            pages: List of page dicts from PDF extractor
            doc_type: 'contract' or 'law'
            doc_name: Document filename or name

        Returns:
            List of chunk dicts with text and metadata
        """
        chunks = []

        for page in pages:
            page_num = page['page']
            text = page['text']

            # Split page into chunks
            page_chunks = self._chunk_text(text)

            # Add metadata to each chunk
            for i, chunk_text in enumerate(page_chunks):
                chunk = {
                    'text': chunk_text,
                    'page': page_num,
                    'chunk_index': i,
                    'doc_type': doc_type,
                    'doc_name': doc_name,
                    'extraction_method': page.get('method', 'unknown')
                }

                # Extract clause/article information
                if doc_type == 'contract':
                    chunk['clause'] = self._extract_clause_info(chunk_text)
                elif doc_type == 'law':
                    chunk['article'] = self._extract_article_info(chunk_text)

                chunks.append(chunk)

        logger.info(f"Created {len(chunks)} chunks from {len(pages)} pages")
        return chunks

    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks by word count with overlap

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        # Split into words (preserving whitespace context)
        words = text.split()

        if len(words) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunks.append(' '.join(chunk_words))

            # Move start by (chunk_size - overlap)
            start += (self.chunk_size - self.chunk_overlap)

        return chunks

    def _extract_clause_info(self, text: str) -> str:
        """
        Extract clause/section information from contract text

        Args:
            text: Chunk text

        Returns:
            Clause identifier or empty string
        """
        # Common contract clause patterns
        patterns = [
            r'(?:Clause|Article|Section)\s+(\d+(?:\.\d+)*)',
            r'(?:Klauzola|Neni|Seksioni)\s+(\d+(?:\.\d+)*)',
            r'(\d+(?:\.\d+)*)\.\s*[A-Z]',  # Numbered sections
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return ''

    def _extract_article_info(self, text: str) -> str:
        """
        Extract article information from law text

        Args:
            text: Chunk text

        Returns:
            Article identifier or empty string
        """
        # Law article patterns
        patterns = [
            r'Article\s+(\d+(?:\.\d+)*)',
            r'Neni\s+(\d+(?:\.\d+)*)',
            r'Art\.\s*(\d+(?:\.\d+)*)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return ''

    def chunk_by_paragraphs(self, pages: List[Dict[str, any]], doc_type: str = 'contract',
                           doc_name: str = '') -> List[Dict[str, any]]:
        """
        Alternative chunking strategy: split by paragraphs instead of word count

        Args:
            pages: List of page dicts
            doc_type: 'contract' or 'law'
            doc_name: Document name

        Returns:
            List of chunk dicts
        """
        chunks = []

        for page in pages:
            page_num = page['page']
            text = page['text']

            # Split by double newlines (paragraphs)
            paragraphs = re.split(r'\n\s*\n', text)

            for i, para in enumerate(paragraphs):
                para = para.strip()
                if not para or len(para) < 50:  # Skip very short paragraphs
                    continue

                # If paragraph is too long, split it
                if len(para.split()) > self.chunk_size:
                    sub_chunks = self._chunk_text(para)
                    for j, sub_chunk in enumerate(sub_chunks):
                        chunk = {
                            'text': sub_chunk,
                            'page': page_num,
                            'chunk_index': f"{i}.{j}",
                            'doc_type': doc_type,
                            'doc_name': doc_name,
                            'extraction_method': page.get('method', 'unknown')
                        }

                        if doc_type == 'contract':
                            chunk['clause'] = self._extract_clause_info(sub_chunk)
                        elif doc_type == 'law':
                            chunk['article'] = self._extract_article_info(sub_chunk)

                        chunks.append(chunk)
                else:
                    chunk = {
                        'text': para,
                        'page': page_num,
                        'chunk_index': i,
                        'doc_type': doc_type,
                        'doc_name': doc_name,
                        'extraction_method': page.get('method', 'unknown')
                    }

                    if doc_type == 'contract':
                        chunk['clause'] = self._extract_clause_info(para)
                    elif doc_type == 'law':
                        chunk['article'] = self._extract_article_info(para)

                    chunks.append(chunk)

        logger.info(f"Created {len(chunks)} paragraph-based chunks from {len(pages)} pages")
        return chunks
