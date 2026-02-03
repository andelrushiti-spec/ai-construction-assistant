"""
Simplified NumPy-based vector database (FAISS alternative for testing)
"""
import numpy as np
import pickle
from typing import List, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class NumpyVectorDB:
    """Simple numpy-based vector database for testing"""

    def __init__(self, dimension: int = 3072):
        self.dimension = dimension
        self.vectors = None
        self.metadata = []

    def create_index(self, embeddings: List[List[float]], chunks: List[Dict[str, any]]):
        """Create index from embeddings"""
        logger.info(f"Creating numpy index with {len(embeddings)} vectors...")

        self.vectors = np.array(embeddings, dtype=np.float32)
        self.metadata = []
        for chunk in chunks:
            meta = {k: v for k, v in chunk.items() if k != 'embedding'}
            self.metadata.append(meta)

        logger.info(f"Index created with {len(self.vectors)} vectors")

    def add_to_index(self, embeddings: List[List[float]], chunks: List[Dict[str, any]]):
        """Add more embeddings to existing index"""
        if self.vectors is None:
            self.create_index(embeddings, chunks)
            return

        logger.info(f"Adding {len(embeddings)} vectors to existing index...")

        new_vectors = np.array(embeddings, dtype=np.float32)
        self.vectors = np.vstack([self.vectors, new_vectors])

        for chunk in chunks:
            meta = {k: v for k, v in chunk.items() if k != 'embedding'}
            self.metadata.append(meta)

        logger.info(f"Index now contains {len(self.vectors)} vectors")

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, any]]:
        """Search for similar chunks using cosine similarity"""
        if self.vectors is None or len(self.vectors) == 0:
            logger.warning("Index is empty, no results to return")
            return []

        query = np.array(query_embedding, dtype=np.float32)

        # Compute cosine similarity
        # similarity = (A · B) / (||A|| * ||B||)
        dots = np.dot(self.vectors, query)
        norms = np.linalg.norm(self.vectors, axis=1) * np.linalg.norm(query)
        similarities = dots / (norms + 1e-10)  # Add small value to prevent division by zero

        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # Prepare results
        results = []
        for rank, idx in enumerate(top_indices):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['similarity_score'] = float(similarities[idx])
                result['rank'] = rank + 1
                results.append(result)

        return results

    def save_index(self, filepath: str):
        """Save index and metadata to disk"""
        if self.vectors is None:
            logger.warning("No index to save")
            return

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Save vectors
        vectors_path = str(filepath.with_suffix('.npy'))
        np.save(vectors_path, self.vectors)

        # Save metadata
        metadata_path = str(filepath.with_suffix('.pkl'))
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)

        logger.info(f"Index saved to {vectors_path}")

    def load_index(self, filepath: str):
        """Load index and metadata from disk"""
        filepath = Path(filepath)

        # Load vectors
        vectors_path = str(filepath.with_suffix('.npy'))
        if not Path(vectors_path).exists():
            raise FileNotFoundError(f"Index file not found: {vectors_path}")

        self.vectors = np.load(vectors_path)

        # Load metadata
        metadata_path = str(filepath.with_suffix('.pkl'))
        if Path(metadata_path).exists():
            with open(metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            logger.warning(f"Metadata file not found: {metadata_path}")
            self.metadata = []

        logger.info(f"Index loaded with {len(self.vectors)} vectors")

    def delete_index(self, filepath: str):
        """Delete index files from disk"""
        filepath = Path(filepath)

        # Delete vectors
        vectors_path = filepath.with_suffix('.npy')
        if vectors_path.exists():
            vectors_path.unlink()
            logger.info(f"Deleted vectors: {vectors_path}")

        # Delete metadata
        metadata_path = filepath.with_suffix('.pkl')
        if metadata_path.exists():
            metadata_path.unlink()
            logger.info(f"Deleted metadata: {metadata_path}")

    def get_stats(self) -> Dict[str, any]:
        """Get index statistics"""
        return {
            'total_vectors': len(self.vectors) if self.vectors is not None else 0,
            'dimension': self.dimension,
            'metadata_count': len(self.metadata)
        }


class ContractVectorDB(NumpyVectorDB):
    """Specialized handler for contracts"""

    def search_contracts(self, query_embedding: List[float], top_k: int = 5,
                        filter_contract: str = None) -> List[Dict[str, any]]:
        results = self.search(query_embedding, top_k * 2)

        if filter_contract:
            results = [r for r in results if r.get('doc_name') == filter_contract]

        return results[:top_k]


class LawVectorDB(NumpyVectorDB):
    """Specialized handler for laws"""

    def search_laws(self, query_embedding: List[float], top_k: int = 5,
                   filter_law_number: str = None) -> List[Dict[str, any]]:
        results = self.search(query_embedding, top_k * 2)

        if filter_law_number:
            results = [r for r in results if filter_law_number in r.get('doc_name', '')]

        return results[:top_k]
