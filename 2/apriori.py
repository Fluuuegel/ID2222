def load_data(filename):
    transactions = []
    with open(filename, 'r') as f:
        for line in f:
            # Convert each line to a set of items (int)
            items = set(map(int, line.strip().split()))
            transactions.append(items)
    return transactions


def get_frequent_1_itemsets(transactions, min_support):
    item_counts = {}
    
    # Count occurrences of each item
    for transaction in transactions:
        for item in transaction:
            item_counts[item] = item_counts.get(item, 0) + 1
    
    # Filter items with support >= min_support
    frequent_items = {}
    for item, count in item_counts.items():
        if count >= min_support:
            frequent_items[frozenset([item])] = count
    
    return frequent_items


def generate_candidates(prev_frequent, k):
    candidates = set()
    prev_itemsets = list(prev_frequent.keys())
    
    # Join step: combine itemsets that share first k-2 items
    for i in range(len(prev_itemsets)):
        for j in range(i + 1, len(prev_itemsets)):
            itemset1 = prev_itemsets[i]
            itemset2 = prev_itemsets[j]
            list1 = sorted(list(itemset1))
            list2 = sorted(list(itemset2))
            
            # Check if first k-2 items are the same
            if k == 2 or list1[:k-2] == list2[:k-2]:
                # Create new candidate by union
                new_candidate = itemset1 | itemset2
                if len(new_candidate) == k:
                    candidates.add(new_candidate)
    
    return candidates


def prune_candidates(candidates, prev_frequent, k):
    pruned_candidates = set()
    
    for candidate in candidates:
        # Check if all (k-1)-subsets are frequent
        candidate_list = sorted(list(candidate))
        is_valid = True
        
        # Generate all (k-1)-subsets
        for i in range(len(candidate_list)):
            subset = frozenset(candidate_list[:i] + candidate_list[i+1:])
            if subset not in prev_frequent:
                is_valid = False
                break
        
        if is_valid:
            pruned_candidates.add(candidate)
    
    return pruned_candidates


def count_support(transactions, candidates):
    support_counts = {}
    
    for candidate in candidates:
        count = 0
        for transaction in transactions:
            # Check if transaction contains the candidate
            if candidate.issubset(transaction):
                count += 1
        support_counts[candidate] = count
    
    return support_counts


def apriori(transactions, min_support):
    all_frequent = {}
    
    # Find frequent 1-itemsets
    k = 1
    frequent_k = get_frequent_1_itemsets(transactions, min_support)
    all_frequent.update(frequent_k)
    # Iteratively find frequent k-itemsets for k >= 2
    k = 2
    while frequent_k:
        # Generate candidates
        candidates = generate_candidates(frequent_k, k)
        candidates = prune_candidates(candidates, frequent_k, k)
        support_counts = count_support(transactions, candidates)
        # Filter frequent itemsets
        frequent_k = {
            itemset: count 
            for itemset, count in support_counts.items() 
            if count >= min_support
        }
        all_frequent.update(frequent_k)
        k += 1
    return all_frequent


def generate_rules(frequent_itemsets, transactions, min_support, min_confidence):
    rules = []
    # Only consider itemsets with size >= 2
    for itemset, support in frequent_itemsets.items():
        if len(itemset) < 2:
            continue
        
        # Generate all possible rules X -> Y where X ∪ Y = itemset
        itemset_list = list(itemset)
        # Generate all non-empty proper subsets as antecedents
        for i in range(1, 2 ** len(itemset_list) - 1):
            # Create antecedent X
            X = frozenset([itemset_list[j] for j in range(len(itemset_list)) 
                          if (i >> j) & 1])
            Y = itemset - X
        
            if len(Y) == 0:
                continue
            
            # X must be a frequent itemset (all subsets of frequent itemset are frequent)
            # But we still need to check if X is in frequent_itemsets
            support_X = frequent_itemsets.get(X)
            if support_X is None:
                continue
            
            # Calculate confidence: support(X ∪ Y) / support(X)
            confidence = support / support_X
            if confidence >= min_confidence:
                rules.append((X, Y, support, confidence))
    
    return rules


def main():

    filename = 'T10I4D100K.dat'
    min_support = int(input("Enter minimum support count (e.g., 1000): "))
    min_confidence = float(input("Enter minimum confidence (0-1, e.g., 0.5): "))
    transactions = load_data(filename)
    print(f"Loaded {len(transactions)} transactions")
    
    # Find frequent itemsets
    print("\nFinding frequent itemsets...")
    frequent_itemsets = apriori(transactions, min_support)
    print(f"Found {len(frequent_itemsets)} frequent itemsets")
    # Display frequent itemsets
    print("\nFrequent Itemsets")
    sorted_itemsets = sorted(frequent_itemsets.items(), key=lambda x: (-x[1], sorted(list(x[0]))))
    for itemset, support in sorted_itemsets[:20]:
        itemset_str = sorted(list(itemset))
        print(f"  {itemset_str}: support = {support}")
    
    # Generate association rules
    print("\nGenerating association rules...")
    rules = generate_rules(frequent_itemsets, transactions, min_support, min_confidence)
    print(f"Found {len(rules)} association rules")
    
    # Display association rules
    print("\nAssociation Rules (first 20):")
    sorted_rules = sorted(rules, key=lambda x: (-x[3], -x[2]))  # Sort by confidence, then support
    for X, Y, support, confidence in sorted_rules[:20]:
        X_str = sorted(list(X))
        Y_str = sorted(list(Y))
        print(f"  {X_str} -> {Y_str}: support = {support}, confidence = {confidence:.4f}")
    
    # Save results to file
    output_file = 'results.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Minimum Support: {min_support}\n")
        f.write(f"Minimum Confidence: {min_confidence}\n\n")
        f.write(f"Total Frequent Itemsets: {len(frequent_itemsets)}\n")
        f.write(f"Total Association Rules: {len(rules)}\n\n")
        f.write("Frequent Itemsets:\n")
        for itemset, support in sorted_itemsets:
            itemset_str = sorted(list(itemset))
            f.write(f"  {itemset_str}: support = {support}\n")
        f.write("\nAssociation Rules:\n")
        for X, Y, support, confidence in sorted_rules:
            X_str = sorted(list(X))
            Y_str = sorted(list(Y))
            f.write(f"  {X_str} -> {Y_str}: support = {support}, confidence = {confidence:.4f}\n")
    
    print(f"\nResults saved to {output_file}")

if __name__ == '__main__':
    main()

