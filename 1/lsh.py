from typing import List, Dict, Set, Tuple

class LSH:
    
    def __init__(self, num_bands: int, num_rows_per_band: int, threshold: float):
        self.b = num_bands
        self.r = num_rows_per_band
        self.t = threshold
    
    def _hash_band(self, band: List[int]) -> int:
        return hash(tuple(band))
    
    def find_candidate_pairs(self, sigs: List[List[int]], ids: List[int] = None) -> Set[Tuple[int, int]]:
        if not sigs:
            return set()
        
        len_sig = len(sigs[0])
        
        if self.b * self.r != len_sig:
            raise ValueError(
                f"num_bands ({self.b}) * num_rows_per_band "
                f"({self.r}) must equal signature length "
                f"({len_sig})"
            )
        
        if ids is None:
            ids = list(range(len(sigs)))
        
        if len(ids) != len(sigs):
            raise ValueError("Number of doc_ids must match number of signatures")
        
        buckets: Dict[int, Dict[int, Set[int]]] = {}
        
        for bi in range(self.b):
            buckets[bi] = {}
        
        for doc_id, sig in zip(ids, sigs):
            for bi in range(self.b):
                start = bi * self.r
                end = start + self.r
                band = sig[start:end]
                
                bh = self._hash_band(band)
                
                if bh not in buckets[bi]:
                    buckets[bi][bh] = set()
                buckets[bi][bh].add(doc_id)
        
        pairs = set()
        
        for bi in range(self.b):
            for bh, ds in buckets[bi].items():
                dl = sorted(list(ds))
                for i in range(len(dl)):
                    for j in range(i + 1, len(dl)):
                        pairs.add((dl[i], dl[j]))
        
        return pairs
