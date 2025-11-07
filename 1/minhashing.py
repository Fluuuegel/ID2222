import random
from typing import Set, List

class MinHashing:
    def __init__(self, num_permutations: int = 100, seed: int = 42):
        self.n = num_permutations
        self.s = seed
        random.seed(seed)
        
        self.p = 2147483647
        self.params = []
        
        for _ in range(num_permutations):
            a = random.randint(1, self.p - 1)
            b = random.randint(0, self.p - 1)
            self.params.append((a, b))
    
    def compute_signature(self, shingles: Set[int]) -> List[int]:
        sig = []
        
        for a, b in self.params:
            mh = self.p
            
            for s in shingles:
                hv = ((a * s + b) % self.p)
                mh = min(mh, hv)
            
            sig.append(mh)
        
        return sig
