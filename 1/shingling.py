from typing import Set, List

class Shingling:
    
    def __init__(self, k: int = 10):
        self.k = k
    
    def create_shingles(self, doc: str) -> Set[int]:
        if len(doc) < self.k:
            # If document is shorter than k, return a single shingle
            return {hash(doc)}
        
        shingles = set()
        
        # Create k-shingles by sliding a window of size k
        for i in range(len(doc) - self.k + 1):
            shingle = doc[i:i + self.k]
            shingles.add(hash(shingle))
        
        return shingles

