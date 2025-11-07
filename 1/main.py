import os
import time
import heapq
from typing import List, Dict, Tuple
from shingling import Shingling
from compare_sets import CompareSets
from minhashing import MinHashing
from compare_signatures import CompareSignatures
from lsh import LSH

def load_documents(data_dir: str, num_docs: int = 1000) -> Dict[int, str]:
    documents = {}
    doc_id = 0
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if doc_id >= num_docs:
                return documents
            
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if content.strip():
                        documents[doc_id] = content
                        doc_id += 1
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
    
    return documents

def calculate_jaccard_similarity(documents: Dict[int, str], shingling: Shingling) -> List[Tuple[int, int, float]]:
    shingle_sets = {}
    for doc_id, content in documents.items():
        shingle_sets[doc_id] = shingling.create_shingles(content)

    top_k = []
    K = 10
    doc_ids = list(documents.keys())
    
    # Compare all pairs
    for i in range(len(doc_ids)):
        for j in range(i + 1, len(doc_ids)):
            sim = CompareSets.jaccard_similarity(
                shingle_sets[doc_ids[i]],
                shingle_sets[doc_ids[j]]
            )
            # Use heap to store the top 10 similar pairs
            # Store as (sim, doc_id1, doc_id2) so heap sorts by similarity
            if len(top_k) < K:
                heapq.heappush(top_k, (sim, doc_ids[i], doc_ids[j]))
            else:
                if sim > top_k[0][0]:
                    heapq.heapreplace(top_k, (sim, doc_ids[i], doc_ids[j]))
    # Convert back to (doc_id1, doc_id2, sim) format and sort descending
    return [(d1, d2, s) for s, d1, d2 in sorted(top_k, key=lambda x: x[0], reverse=True)]

def find_similar_documents_shingling(results: List[Tuple[int, int, float]], threshold: float) -> List[Tuple[int, int, float]]:
    similar_pairs = []
    for doc_id1, doc_id2, similarity in results:
        if similarity >= threshold:
            similar_pairs.append((doc_id1, doc_id2, similarity))
    
    return similar_pairs

def calculate_signature_similarity(documents: Dict[int, str], shingling: Shingling, minhashing: MinHashing) -> List[Tuple[int, int, float]]:
    signatures = {}
    for doc_id, content in documents.items():
        shingle_set = shingling.create_shingles(content)
        signatures[doc_id] = minhashing.compute_signature(shingle_set)

    top_k = []
    K = 10
    doc_ids = list(documents.keys())

    for i in range(len(doc_ids)):
        for j in range(i + 1, len(doc_ids)):
            sim = CompareSignatures.signature_similarity(
                signatures[doc_ids[i]],
                signatures[doc_ids[j]]
            )
            # Store as (sim, doc_id1, doc_id2) so heap sorts by similarity
            if len(top_k) < K:
                heapq.heappush(top_k, (sim, doc_ids[i], doc_ids[j]))
            else:
                if sim > top_k[0][0]:
                    heapq.heapreplace(top_k, (sim, doc_ids[i], doc_ids[j]))
    # Convert back to (doc_id1, doc_id2, sim) format and sort descending
    return [(d1, d2, s) for s, d1, d2 in sorted(top_k, key=lambda x: x[0], reverse=True)]

def find_similar_documents_minhash(results: List[Tuple[int, int, float]], threshold: float) -> List[Tuple[int, int, float]]:
    similar_pairs = []
    for doc_id1, doc_id2, similarity in results:
        if similarity >= threshold:
            similar_pairs.append((doc_id1, doc_id2, similarity))
    
    return similar_pairs


def calculate_lsh_similarity(documents: Dict[int, str], shingling: Shingling, minhashing: MinHashing, lsh: LSH) -> List[Tuple[int, int, float]]:
    signatures = {}
    for doc_id, content in documents.items():
        shingle_set = shingling.create_shingles(content)
        signatures[doc_id] = minhashing.compute_signature(shingle_set)

    sig_list = []
    doc_ids = []
    for doc_id in signatures.keys():
        sig_list.append(signatures[doc_id])
        doc_ids.append(doc_id)

    candidate_pairs = lsh.find_candidate_pairs(sig_list, doc_ids)

    top_k = []
    K = 10

    for doc_id1, doc_id2 in candidate_pairs:
        sim = CompareSignatures.signature_similarity(
            signatures[doc_id1],
            signatures[doc_id2]
        )
        # Store as (sim, doc_id1, doc_id2) so heap sorts by similarity
        if len(top_k) < K:
            heapq.heappush(top_k, (sim, doc_id1, doc_id2))
        else:
            if sim > top_k[0][0]:
                heapq.heapreplace(top_k, (sim, doc_id1, doc_id2))
    # Convert back to (doc_id1, doc_id2, sim) format and sort descending
    return [(d1, d2, s) for s, d1, d2 in sorted(top_k, key=lambda x: x[0], reverse=True)]

def find_similar_documents_lsh(results: List[Tuple[int, int, float]], threshold: float) -> List[Tuple[int, int, float]]:
    similar_pairs = []
    for doc_id1, doc_id2, similarity in results:
        if similarity >= threshold:
            similar_pairs.append((doc_id1, doc_id2, similarity))
    
    return similar_pairs


