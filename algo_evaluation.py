import time
import tracemalloc
import math

import numpy as np

from d_tree_sorted import find_frequent_patterns , generate_association_rules

def calculate_rule_metrics(rules, records):
    total_transactions = len(records)
    rule_metrics = []
    
    for antecedent, (consequent, confidence) in rules.items():
        antecedent_support = sum(1 for r in records if set(antecedent).issubset(set(r))) / total_transactions
        consequent_support = sum(1 for r in records if set(consequent).issubset(set(r))) / total_transactions
        rule_support = sum(1 for r in records if set(antecedent + consequent).issubset(set(r))) / total_transactions

        lift = confidence / consequent_support if consequent_support > 0 else 0
        leverage = rule_support - (antecedent_support * consequent_support)
        conviction = (1 - consequent_support) / (1 - confidence) if (1 - confidence) > 0 else float('inf')

        p_ac = rule_support
        p_a_not_c = antecedent_support - rule_support
        p_not_c = 1 - consequent_support

        j_measure = 0
        if confidence > 0 and consequent_support > 0:
            j_measure += p_ac * math.log2(confidence / consequent_support)
        if p_a_not_c > 0 and p_not_c > 0 and (1 - confidence) > 0:
            j_measure += p_a_not_c * math.log2((1 - confidence) / p_not_c)

        all_confidence = rule_support / max(antecedent_support, consequent_support)
        cosine_similarity = rule_support / math.sqrt(antecedent_support * consequent_support)

        rule_metrics.append((antecedent, consequent, rule_support, confidence, lift, leverage, conviction, j_measure, all_confidence, cosine_similarity))
    
    return rule_metrics

# Load dataset
try:
    with open('kosarak.dat', 'r') as f:
        records = [line.strip().split() for line in f]
except FileNotFoundError:
    print("Error: File 'mushroom.dat' not found.")
    exit()

min_confidence = 0.8
#support_thresholds = list(range(10, 0, -1))
support_thresholds = np.arange(1.0, 0.5, -0.1)
results = []

for support in support_thresholds:
    min_supp = max(int(len(records) * (support / 100)), 1)
    
    print(f"Processing with support threshold: {support}% (min_supp = {min_supp})")
    
    tracemalloc.start()
    start_time = time.perf_counter()

    patterns = find_frequent_patterns(records, min_supp)
    rules = generate_association_rules(patterns, min_confidence)

    exec_time = time.perf_counter() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()
    memory_usage = peak_memory / 1024  # Convert to KB
    tracemalloc.stop()
    tracemalloc.clear_traces()

    rule_metrics = calculate_rule_metrics(rules, records)
    
    avg_metrics = {
        "Avg Support": sum(rm[2] for rm in rule_metrics) / len(rule_metrics) if rule_metrics else 0,
        "Avg Confidence": sum(rm[3] for rm in rule_metrics) / len(rule_metrics) if rule_metrics else 0,
        "Avg Lift": sum(rm[4] for rm in rule_metrics) / len(rule_metrics) if rule_metrics else 0,
        "Avg Leverage": sum(rm[5] for rm in rule_metrics) / len(rule_metrics) if rule_metrics else 0,
        "Avg Conviction": sum(rm[6] for rm in rule_metrics) / len(rule_metrics) if rule_metrics else 0,
        "Avg J-Measure": sum(rm[7] for rm in rule_metrics) / len(rule_metrics) if rule_metrics else 0,
        "Avg All-Confidence": sum(rm[8] for rm in rule_metrics) / len(rule_metrics) if rule_metrics else 0,
        "Avg Cosine Similarity": sum(rm[9] for rm in rule_metrics) / len(rule_metrics) if rule_metrics else 0
    }
    
    results.append({
        "Support Threshold": support,
        "Execution Time (s)": exec_time,
        "Memory Usage (KB)": memory_usage,
        "Pattern Count": len(patterns),
        "Rule Count": len(rules),
        "Average Metrics": avg_metrics
    })

print("\n=== Comparison of ARM Performance ===")
for result in results:
    print(f"\nSupport Threshold: {result['Support Threshold']}%")
    print(f"  Execution Time: {result['Execution Time (s)']:.4f} seconds")
    print(f"  Memory Usage: {result['Memory Usage (KB)']:.2f} KB")
    print(f"  Pattern Count: {result['Pattern Count']}")
    print(f"  Rule Count: {result['Rule Count']}")
    for metric, value in result["Average Metrics"].items():
        print(f"  {metric}: {value:.4f}")
