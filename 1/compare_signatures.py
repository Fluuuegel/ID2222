from typing import List

class CompareSignatures:
    @staticmethod
    def signature_similarity(sig1: List[int], sig2: List[int]) -> float:
        if len(sig1) != len(sig2):
            raise ValueError("Signatures must have the same length")
        
        if len(sig1) == 0:
            return 0.0
        
        # Count the num of positions where sig agree
        agree = sum(1 for i in range(len(sig1)) 
                        if sig1[i] == sig2[i])
        
        return agree / len(sig1)

