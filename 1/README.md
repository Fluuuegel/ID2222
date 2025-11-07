# Homework 1: Finding Similar Items: Textually Similar Documents

This implementation finds textually similar documents based on Jaccard similarity using:

- **Shingling**: Creates k-shingles and hashes them
- **MinHashing**: Builds minHash signatures to approximate Jaccard similarity
- **Locality-Sensitive Hashing (LSH)**: Efficiently finds candidate pairs of similar documents

## Dataset

[Twenty Newsgroups - UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/113/twenty+newsgroups)

## Implementation

The project consists of the following modules:

### Core Classes

1. **`Shingling`** (`shingling.py`): Constructs k-shingles of a given length k from a document, computes hash values for each unique shingle, and represents the document as an ordered set of hashed k-shingles.
2. **`CompareSets`** (`compare_sets.py`): Computes the Jaccard similarity of two sets of integers (sets of hashed shingles).
3. **`MinHashing`** (`minhashing.py`): Builds a minHash signature (vector) of a given length n from a given set of integers (a set of hashed shingles).
4. **`CompareSignatures`** (`compare_signatures.py`): Estimates the similarity of two integer vectors (minhash signatures) as a fraction of components in which they agree.
5. **`LSH`** (`lsh.py`): Implements the LSH technique using banding and hashing to find candidate pairs of signatures agreeing on at least a fraction t of their components.

## Usage

### Running the Main Program

```bash
python main.py
```

The main program:

- Loads 1000 documents from the dataset
- Finds similar documents using three methods:
  1. **Shingling**: Direct Jaccard similarity comparison
  2. **MinHash**: Using minHash signatures
  3. **LSH**: Using Locality-Sensitive Hashing
- Reports execution times and similar pairs found(top 10)
- Compares results

### Configuration

You can modify the following parameters in `main.py`:

- `k`: Shingle length (default: 10)
- `num_permutations`: Number of hash functions for minhashing (default: 100)
- `similarity_threshold`: Threshold for considering documents similar (default: 0.8)
- `num_docs`: Number of documents to process (default: 1000)
- `num_bands`: Number of bands for LSH (default: 10)
- `num_rows_per_band`: Number of rows per band for LSH (default: 10)

### Example Usage

```python
from shingling import Shingling
from compare_sets import CompareSets
from minhashing import MinHashing
from compare_signatures import CompareSignatures
from lsh import LSH

# Create shingles
shingling = Shingling(k=10)
doc1_shingles = shingling.create_shingles("Your document text here...")

# Compare sets
set1 = {1, 2, 3, 4, 5}
set2 = {3, 4, 5, 6, 7}
similarity = CompareSets.jaccard_similarity(set1, set2)

# Create minhash signature
minhashing = MinHashing(num_permutations=100)
signature = minhashing.compute_signature(doc1_shingles)

# Compare signatures
sig1 = [1, 2, 3, 4, 5]
sig2 = [1, 2, 3, 6, 7]
sig_similarity = CompareSignatures.signature_similarity(sig1, sig2)

# Use LSH
lsh = LSH(num_bands=10, num_rows_per_band=10, threshold=0.8)
candidate_pairs = lsh.find_candidate_pairs([sig1, sig2], [0, 1])
```

## Requirements

No external dependencies required. The implementation uses only Python standard library.

## Notes

- The similarity threshold of 0.8 is quite high and may not find many similar pairs in diverse document collections
- LSH is most beneficial for large document collections where brute force comparison becomes expensive
