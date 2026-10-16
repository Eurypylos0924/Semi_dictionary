from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_PATH = Path("data/processed/papers.jsonl")
REMOVED_PATH = Path("data/processed/removed.jsonl")
INDEX_DIR = Path("data/index")
FAISS_PATH = INDEX_DIR / "papers.faiss"
DOCS_PATH = INDEX_DIR / "papers_meta.jsonl"

EMBEDDING_MODEL = "nvidia/nemotron-3-embed-1b"
EMBED_BATCH_SIZE = 32
