import numpy as np

from src.vectorstore.embedder import normalize


def test_normalize_makes_unit_vectors_so_inner_product_is_cosine():
    out = normalize([[3.0, 4.0], [0.0, 2.0]])
    assert np.allclose(np.linalg.norm(out, axis=1), 1.0)
    assert np.allclose(out[0], [0.6, 0.8])
