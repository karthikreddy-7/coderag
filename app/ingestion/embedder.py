# embedder.py - Embedding model calls
import logging

from sentence_transformers import SentenceTransformer
from app.config import config
from app.config.logging_config import setup_logging

logger = logging.getLogger(__name__)

class Embedder:
    def __init__(self, model_path: str | None = None):
        path = model_path or config.EMBEDDING_MODEL_PATH
        logger.info("Loading embedding model from: %s", path)
        self.model = SentenceTransformer(path)

    def get_embedding(self, text: str):
        """
        Get embedding vector for a single text input
        """
        logger.debug("Encoding single text: %s...", text[:50])
        return self.model.encode(text, convert_to_numpy=True)

    def get_embeddings(self, texts: list[str]):
        """
        Get embedding vectors for multiple texts
        """
        logger.debug("Encoding %d texts", len(texts))
        return self.model.encode(texts, convert_to_numpy=True)


"""
if __name__ == "__main__":
    setup_logging()
    embedder = Embedder()
    text = "ChatGPT is amazing for backend devs!"
    embedding = embedder.get_embedding(text)
    logger.info("Embedding shape: %s", embedding.shape)
    logger.info("First 5 values: %s", embedding[:5])
"""
