import os
from functools import lru_cache

import numpy as np
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

from src.const.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embeddings() -> NVIDIAEmbeddings:
    load_dotenv(".env")
    # truncate="END": 입력이 모델 한도를 넘으면 뒷부분을 잘라 오류 대신 계속 진행
    return NVIDIAEmbeddings(model=EMBEDDING_MODEL, api_key=os.getenv("nvidiaapi_key"), truncate="END")


def normalize(vectors: list[list[float]]) -> np.ndarray:
    """길이를 1로 맞춘다. 이렇게 하면 내적(inner product)이 곧 코사인 유사도가 된다."""
    arr = np.asarray(vectors, dtype="float32")
    return arr / np.linalg.norm(arr, axis=1, keepdims=True)
