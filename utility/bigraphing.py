from __future__ import annotations
import numpy as np
from typing import Literal, Iterable
from collections import deque
import time


def get_random_ui_matrix(num_user: int, num_item: int, num_rating: int):
    mat = np.array([], dtype=np.int64).reshape((0, 2))
    while mat.shape[0] < num_rating:
        user = np.random.randint(num_user)
        item = np.random.randint(num_item)
        ui = np.array([[user, item]])
        if (ui == mat).all(1).any():
            continue
        mat = np.append(mat, ui, axis=0)
    return mat


class Node:
    def __init__(self, type: int, index: int):
        self.type = type
        self.index = index
        self.neighbors: set[Node] = set()

    @property
    def degree(self):
        return len(self.neighbors)

    def connect(self, other: Node):
        assert self.type != other.type, "Cannot connect to node of the same type."
        self.neighbors.add(other)

    def disconnect(self):
        for n in self.neighbors:
            n.neighbors.remove(self)
        self.neighbors = set()

    def __repr__(self):
        return f"Node(type: {self.type}, degree {self.degree})"


def prune_bigraph(
    a: Iterable[int],
    b: Iterable[int],
    counts: tuple[int, int],
    thresholds: tuple[int, int],
    mode: Literal["valid", "info"] = "valid",
):
    num_a, num_b = counts
    nodes_a = [Node(0, i) for i in range(num_a)]
    nodes_b = [Node(1, i) for i in range(num_b)]
    start_time = time.time()
    for a_idx, b_idx in zip(a, b):
        time_taken = time.time() - start_time
        print(f"[INFO] Creating Bigraph, time taken: {time_taken: .2f}s", end="\r")
        node_a, node_b = nodes_a[int(a_idx)], nodes_b[int(b_idx)]
        node_a.connect(node_b)
        node_b.connect(node_a)
    print()
    # Pruning
    removed = set()
    process_queue = deque(nodes_a + nodes_b)
    start_time = time.time()
    while process_queue:
        time_taken = time.time() - start_time
        print(f"[INFO] Pruning, time taken: {time_taken: .2f}s", end="\r")
        node = process_queue.popleft()
        if node in removed:
            continue
        if node.degree < thresholds[node.type]:
            process_queue.extend(node.neighbors)
            node.disconnect()
            removed.add(node)
    print(f"\n[INFO] Returning {mode}")
    match mode:
        case "valid":
            valid_a = [i for i in range(num_a) if nodes_a[i].degree]
            valid_b = [i for i in range(num_b) if nodes_b[i].degree]
            return valid_a, valid_b
        case "info":
            info_a = {i: nodes_a[i].degree for i in range(num_a)}
            info_b = {i: nodes_b[i].degree for i in range(num_b)}
            return info_a, info_b


if __name__ == "__main__":
    num_users, num_items = 20, 20
    num_ratings = 200
    ratings_mat = get_random_ui_matrix(num_users, num_items, num_ratings)
    # Initial graph
    a, b = ratings_mat.T
    valid_users, valid_items = prune_bigraph(
        a, b, counts=(num_users, num_items), thresholds=(10, 2), mode="valid"
    )
    print(valid_users)
    print(valid_items)
