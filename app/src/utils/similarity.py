import numpy as np
from typing import List
import time
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def similarity(a: List[float], b: List[List[float]]) -> List[List[float]]:
    """
    Takes in a list of text and returns a list of embeddings
    """
    time_start = time.time()
    partial_sim = lambda single_b: cosine_similarity(a, single_b)

    with ThreadPoolExecutor() as executor:
        sim = executor.map(partial_sim, b)
    time_end = time.time()

    sim_list = [i[0] for i in sim]

    print(f"Concurrent semantic search took {time_end - time_start} seconds")
    return sim_list