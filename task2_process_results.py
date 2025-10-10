import os
import re
import csv
import matplotlib.pyplot as plt

def extract_metrics(filepath):
    """
    Extracts IPC and MPKI metrics from a Champsim log file using regular expressions.
    """
    if not os.path.exists(filepath):
        print(f"Error: Log file not found at {filepath}")
        return None

    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

    metrics = {}

    # Regex 1: IPC
    # Looks for: "CPU 0 cumulative IPC: 1.02412 instructions:"
    ipc_match = re.search(r"CPU 0 cumulative IPC: ([\d\.]+)\s+instructions:", content, re.MULTILINE)
    metrics['IPC'] = float(ipc_match.group(1)) if ipc_match else 0.0

    # Regex 2: L1D MPKI
    # Looks for: "L1D TOTAL      ACCESS:..." and captures the final MPKI value
    l1d_match = re.search(r"L1D TOTAL\s+ACCESS:.*MPKI: ([\d\.]+)", content)
    metrics['L1D_MPKI'] = float(l1d_match.group(1)) if l1d_match else 0.0

    # Regex 3: L2C MPKI
    l2c_match = re.search(r"L2C TOTAL\s+ACCESS:.*MPKI: ([\d\.]+)", content)
    metrics['L2C_MPKI'] = float(l2c_match.group(1)) if l2c_match else 0.0

    # Regex 4: LLC MPKI (as L3 is typically named LLC)
    llc_match = re.search(r"LLC TOTAL\s+ACCESS:.*MPKI: ([\d\.]+)", content)
    metrics['LLC_MPKI'] = float(llc_match.group(1)) if llc_match else 0.0
    
    return metrics

def process_champsim_results():
    """
    Reads log files, calculates speedup, and generates the final CSV report and plot.
    """
    TRACES = ["trace1", "trace2", "trace3", "trace4"]
    EXCLUSIVE_DIR = "results/Task2/exclusive"
    NON_INCLUSIVE_DIR = "results/Task2/non-inclusive"
    RESULTS_DIR = "results/Task2"
    
    report_data = []
    speedup_values = {}

    for trace in TRACES:
        exclusive_path = os.path.join(EXCLUSIVE_DIR, f"{trace}.txt")
        non_inclusive_path = os.path.join(NON_INCLUSIVE_DIR, f"{trace}.txt")
        
        print(f"Processing results for {trace}...")

        # Extract metrics for both configurations
        excl_metrics = extract_metrics(exclusive_path)
        non_incl_metrics = extract_metrics(non_inclusive_path)

        if excl_metrics is None or non_incl_metrics is None:
            print(f"Skipping {trace} due to missing data.")
            continue

        # Calculate Speedup (IPC_exclusive / IPC_non_inclusive)
        speedup = 0.0
        if non_incl_metrics['IPC'] > 0:
            speedup = excl_metrics['IPC'] / non_incl_metrics['IPC']
        else:
            print(f"Warning: Non-inclusive IPC is 0 for {trace}. Speedup set to N/A.")

        speedup_values[trace] = speedup

        # Append Exclusive data to report
        report_data.append({
            'Trace': trace,
            'Configuration': 'Exclusive',
            'IPC': f"{excl_metrics['IPC']:.4f}",
            'L1D_MPKI': f"{excl_metrics['L1D_MPKI']:.4f}",
            'L2C_MPKI': f"{excl_metrics['L2C_MPKI']:.4f}",
            'LLC_MPKI': f"{excl_metrics['LLC_MPKI']:.4f}",
            'Speedup_over_Non_Inclusive': f"{speedup:.4f}" if speedup > 0 else 'N/A'
        })
        
        # Append Non-Inclusive data to report (Speedup N/A for baseline)
        report_data.append({
            'Trace': trace,
            'Configuration': 'Non-Inclusive',
            'IPC': f"{non_incl_metrics['IPC']:.4f}",
            'L1D_MPKI': f"{non_incl_metrics['L1D_MPKI']:.4f}",
            'L2C_MPKI': f"{non_incl_metrics['L2C_MPKI']:.4f}",
            'LLC_MPKI': f"{non_incl_metrics['LLC_MPKI']:.4f}",
            'Speedup_over_Non_Inclusive': 'N/A'
        })
    
    # 1. Generate CSV Report
    csv_filepath = os.path.join(RESULTS_DIR, "performance_report.csv")
    if report_data:
        fieldnames = ['Trace', 'Configuration', 'IPC', 'L1D_MPKI', 'L2C_MPKI', 'LLC_MPKI', 'Speedup_over_Non_Inclusive']
        with open(csv_filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(report_data)
        print(f"\nCSV Report successfully generated at {csv_filepath}")
    
    # 2. Generate Speedup Plot
    if speedup_values:
        plot_filepath = os.path.join(RESULTS_DIR, "speedup_plot.png")
        traces = list(speedup_values.keys())
        speeds = list(speedup_values.values())

        try:
            plt.figure(figsize=(9, 6))
            plt.ylim(0, 1.6)
            
            # Bar plot for speedup
            bars = plt.bar(traces, speeds, color=['#3a5a40', '#588157', '#a3b18a', '#dad7cd'])
            
            # Baseline line (Speedup = 1.0)
            plt.axhline(1.0, color='#e63946', linestyle='--', linewidth=1.5, label='Non-Inclusive Baseline (Speedup = 1.0)')
            
            # Adding labels and titles
            plt.xlabel('Trace Name', fontsize=12)
            plt.ylabel(r'Speedup ($\frac{IPC_{Exclusive}}{IPC_{Non-Inclusive}}$)', fontsize=12)
            plt.title('Exclusive vs. Non-Inclusive Cache Speedup Across Traces', fontsize=14)
            plt.grid(axis='y', linestyle=':', alpha=0.6)
            plt.legend(loc='upper right')
            
            # Annotate bars with their value
            for bar in bars:
                yval = bar.get_height()
                # Adjust label position slightly based on the dynamic y_limit
                plt.text(bar.get_x() + bar.get_width()/2, yval , round(yval, 3), ha='center', va='bottom', fontsize=10)
            
            plt.tight_layout()
            plt.savefig(plot_filepath)
            print(f"Speedup Plot successfully generated at {plot_filepath}")
            
        except ImportError:
            print("Warning: Matplotlib not found. Cannot generate plot. Please install it using 'pip install matplotlib'.")
        except Exception as e:
            print(f"An error occurred during plotting: {e}")

if __name__ == "__main__":
    process_champsim_results()
