from typing import Set, FrozenSet, DefaultDict
from collections import defaultdict
import random


def parse_edge(line: str) -> FrozenSet[int]:
    """Parse edge from line, return frozenset of vertices"""
    u, v = map(int, line.split())
    return frozenset([u, v])


class ReservoirSampler:
    """Reservoir Sampling algorithm - maintains a fixed-size random sample"""
    
    def __init__(self, sample_size: int):
        self.sample_size = sample_size
        self.sample: Set[FrozenSet[int]] = set()
        self.stream_cnt = 0
    
    def should_include(self) -> bool:
        """Decide whether the current element should be included in the sample"""
        self.stream_cnt += 1
        
        if len(self.sample) < self.sample_size:
            return True
        
        # Keep new element with probability M/t
        if random.random() < self.sample_size / self.stream_cnt:
            return True
        
        return False
    
    def add(self, edge: FrozenSet[int]):
        """Add edge to sample, randomly remove an edge if sample is full"""
        if len(self.sample) < self.sample_size:
            self.sample.add(edge)
        else:
            # Randomly select an edge to remove
            edge_to_remove = random.choice(list(self.sample))
            self.sample.remove(edge_to_remove)
            self.sample.add(edge)


class StreamingTriangleCounter:
    """Streaming triangle counting algorithm using Reservoir Sampling (Triest)"""
    
    def __init__(self, file_path: str, memory_size: int):
        self.file_path = file_path
        self.memory_size = memory_size
        
        # Use reservoir sampling to maintain edge sample
        self.reservoir = ReservoirSampler(memory_size)
        
        # Triangle counters
        self.triangle_count = 0
        self.vertex_triangles: DefaultDict[int, float] = defaultdict(float)
        
        # Number of edges in stream
        self.edge_cnt = 0
    
    def find_neighbors(self, edge: FrozenSet[int]) -> Set[int]:
        """Find common neighbors of the two vertices in the edge"""
        u, v = edge
        
        neighbors_u = set()
        neighbors_v = set()
        
        for sampled_edge in self.reservoir.sample:
            if u in sampled_edge:
                neighbors_u.update(sampled_edge - {u})
            if v in sampled_edge:
                neighbors_v.update(sampled_edge - {v})
        
        return neighbors_u & neighbors_v
    
    def update_triangles(self, edge: FrozenSet[int], weight: float):
        """Update triangle count"""
        common_neighbors = self.find_neighbors(edge)
        
        for neighbor in common_neighbors:
            self.triangle_count += weight
            self.vertex_triangles[neighbor] += weight
            for vertex in edge:
                self.vertex_triangles[vertex] += weight
    
    def get_estimation_factor(self) -> float:
        """Calculate estimation factor (Triest-IMPROVED version)"""
        if self.edge_cnt <= 2:
            return 1.0
        
        t = self.edge_cnt
        M = self.memory_size
        
        # eta = max(1, (t-1)(t-2) / (M(M-1)))
        return max(1.0, (t - 1) * (t - 2) / (M * (M - 1)))
    
    def run(self) -> float:
        """Run algorithm to process stream data"""
        with open(self.file_path, 'r') as f:
            for line in f:
                edge = parse_edge(line.strip())
                self.edge_cnt += 1
                eta = self.get_estimation_factor()
                self.update_triangles(edge, eta)
                if self.reservoir.should_include():
                    self.reservoir.add(edge)
        return self.triangle_count


if __name__ == "__main__":
    memory_sizes = [1000, 2000, 5000, 10000, 20000]
    num_runs = 5
    file_path = 'data/facebook_combined.txt'
    results_file = 'results.txt'
    
    with open(results_file, 'w', encoding='utf-8') as f:
        for memory_size in memory_sizes:
            results = []
            for run_num in range(1, num_runs + 1):
                counter = StreamingTriangleCounter(file_path, memory_size)
                result = counter.run()
                results.append(result)
                f.write(f"M={memory_size}, Run {run_num}: {result:.2f}\n")
            avg = sum(results) / len(results)
            f.write(f"M={memory_size}, Average: {avg:.2f}\n\n")

