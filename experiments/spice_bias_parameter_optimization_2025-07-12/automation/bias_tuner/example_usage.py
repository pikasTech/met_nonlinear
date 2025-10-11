#!/usr/bin/env python
"""Example usage of the bias tuner."""

from pathlib import Path
from bias_tuner import BiasTuner, CompensationStrategy


def main():
    """Example bias tuning workflow."""
    # Set up project path
    project_path = Path("/path/to/your/project/WNET5q1h2u6l3")
    
    # Create tuner with same-phase compensation strategy
    tuner = BiasTuner(
        project_path,
        strategy=CompensationStrategy.SAME_PHASE,
        python_env="conda run -n tf26 python",
        dry_run=False  # Set to True for testing without running cli.py
    )
    
    # Step 1: Run baseline measurement
    print("Running baseline measurement...")
    baseline = tuner.run_baseline_measurement()
    print(f"Baseline errors measured for {len(baseline['statistics'])} layers")
    
    # Step 2: Sequential tuning of layers 1-3
    print("\nTuning layers sequentially...")
    results = tuner.tune_sequential(
        layer_order=[1, 2, 3],  # Dense layers only
        scale_factors={1: 1.0, 2: 1.0, 3: 1.0}  # 100% compensation
    )
    
    print(f"Tuned {len(results)} layers")
    for result in results:
        layer_idx = result["layer_idx"]
        stats = result["statistics"][layer_idx]
        print(f"  Layer {layer_idx}: error reduced to {stats['abs_mean']:.6f}")
    
    # Step 3: Generate report
    print("\nGenerating report...")
    report_path = tuner.generate_report()
    print(f"Report saved to: {report_path}")
    
    # Step 4: Print summary
    if tuner.tuning_history:
        baseline_stats = tuner.tuning_history[0]["statistics"]
        final_stats = tuner.tuning_history[-1]["statistics"]
        
        print("\nCompensation Summary:")
        for layer_idx in [1, 2, 3]:
            if layer_idx in baseline_stats and layer_idx in final_stats:
                before = baseline_stats[layer_idx]["abs_mean"]
                after = final_stats[layer_idx]["abs_mean"]
                improvement = (before - after) / before * 100 if before > 0 else 0
                
                print(f"  Layer {layer_idx}: {before:.6f} -> {after:.6f} "
                      f"({improvement:.1f}% improvement)")


if __name__ == "__main__":
    main()