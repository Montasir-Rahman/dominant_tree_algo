import numpy as np
import os
from collections import Counter

def get_mining_recommendations(analysis_results):
    """
    Generates mining recommendations based on dataset characteristics.
    """
    avg_len = float(analysis_results["--- Transaction Length ---"]["Average Length"])
    dataset_type = analysis_results["--- Dataset Density ---"]["Determination"]

    recommendation = {}

    if dataset_type == "Dense":
        recommendation["Suggestion"] = "This is a DENSE dataset. Many items co-occur frequently."
        recommendation["Recommended Range"] = "20% - 40%"
        recommendation["Advice"] = "Start with a high support threshold to get a manageable number of rules. Lowering it may produce an overwhelming number of patterns."
    elif dataset_type == "Functionally Sparse":
        recommendation["Suggestion"] = "This is a FUNCTIONALLY SPARSE dataset (like 'accidents')."
        recommendation["Recommended Range"] = "40% - 60%"
        recommendation["Advice"] = "The combination of many transactions and items will cause a 'combinatorial explosion' at low support. Start high and lower the threshold in small steps (e.g., 5%), monitoring performance at each stage."
    elif avg_len > 20:
        recommendation["Suggestion"] = "This is a sparse dataset with LONG transactions."
        recommendation["Recommended Range"] = "15% - 30%"
        recommendation["Advice"] = "Longer patterns are computationally expensive. Start with a moderate threshold and lower it cautiously."
    else:
        recommendation["Suggestion"] = "This is a typical SPARSE dataset."
        recommendation["Recommended Range"] = "5% - 15%"
        recommendation["Advice"] = "This is a good starting range to find initial patterns. If no patterns are found, you can safely lower the threshold."

    return recommendation



def analyze_dataset(file_path):
    """
    Analyzes a .dat file to compute key metrics for association rule mining.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        return None

    try:
        with open(file_path, 'r') as f:
            records = [line.strip().split() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading or processing file: {e}")
        return None

    if not records:
        print("Error: The dataset is empty or could not be read properly.")
        return None

    num_transactions = len(records)
    all_items = [item for transaction in records for item in transaction]
    num_unique_items = len(set(all_items))
    transaction_lengths = [len(t) for t in records]

    total_item_instances = len(all_items)
    total_possible_instances = num_transactions * num_unique_items
    density = total_item_instances / total_possible_instances if total_possible_instances > 0 else 0

    # --- Advanced Dataset Type Classification ---
    if density > 0.05:
        if num_transactions > 100000 and num_unique_items > 300:
            dataset_type = "Functionally Sparse"
        else:
            dataset_type = "Dense"
    else:
        dataset_type = "Sparse"

    # --- Compile Results ---
    analysis_results = {
        "File Path": file_path,
        "--- General Metrics ---": {
            "Total Transactions": num_transactions,
            "Total Unique Items": num_unique_items,
        },
        "--- Transaction Length ---": {
            "Max Length": max(transaction_lengths) if transaction_lengths else 0,
            "Min Length": min(transaction_lengths) if transaction_lengths else 0,
            "Average Length": f"{np.mean(transaction_lengths):.2f}" if transaction_lengths else "0.00",
        },
        "--- Dataset Density ---": {
            "Density": f"{density:.6f}",
            "Determination": dataset_type,
            "Explanation": "Density is the proportion of non-empty cells in the transaction-item matrix. Classification considers scale and structure."
        },
        "--- Item Frequency (Top 5) ---": {
            item: count for item, count in Counter(all_items).most_common(5)
        },
        "--- Item Frequency (Bottom 5) ---": {
            item: count for item, count in Counter(all_items).most_common()[:-6:-1]
        }
    }

    analysis_results["--- Mining Recommendations ---"] = get_mining_recommendations(analysis_results)

    return analysis_results


def print_analysis(results):
    """
    Prints the analysis results in a readable format.
    """
    if not results:
        return

    print("\n" + "=" * 60)
    print("        Dataset Pre-Mining Analysis and Recommendation")
    print("=" * 60 + "\n")

    print(f"Analysis for: {results['File Path']}\n")

    for category, metrics in results.items():
        if isinstance(metrics, dict):
            print(f"--- {category.strip('---')} ---")
            for key, value in metrics.items():
                print(f"  {key:<25}: {value}")
            print()


if __name__ == '__main__':
    # Set your file here
    dat_filename = "webdocs.dat"  # <--- CHANGE THIS TO TEST OTHER FILES
    analysis = analyze_dataset(dat_filename)
    print_analysis(analysis)
