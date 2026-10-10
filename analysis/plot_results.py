import pandas as pd
import matplotlib.pyplot as plt
import os
import json

def generate_plots():
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    csv_file = os.path.join(results_dir, 'metrics.csv')

    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found.")
        return

    df = pd.read_csv(csv_file)
    
    # Save a JSON summary
    json_summary = df.to_dict(orient='records')
    with open(os.path.join(results_dir, 'summary.json'), 'w') as f:
        json.dump(json_summary, f, indent=4)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Latency Plot
    axes[0].bar(df['Scenario'], df['Latency(ms)'], color=['blue', 'orange', 'green'])
    axes[0].set_title('Average Latency (ms)')
    axes[0].set_ylabel('Latency (ms)')

    # Loss Plot
    axes[1].bar(df['Scenario'], df['Loss(%)'], color=['blue', 'orange', 'green'])
    axes[1].set_title('Packet Loss (%)')
    axes[1].set_ylabel('Loss (%)')

    # Throughput Plot
    axes[2].bar(df['Scenario'], df['Throughput(Mbps)'], color=['blue', 'orange', 'green'])
    axes[2].set_title('Throughput (Mbps)')
    axes[2].set_ylabel('Throughput (Mbps)')

    plt.tight_layout()
    plot_path = os.path.join(results_dir, 'performance_metrics.png')
    plt.savefig(plot_path)
    print(f"Plots saved to {plot_path}")

if __name__ == '__main__':
    generate_plots()
