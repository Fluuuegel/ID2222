from typing import Set

class CompareSets:
    @staticmethod
    def jaccard_similarity(set1: Set[int], set2: Set[int]) -> float:
        if not set1 and not set2:
            return 1.0
        
        if not set1 or not set2:
            return 0.0
        
        inter = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            return 0.0
        
        return inter / union

