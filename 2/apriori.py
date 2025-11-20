def load_data(filename):
    data = []
    with open(filename, 'r') as f:
        for line in f:
            data.append(line.strip().split())
    return data


def get_frequent_1_itemsets(data, min_support):
    item_counts = {}
    
    # Count occurrences of each item
    for row in data:
        for item in row:
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
    
    # Combine itemsets that share first k-2 items
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


def count_support(data, candidates):
    support_counts = {}
    
    for candidate in candidates:
        count = 0
        for row in data:
            # Check if transaction contains the candidate
            if candidate.issubset(row):
                count += 1
        support_counts[candidate] = count
    
    return support_counts


def apriori(data, min_support):
    all_frequent = {}
    
    # Find frequent 1-itemsets
    k = 1
    frequent_k = get_frequent_1_itemsets(data, min_support)
    all_frequent.update(frequent_k)
    # Iteratively find frequent k-itemsets for k >= 2
    k = 2
    while frequent_k:
        # Generate candidates
        candidates = generate_candidates(frequent_k, k)
        candidates = prune_candidates(candidates, frequent_k, k)
        support_counts = count_support(data, candidates)
        # Filter frequent itemsets
        frequent_k = {
            itemset: count 
            for itemset, count in support_counts.items() 
            if count >= min_support
        }
        all_frequent.update(frequent_k)
        k += 1
    return all_frequent


def generate_rules(frequent_itemsets, min_confidence):
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
            selected_items = []

            for index in range(len(itemset_list)):
                is_selected = (i >> index) & 1
                if is_selected:
                    selected_items.append(itemset_list[index])

            X = frozenset(selected_items)
                        
            Y = itemset - X
            
            # X must be a frequent itemset (all subsets of frequent itemset are frequent)
            # Double check
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
    data = load_data(filename)
    print(f"Loaded {len(data)} transactions")
    
    # Find frequent itemsets
    print("\nFinding frequent itemsets...")
    frequent_itemsets = apriori(data, min_support)
    print(f"Found {len(frequent_itemsets)} frequent itemsets")
    # Display frequent itemsets
    print("\nFrequent itemsets:")
    sorted_itemsets = sorted(frequent_itemsets.items(), key=lambda x: (-x[1], sorted(list(x[0]))))
    for itemset, support in sorted_itemsets[:20]:
        itemset_str = sorted(list(itemset))
        print(f"  {itemset_str}: support = {support}")
    
    # Generate rules
    print("\nGenerating rules...")
    rules = generate_rules(frequent_itemsets, data, min_support, min_confidence)
    print(f"Found {len(rules)} rules")
    
    # Display rules
    print("\nRules:")
    sorted_rules = sorted(rules, key=lambda x: (-x[3], -x[2]))  # Sort by confidence, then support
    for X, Y, support, confidence in sorted_rules[:20]:
        X_str = sorted(list(X))
        Y_str = sorted(list(Y))
        print(f"  {X_str} -> {Y_str}: support = {support}, confidence = {confidence:.4f}")
    
    # Save results
    output_file = 'results_' + str(min_support) + '_' + str(min_confidence) + '.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Frequent Itemsets: {len(frequent_itemsets)}\n")
        f.write(f"Rules: {len(rules)}\n\n")
        f.write("Frequent Itemsets:\n")
        for itemset, support in sorted_itemsets:
            itemset_str = sorted(list(itemset))
            f.write(f"  {itemset_str}: support = {support}\n")
        f.write("\nRules:\n")
        for X, Y, support, confidence in sorted_rules:
            X_str = sorted(list(X))
            Y_str = sorted(list(Y))
            f.write(f"  {X_str} -> {Y_str}: support = {support}, confidence = {confidence:.4f}\n")

if __name__ == '__main__':
    main()

