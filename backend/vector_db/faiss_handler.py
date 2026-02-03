import faiss
import numpy as np
import pickle
from typing import List, Dict, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FAISSHandler:
    """Handle FAISS vector database operations"""

    def __init__(self, dimension: int = 3072):
        """
        Initialize FAISS handler

        Args:
            dimension: Embedding vector dimension
        """
        self.dimension = dimension
        self.index = None
        self.metadata = []  # Store chunk metadata

    def create_index(self, embeddings: List[List[float]], chunks: List[Dict[str, any]]):
        """
        Create FAISS index from embeddings

        Args:
            embeddings: List of embedding vectors
            chunks: List of chunk dicts with metadata
        """
        logger.info(f"Creating FAISS index with {len(embeddings)} vectors...")

        # Convert to numpy array
        embeddings_array = np.array(embeddings).astype('float32')

        # Create FAISS index (using IndexFlatL2 for exact search)
        # For larger datasets, consider IndexIVFFlat or IndexHNSW
        self.index = faiss.IndexFlatL2(self.dimension)

        # Add vectors to index
        self.index.add(embeddings_array)

        # Store metadata (without embeddings to save space)
        self.metadata = []
        for chunk in chunks:
            meta = {k: v for k, v in chunk.items() if k != 'embedding'}
            self.metadata.append(meta)

        logger.info(f"FAISS index created with {self.index.ntotal} vectors")

    def add_to_index(self, embeddings: List[List[float]], chunks: List[Dict[str, any]]):
        """
        Add more embeddings to existing index

        Args:
            embeddings: List of embedding vectors to add
            chunks: List of chunk dicts with metadata
        """
        if self.index is None:
            logger.warning("No existing index, creating new one")
            self.create_index(embeddings, chunks)
            return

        logger.info(f"Adding {len(embeddings)} vectors to existing index...")

        # Convert to numpy array
        embeddings_array = np.array(embeddings).astype('float32')

        # Add to index
        self.index.add(embeddings_array)

        # Add metadata
        for chunk in chunks:
            meta = {k: v for k, v in chunk.items() if k != 'embedding'}
            self.metadata.append(meta)

        logger.info(f"Index now contains {self.index.ntotal} vectors")

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, any]]:
        """
        Search for similar chunks

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return

        Returns:
            List of chunk dicts with similarity scores
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Index is empty, no results to return")
            return []

        # Convert to numpy array
        query_array = np.array([query_embedding]).astype('float32')

        # Search
        distances, indices = self.index.search(query_array, min(top_k, self.index.ntotal))

        # Prepare results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['similarity_score'] = float(1 / (1 + distance))  # Convert distance to similarity
                result['rank'] = i + 1
                results.append(result)

        return results

    def save_index(self, filepath: str):
        """
        Save FAISS index and metadata to disk

        Args:
            filepath: Path to save index (without extension)
        """
        if self.index is None:
            logger.warning("No index to save")
            return

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        index_path = str(filepath.with_suffix('.faiss'))
        faiss.write_index(self.index, index_path)

        # Save metadata
        metadata_path = str(filepath.with_suffix('.pkl'))
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)

        logger.info(f"Index saved to {index_path}")

    def load_index(self, filepath: str):
        """
        Load FAISS index and metadata from disk

        Args:
            filepath: Path to index (without extension)
        """
        filepath = Path(filepath)

        # Load FAISS index
        index_path = str(filepath.with_suffix('.faiss'))
        if not Path(index_path).exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")

        self.index = faiss.read_index(index_path)

        # Load metadata
        metadata_path = str(filepath.with_suffix('.pkl'))
        if Path(metadata_path).exists():
            with open(metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            logger.warning(f"Metadata file not found: {metadata_path}")
            self.metadata = []

        logger.info(f"Index loaded with {self.index.ntotal} vectors")

    def delete_index(self, filepath: str):
        """
        Delete index files from disk

        Args:
            filepath: Path to index (without extension)
        """
        filepath = Path(filepath)

        # Delete FAISS index
        index_path = filepath.with_suffix('.faiss')
        if index_path.exists():
            index_path.unlink()
            logger.info(f"Deleted index: {index_path}")

        # Delete metadata
        metadata_path = filepath.with_suffix('.pkl')
        if metadata_path.exists():
            metadata_path.unlink()
            logger.info(f"Deleted metadata: {metadata_path}")

    def get_stats(self) -> Dict[str, any]:
        """
        Get index statistics

        Returns:
            Dict with index stats
        """
        return {
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'metadata_count': len(self.metadata)
        }


class ContractVectorDB(FAISSHandler):
    """Specialized FAISS handler for contracts"""

    def search_contracts(self, query_embedding: List[float], top_k: int = 5,
                        filter_contract: str = None) -> List[Dict[str, any]]:
        """
        Search contracts with optional filtering

        Args:
            query_embedding: Query embedding
            top_k: Number of results
            filter_contract: Filter by contract name

        Returns:
            List of relevant contract chunks
        """
        results = self.search(query_embedding, top_k * 2)  # Get more results for filtering

        if filter_contract:
            results = [r for r in results if r.get('doc_name') == filter_contract]

        return results[:top_k]


class LawVectorDB(FAISSHandler):
    """Specialized FAISS handler for laws"""

    def search_laws(self, query_embedding: List[float], top_k: int = 5,
                   filter_law_number: str = None) -> List[Dict[str, any]]:
        """
        Search laws with optional filtering

        Args:
            query_embedding: Query embedding
            top_k: Number of results
            filter_law_number: Filter by law number

        Returns:
            List of relevant law chunks
        """
        results = self.search(query_embedding, top_k * 2)

        if filter_law_number:
            results = [r for r in results if filter_law_number in r.get('doc_name', '')]

        return results[:top_k]
