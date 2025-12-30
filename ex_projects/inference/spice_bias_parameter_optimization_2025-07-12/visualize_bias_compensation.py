#!/usr/bin/env python3
"""
SPICE Bias Compensation Results Visualization

This script creates visualizations comparing bias errors before and after compensation
for each layer and channel in the WaveNet5 model.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import seaborn as sns

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_results(json_path):
    """Load experimental results from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_layer_comparison_plot(layer_name, baseline_data, compensated_data, 
                               layer_info, ax, improvement_pct=None):
    """Create a comparison plot for one layer showing before/after compensation."""
    
    channels = baseline_data['channels']
    compensated_channels = compensated_data['channels']
    
    n_channels = len(channels)
    x = np.arange(n_channels)
    width = 0.35
    
    # Create bar plots
    bars1 = ax.bar(x - width/2, channels, width, label='Before Compensation', 
                   alpha=0.8, color='lightcoral', edgecolor='darkred')
    bars2 = ax.bar(x + width/2, compensated_channels, width, label='After Compensation',
                   alpha=0.8, color='lightblue', edgecolor='darkblue')
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{height:.6f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, rotation=45)
    
    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f'{height:.6f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, rotation=45)
    
    # Customize the plot
    ax.set_xlabel('Channel Index')
    ax.set_ylabel('Bias Error')
    
    # Create title with improvement percentage if available
    title = f'{layer_name}\n({layer_info["type"]}, {layer_info["channels"]} channels)'
    if improvement_pct is not None:
        title += f'\nImprovement: {improvement_pct:.1f}%'
    ax.set_title(title, fontweight='bold')
    
    ax.set_xticks(x)
    ax.set_xticklabels([f'Ch{i}' for i in range(n_channels)])
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add mean lines
    baseline_mean = np.mean(channels)
    compensated_mean = np.mean(compensated_channels)
    
    ax.axhline(y=baseline_mean, color='red', linestyle='--', alpha=0.7, 
               label=f'Baseline Mean: {baseline_mean:.6f}')
    ax.axhline(y=compensated_mean, color='blue', linestyle='--', alpha=0.7,
               label=f'Compensated Mean: {compensated_mean:.6f}')
    
    # Add text box with statistics
    stats_text = f'Baseline Mean: {baseline_mean:.6f}\n'
    stats_text += f'Compensated Mean: {compensated_mean:.6f}\n'
    stats_text += f'Absolute Improvement: {abs(baseline_mean - compensated_mean):.6f}'
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

def create_boxplot_comparison(layer_name, baseline_data, compensated_data, 
                            layer_info, ax, improvement_pct=None):
    """Create boxplot comparison for one layer (alternative visualization)."""
    
    channels = baseline_data['channels']
    compensated_channels = compensated_data['channels']
    
    n_channels = len(channels)
    
    # Prepare data for boxplot
    data_to_plot = []
    labels = []
    colors = []
    
    for i in range(n_channels):
        # For each channel, create before/after pair
        data_to_plot.append([channels[i], compensated_channels[i]])
        labels.append(f'Ch{i}')
        colors.extend(['lightcoral', 'lightblue'])
    
    # Create boxplots
    positions = []
    for i in range(n_channels):
        positions.extend([i*3, i*3+1])
    
    # Flatten data for boxplot
    flattened_data = []
    for i, channel_data in enumerate(data_to_plot):
        flattened_data.extend(channel_data)
    
    # Create individual boxplots
    box_data = []
    box_positions = []
    for i in range(n_channels):
        box_data.append([channels[i]])  # Before
        box_data.append([compensated_channels[i]])  # After
        box_positions.extend([i*3, i*3+1])
    
    bp = ax.boxplot(box_data, positions=box_positions, widths=0.6, patch_artist=True)
    
    # Color the boxes
    for i, patch in enumerate(bp['boxes']):
        if i % 2 == 0:  # Before compensation
            patch.set_facecolor('lightcoral')
            patch.set_alpha(0.8)
        else:  # After compensation
            patch.set_facecolor('lightblue')
            patch.set_alpha(0.8)
    
    # Customize the plot
    ax.set_xlabel('Channels')
    ax.set_ylabel('Bias Error')
    
    title = f'{layer_name} - Boxplot Comparison\n({layer_info["type"]}, {layer_info["channels"]} channels)'
    if improvement_pct is not None:
        title += f'\nImprovement: {improvement_pct:.1f}%'
    ax.set_title(title, fontweight='bold')
    
    # Set x-axis labels
    xtick_positions = []
    xtick_labels = []
    for i in range(n_channels):
        xtick_positions.append(i*3 + 0.5)
        xtick_labels.append(f'Ch{i}')
    
    ax.set_xticks(xtick_positions)
    ax.set_xticklabels(xtick_labels)
    
    # Add legend
    before_patch = mpatches.Patch(color='lightcoral', alpha=0.8, label='Before Compensation')
    after_patch = mpatches.Patch(color='lightblue', alpha=0.8, label='After Compensation')
    ax.legend(handles=[before_patch, after_patch])
    
    ax.grid(True, alpha=0.3)

