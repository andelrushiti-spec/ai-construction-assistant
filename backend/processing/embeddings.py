"""
Construction Legal Assistant
Embedding Generator - Create Text Embeddings using OpenAI

Developer: Andel Albdesk
Copyright (c) 2026 Andel Albdesk. All rights reserved.
"""

import openai
from typing import List, Dict
import numpy as np
import logging
from pathlib import Path
import time

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Generate embeddings using OpenAI API"""

    def __init__(self, api_key: str, model: str = "text-embedding-3-large", batch_size: int = 100):
        """
        Initialize embedding generator

        Args:
            api_key: OpenAI API key
            model: Embedding model name
            batch_size: Number of texts to embed per API call
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.batch_size = batch_size

    def embed_chunks(self, chunks: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Generate embeddings for text chunks

        Args:
            chunks: List of chunk dicts with 'text' field

        Returns:
            List of chunks with added 'embedding' field
        """
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")

        # Process in batches
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i + self.batch_size]
            batch_texts = [chunk['text'] for chunk in batch]

            try:
                # Call OpenAI API
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch_texts
                )

                # Add embeddings to chunks
                for j, chunk in enumerate(batch):
                    chunk['embedding'] = response.data[j].embedding

                logger.info(f"Processed batch {i // self.batch_size + 1}/{(len(chunks) - 1) // self.batch_size + 1}")

                # Rate limiting - be nice to the API
                if i + self.batch_size < len(chunks):
                    time.sleep(0.5)

            except Exception as e:
                logger.error(f"Error generating embeddings for batch {i}: {str(e)}")
                raise

        logger.info(f"Successfully generated {len(chunks)} embeddings")
        return chunks

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query

        Args:
            query: Query text

        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=[query]
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings for this model

        Returns:
            Embedding dimension (3072 for text-embedding-3-large)
        """
        # text-embedding-3-large produces 3072-dimensional embeddings
        # text-embedding-3-small produces 1536-dimensional embeddings
        if 'large' in self.model:
            return 3072
        elif 'small' in self.model:
            return 1536
        else:
            # Default fallback
            return 1536

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)