def main():
    # Configuration
    data_dir = "data/twenty+newsgroups/20_newsgroups"
    k = 10  # Shingle length
    num_permutations = 100  # Number of hash functions for minhashing
    similarity_threshold = 0.8
    num_docs = 1000
    
    # LSH parameters
    # For 100 permutations, we can use 10 bands with 10 rows each
    num_bands = 10
    num_rows_per_band = 10
    
    print(f"Config:")
    print(f"  Shingle length: {k}")
    print(f"  Number of permutations: {num_permutations}")
    print(f"  Similarity threshold: {similarity_threshold}")
    print(f"  Number of docs: {num_docs}")
    print(f"  LSH bands: {num_bands}, rows per band: {num_rows_per_band}")
    print()
    print("Loading docs...")
    docs = load_documents(data_dir, num_docs)
    print()
    if len(docs) < 2:
        print("Error: Need at least 2 docs to compare")
        return
    
    shingling = Shingling(k=k)
    minhashing = MinHashing(num_permutations=num_permutations)
    lsh = LSH(num_bands=num_bands, 
              num_rows_per_band=num_rows_per_band,
              threshold=similarity_threshold)
    
    # Shingling and Jaccard similarity
    print("Shingling and Jaccard Similarity")

    start_time = time.time()
    results = calculate_jaccard_similarity(docs, shingling)
    shingling_time = time.time() - start_time

    print(f"Execution time: {shingling_time:.4f} seconds")
    print(f"Found {len(results)} pairs:")
    for doc_id1, doc_id2, sim in sorted(results, key=lambda x: x[2], reverse=True):
        print(f"  Documents {doc_id1} and {doc_id2}: similarity = {sim:.4f}")
    print()

    similar_pairs_shingling = find_similar_documents_shingling(results, similarity_threshold)
    print(f"Found {len(similar_pairs_shingling)} similar pairs:")
    for doc_id1, doc_id2, sim in sorted(similar_pairs_shingling, key=lambda x: x[2], reverse=True):
        print(f"  Documents {doc_id1} and {doc_id2}: similarity = {sim:.4f}")
    print()
    
    # MinHash signatures
    print("MinHash Signatures")
    start_time = time.time()
    results = calculate_signature_similarity(docs, shingling, minhashing)
    mh_time = time.time() - start_time
    print(f"Execution time: {mh_time:.4f} seconds")
    print(f"Found {len(results)} pairs:")
    for doc_id1, doc_id2, sim in sorted(results, key=lambda x: x[2], reverse=True):
        print(f"  Documents {doc_id1} and {doc_id2}: similarity = {sim:.4f}")
    print()

    similar_pairs_mh = find_similar_documents_minhash(results, similarity_threshold)
    print(f"Found {len(similar_pairs_mh)} similar pairs:")
    for doc_id1, doc_id2, sim in sorted(similar_pairs_mh, key=lambda x: x[2], reverse=True):
        print(f"  Documents {doc_id1} and {doc_id2}: similarity = {sim:.4f}")
    print()
    
    # LSH
    print("LSH")
    start_time = time.time()
    results = calculate_lsh_similarity(docs, shingling, minhashing, lsh)
    lsh_time = time.time() - start_time
    
    print(f"Execution time: {lsh_time:.4f} seconds")
    print(f"Found {len(results)} pairs:")
    for doc_id1, doc_id2, sim in sorted(results, key=lambda x: x[2], reverse=True):
        print(f"  Documents {doc_id1} and {doc_id2}: similarity = {sim:.4f}")
    print()

    similar_pairs_lsh = find_similar_documents_lsh(results, similarity_threshold)
    print(f"Found {len(similar_pairs_lsh)} similar pairs:")
    for doc_id1, doc_id2, sim in sorted(similar_pairs_lsh, key=lambda x: x[2], reverse=True):
        print(f"  Documents {doc_id1} and {doc_id2}: similarity = {sim:.4f}")
    print()
    
    # Summary
    print("Summary")
    print(f"Shingling time: {shingling_time:.4f} seconds")
    print(f"MinHash time: {mh_time:.4f} seconds")
    print(f"LSH time: {lsh_time:.4f} seconds")
    print()
    print(f"Speedup (MinHash vs Shingling): {shingling_time/mh_time:.2f}x")
    print(f"Speedup (LSH vs Shingling): {shingling_time/lsh_time:.2f}x")
    print()
    
    # Compare results
    shingling_pairs_set = {(d1, d2) for d1, d2, _ in similar_pairs_shingling}
    mh_pairs_set = {(d1, d2) for d1, d2, _ in similar_pairs_mh}
    lsh_pairs_set = {(d1, d2) for d1, d2, _ in similar_pairs_lsh}
    
    print("Pair comparison:")
    print(f"  Shingling pairs: {len(shingling_pairs_set)}")
    print(f"  MinHash pairs: {len(mh_pairs_set)}")
    print(f"  LSH pairs: {len(lsh_pairs_set)}")
    print(f"  MinHash matches Shingling: {shingling_pairs_set == mh_pairs_set}")
    print(f"  LSH candidate pairs: {len(lsh_pairs_set)} (may include false positives)")

if __name__ == "__main__":
    main()