def create_summary_statistics_plot(results, ax):
    """Create a summary plot showing overall improvement statistics."""
    
    effectiveness = results['compensation_effectiveness']
    
    layers = []
    improvements = []
    baseline_means = []
    compensated_means = []
    
    for layer_key, data in effectiveness.items():
        layer_name = layer_key.replace('_', ' ').title()
        layers.append(layer_name)
        improvements.append(data['improvement_percentage'])
        baseline_means.append(abs(data['baseline_mean']))
        compensated_means.append(abs(data['compensated_mean']))
    
    x = np.arange(len(layers))
    width = 0.35
    
    # Create improvement percentage bars
    colors = ['green' if imp > 0 else 'red' for imp in improvements]
    bars = ax.bar(x, improvements, color=colors, alpha=0.7, edgecolor='black')
    
    # Add value labels
    for bar, imp in zip(bars, improvements):
        height = bar.get_height()
        ax.annotate(f'{imp:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3 if height >= 0 else -15),
                    textcoords="offset points",
                    ha='center', va='bottom' if height >= 0 else 'top',
                    fontweight='bold')
    
    ax.set_xlabel('Layers')
    ax.set_ylabel('Improvement Percentage (%)')
    ax.set_title('Compensation Effectiveness Summary\n(Positive = Improvement, Negative = Degradation)', 
                 fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(layers, rotation=45, ha='right')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)

def main():
    """Main function to create all visualizations."""
    
    # File paths
    script_dir = Path(__file__).parent
    json_path = script_dir / 'results' / 'bias_compensation_results.json'
    output_dir = script_dir / 'results'
    output_dir.mkdir(exist_ok=True)
    
    # Load results
    print("Loading experimental results...")
    results = load_results(json_path)
    
    baseline = results['baseline_errors']
    compensated = results['compensated_errors'] 
    architecture = results['layer_architecture']
    effectiveness = results['compensation_effectiveness']
    
    # Define layers to visualize (skip SVF layer as it's not compensated)
    layers_to_plot = [
        ('layer_1_dense1', 'Dense Layer 1'),
        ('layer_2_dense2', 'Dense Layer 2'), 
        ('layer_3_dense3', 'Dense Layer 3'),
        ('layer_4_output', 'Output Layer')
    ]
    
    # Create figure with subplots - Bar plot version
    print("Creating bar plot visualizations...")
    fig1, axes1 = plt.subplots(2, 3, figsize=(18, 12))
    fig1.suptitle('SPICE Bias Compensation Results - Bar Plot Comparison', fontsize=16, fontweight='bold')
    
    axes1_flat = axes1.flatten()
    
    # Plot each layer
    for i, (layer_key, layer_display_name) in enumerate(layers_to_plot):
        if i < len(axes1_flat):
            # Get improvement percentage
            improvement_key = layer_key
            improvement_pct = effectiveness.get(improvement_key, {}).get('improvement_percentage')
            
            # Get layer info
            layer_num = layer_key.split('_')[1]
            layer_info_key = f'layer_{layer_num}'
            layer_info = architecture.get(layer_info_key, {})
            
            create_layer_comparison_plot(
                layer_display_name,
                baseline[layer_key],
                compensated[layer_key],
                layer_info,
                axes1_flat[i],
                improvement_pct
            )
    
    # Summary plot
    if len(layers_to_plot) < len(axes1_flat):
        create_summary_statistics_plot(results, axes1_flat[-2])
        axes1_flat[-1].axis('off')  # Hide last subplot
    
    plt.tight_layout()
    
    # Save bar plot
    bar_plot_path = output_dir / 'bias_compensation_barplot.png'
    fig1.savefig(bar_plot_path, dpi=300, bbox_inches='tight')
    print(f"Bar plot saved to: {bar_plot_path}")
    
    # Create figure with subplots - Boxplot version  
    print("Creating boxplot visualizations...")
    fig2, axes2 = plt.subplots(2, 3, figsize=(18, 12))
    fig2.suptitle('SPICE Bias Compensation Results - Boxplot Comparison', fontsize=16, fontweight='bold')
    
    axes2_flat = axes2.flatten()
    
    # Plot each layer with boxplots
    for i, (layer_key, layer_display_name) in enumerate(layers_to_plot):
        if i < len(axes2_flat):
            # Get improvement percentage
            improvement_key = layer_key
            improvement_pct = effectiveness.get(improvement_key, {}).get('improvement_percentage')
            
            # Get layer info
            layer_num = layer_key.split('_')[1]
            layer_info_key = f'layer_{layer_num}'
            layer_info = architecture.get(layer_info_key, {})
            
            create_boxplot_comparison(
                layer_display_name,
                baseline[layer_key],
                compensated[layer_key],
                layer_info,
                axes2_flat[i],
                improvement_pct
            )
    
    # Summary plot
    if len(layers_to_plot) < len(axes2_flat):
        create_summary_statistics_plot(results, axes2_flat[-2])
        axes2_flat[-1].axis('off')  # Hide last subplot
    
    plt.tight_layout()
    
    # Save boxplot
    boxplot_path = output_dir / 'bias_compensation_boxplot.png'
    fig2.savefig(boxplot_path, dpi=300, bbox_inches='tight')
    print(f"Boxplot saved to: {boxplot_path}")
    
    # Create detailed statistics table
    print("Creating detailed statistics...")
    create_statistics_table(results, output_dir)
    
    # Show plots
    plt.show()

def create_statistics_table(results, output_dir):
    """Create a detailed statistics table and save as text file."""
    
    baseline = results['baseline_errors']
    compensated = results['compensated_errors']
    effectiveness = results['compensation_effectiveness']
    
    stats_content = "="*80 + "\n"
    stats_content += "SPICE BIAS COMPENSATION EXPERIMENT - DETAILED STATISTICS\n"
    stats_content += "="*80 + "\n\n"
    
    stats_content += f"Experiment: {results['experiment_info']['name']}\n"
    stats_content += f"Project: {results['experiment_info']['project']}\n"
    stats_content += f"Model: {results['experiment_info']['model_type']}\n"
    stats_content += f"Duration: {results['experiment_info']['duration_hours']} hours\n"
    stats_content += f"Method: {results['experiment_info']['compensation_method']}\n\n"
    
    layers_to_analyze = [
        ('layer_1_dense1', 'Dense Layer 1'),
        ('layer_2_dense2', 'Dense Layer 2'),
        ('layer_3_dense3', 'Dense Layer 3'),
        ('layer_4_output', 'Output Layer')
    ]
    
    for layer_key, layer_name in layers_to_analyze:
        stats_content += f"{layer_name}\n" + "-"*50 + "\n"
        
        baseline_data = baseline[layer_key]
        compensated_data = compensated[layer_key]
        
        stats_content += f"Channels: {len(baseline_data['channels'])}\n"
        stats_content += f"Baseline Mean: {baseline_data['mean']:.6f}\n"
        stats_content += f"Compensated Mean: {compensated_data['mean']:.6f}\n"
        
        if layer_key in effectiveness:
            improvement = effectiveness[layer_key]['improvement_percentage']
            stats_content += f"Improvement: {improvement:.1f}%\n"
            stats_content += f"Status: {effectiveness[layer_key]['status']}\n"
        
        stats_content += "\nChannel-by-channel comparison:\n"
        for i, (before, after) in enumerate(zip(baseline_data['channels'], compensated_data['channels'])):
            change = after - before
            change_pct = (change / abs(before) * 100) if before != 0 else float('inf')
            stats_content += f"  Channel {i}: {before:.6f} → {after:.6f} (Δ: {change:+.6f}, {change_pct:+.1f}%)\n"
        
        stats_content += "\n"
    
    # Key findings
    stats_content += "KEY FINDINGS\n" + "="*50 + "\n"
    for key, value in results['key_findings'].items():
        stats_content += f"• {key.replace('_', ' ').title()}: {value}\n"
    
    # Save statistics
    stats_path = output_dir / 'detailed_statistics.txt'
    with open(stats_path, 'w', encoding='utf-8') as f:
        f.write(stats_content)
    
    print(f"Detailed statistics saved to: {stats_path}")

if __name__ == "__main__":
    main()