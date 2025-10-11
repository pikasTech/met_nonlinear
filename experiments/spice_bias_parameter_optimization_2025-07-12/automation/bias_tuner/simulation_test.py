#!/usr/bin/env python
"""
Comprehensive end-to-end simulation test for bias tuner.
Tests all major features with extensive logging for debugging.
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add bias_tuner parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import bias tuner modules
from bias_tuner import BiasTuner, CompensationStrategy
from bias_tuner.core import set_mock_mode, is_mock_mode
from bias_tuner.utils import setup_logger, get_logger


def setup_test_environment(test_dir):
    """Set up test environment with mock project."""
    logger = get_logger('simulation_test.setup')
    logger.info("="*80)
    logger.info("Setting up test environment")
    logger.info("="*80)
    
    # Create test project directory
    project_path = test_dir / "test_project_simulation"
    project_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created project directory: {project_path}")
    
    # Copy baseline config from test resources
    test_resources = Path(__file__).parent / "test_resources"
    config_source = test_resources / "config_samples" / "config_baseline.json"
    config_dest = project_path / "config.json"
    
    logger.debug(f"Copying config from: {config_source}")
    logger.debug(f"Copying config to: {config_dest}")
    
    import shutil
    shutil.copy(config_source, config_dest)
    logger.info("Copied baseline configuration")
    
    # Enable mock mode
    logger.info("Enabling mock mode for simulation")
    set_mock_mode(True, test_resources)
    logger.info(f"Mock mode enabled: {is_mock_mode()}")
    logger.info(f"Mock resources path: {test_resources}")
    
    return project_path


def test_baseline_measurement(tuner):
    """Test baseline measurement phase."""
    logger = get_logger('simulation_test.baseline')
    logger.info("\n" + "="*80)
    logger.info("PHASE 1: Baseline Measurement")
    logger.info("="*80)
    
    logger.info("Starting baseline measurement...")
    start_time = time.time()
    
    try:
        baseline_result = tuner.run_baseline_measurement()
        elapsed = time.time() - start_time
        
        logger.info(f"Baseline measurement completed in {elapsed:.2f}s")
        logger.debug(f"Result type: {baseline_result['type']}")
        logger.debug(f"Timestamp: {baseline_result['timestamp']}")
        
        # Log statistics for each layer
        logger.info("\nBaseline bias errors by layer:")
        for layer_idx, stats in baseline_result['statistics'].items():
            logger.info(f"  Layer {layer_idx}:")
            logger.info(f"    - Mean error: {stats['mean']:.6f}")
            logger.info(f"    - Abs mean: {stats['abs_mean']:.6f}")
            logger.info(f"    - Std dev: {stats['std']:.6f}")
            logger.info(f"    - Range: [{stats['min']:.6f}, {stats['max']:.6f}]")
            logger.info(f"    - Channels: {stats['channel_count']}")
        
        # Log raw bias error matrix
        logger.debug("\nRaw bias error matrix:")
        for idx, errors in enumerate(baseline_result['bias_errors']):
            logger.debug(f"  Layer {idx}: {errors}")
        
        return baseline_result
        
    except Exception as e:
        logger.error(f"Baseline measurement failed: {e}", exc_info=True)
        raise


def test_single_layer_compensation(tuner, layer_idx=1):
    """Test single layer compensation."""
    logger = get_logger('simulation_test.single_layer')
    logger.info("\n" + "="*80)
    logger.info(f"PHASE 2: Single Layer Compensation (Layer {layer_idx})")
    logger.info("="*80)
    
    # Update mock state for layer 1 compensation
    logger.debug("Updating mock state to 'layer1'")
    tuner.executor.set_mock_state("layer1")
    
    logger.info(f"Applying compensation to layer {layer_idx}")
    logger.debug(f"Compensation strategy: {tuner.compensator.strategy.value}")
    logger.debug(f"Scale factor: 1.0")
    
    start_time = time.time()
    
    try:
        result = tuner.tune_single_layer(layer_idx, scale_factor=1.0)
        elapsed = time.time() - start_time
        
        logger.info(f"Layer {layer_idx} compensation completed in {elapsed:.2f}s")
        
        # Log compensation applied
        compensation = tuner.current_compensation.get(layer_idx, [])
        logger.info(f"\nCompensation values applied: {compensation}")
        
        # Log new statistics
        new_stats = result['statistics'][layer_idx]
        logger.info(f"\nLayer {layer_idx} after compensation:")
        logger.info(f"  - Mean error: {new_stats['mean']:.6f}")
        logger.info(f"  - Abs mean: {new_stats['abs_mean']:.6f}")
        logger.info(f"  - Improvement: {((0.005578 - new_stats['abs_mean']) / 0.005578 * 100):.1f}%")
        
        # Log config changes
        logger.debug("\nConfiguration changes:")
        config = tuner.config_manager.get_bias_compensation_config()
        logger.debug(f"  - Enabled: {config['enabled']}")
        logger.debug(f"  - Adjustments: {config['layer_bias_adjustments']}")
        
        return result
        
    except Exception as e:
        logger.error(f"Single layer compensation failed: {e}", exc_info=True)
        raise


def test_sequential_compensation(tuner):
    """Test sequential multi-layer compensation."""
    logger = get_logger('simulation_test.sequential')
    logger.info("\n" + "="*80)
    logger.info("PHASE 3: Sequential Multi-Layer Compensation")
    logger.info("="*80)
    
    # Define layer order and mock states
    layer_order = [2, 3]
    mock_states = ["layer12", "layer123"]
    
    logger.info(f"Compensating layers in order: {layer_order}")
    
    all_results = []
    
    for layer_idx, mock_state in zip(layer_order, mock_states):
        logger.info(f"\n--- Compensating Layer {layer_idx} ---")
        
        # Update mock state
        logger.debug(f"Setting mock state to: {mock_state}")
        tuner.executor.set_mock_state(mock_state)
        
        start_time = time.time()
        
        try:
            result = tuner.tune_single_layer(layer_idx, scale_factor=1.0)
            elapsed = time.time() - start_time
            
            logger.info(f"Layer {layer_idx} completed in {elapsed:.2f}s")
            
            # Log compensation state
            logger.debug(f"Current compensation state: {tuner.current_compensation}")
            
            # Log layer statistics
            stats = result['statistics'][layer_idx]
            logger.info(f"Layer {layer_idx} error: {stats['abs_mean']:.6f}")
            
            all_results.append(result)
            
        except Exception as e:
            logger.error(f"Failed to compensate layer {layer_idx}: {e}", exc_info=True)
            raise
    
    # Summary of all layers
    logger.info("\n--- Sequential Compensation Summary ---")
    for layer_idx in [1, 2, 3]:
        if layer_idx in tuner.current_compensation:
            comp = tuner.current_compensation[layer_idx]
            logger.info(f"Layer {layer_idx}: {len(comp)} compensation values applied")
    
    return all_results


def test_optimization(tuner):
    """Test layer optimization feature."""
    logger = get_logger('simulation_test.optimization')
    logger.info("\n" + "="*80)
    logger.info("PHASE 4: Layer Optimization Test")
    logger.info("="*80)
    
    # Reset to baseline for optimization test
    logger.info("Resetting tuner to baseline state")
    tuner.reset()
    tuner.executor.set_mock_state("baseline")
    
    # Run baseline again
    logger.debug("Running fresh baseline measurement")
    tuner.run_baseline_measurement()
    
    # Optimize layer 1
    layer_idx = 1
    target_error = 0.001
    
    logger.info(f"Optimizing layer {layer_idx} to target error: {target_error}")
    logger.info("Note: In mock mode, optimization completes after first iteration")
    
    tuner.executor.set_mock_state("layer1")
    
    try:
        opt_result = tuner.optimize_layer(
            layer_idx=layer_idx,
            target_error=target_error,
            max_iterations=3
        )
        
        logger.info(f"\nOptimization completed:")
        logger.info(f"  - Success: {opt_result['success']}")
        logger.info(f"  - Final error: {opt_result['final_error']:.6f}")
        logger.info(f"  - Iterations: {len(opt_result['iterations'])}")
        
        for iteration in opt_result['iterations']:
            logger.debug(f"  Iteration {iteration['iteration']}: "
                        f"scale={iteration['scale_factor']:.2f}, "
                        f"error={iteration['error_after']:.6f}")
        
        return opt_result
        
    except Exception as e:
        logger.error(f"Optimization failed: {e}", exc_info=True)
        raise


def test_report_generation(tuner, output_dir):
    """Test report generation."""
    logger = get_logger('simulation_test.report')
    logger.info("\n" + "="*80)
    logger.info("PHASE 5: Report Generation")
    logger.info("="*80)
    
    logger.info("Generating comprehensive report...")
    
    try:
        report_path = tuner.generate_report(output_dir / "simulation_report.json")
        
        logger.info(f"Report generated: {report_path}")
        
        # Load and log report summary
        with open(report_path) as f:
            report = json.load(f)
        
        logger.info("\nReport Summary:")
        logger.info(f"  - Project: {report['project']}")
        logger.info(f"  - Timestamp: {report['timestamp']}")
        logger.info(f"  - Strategy: {report['strategy']}")
        logger.info(f"  - History entries: {len(report['tuning_history'])}")
        
        if 'summary' in report:
            summary = report['summary']
            logger.info(f"\n  - Total iterations: {summary.get('total_iterations', 0)}")
            logger.info(f"  - Layers tuned: {summary.get('layers_tuned', [])}")
            
            if 'overall_improvement' in summary:
                logger.info(f"  - Overall improvement: {summary['overall_improvement']:.1f}%")
            
            if 'layer_improvements' in summary:
                logger.info("\n  Layer improvements:")
                for layer_idx, imp in summary['layer_improvements'].items():
                    logger.info(f"    Layer {layer_idx}: "
                               f"{imp['before']:.6f} -> {imp['after']:.6f} "
                               f"({imp['improvement_percent']:.1f}%)")
        
        return report_path
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        raise


def test_different_strategies(project_path):
    """Test different compensation strategies."""
    logger = get_logger('simulation_test.strategies')
    logger.info("\n" + "="*80)
    logger.info("PHASE 6: Testing Different Compensation Strategies")
    logger.info("="*80)
    
    strategies = [
        CompensationStrategy.SAME_PHASE,
        CompensationStrategy.SCALED,
        CompensationStrategy.CONSERVATIVE,
        CompensationStrategy.ADAPTIVE
    ]
    
    results = {}
    
    for strategy in strategies:
        logger.info(f"\n--- Testing {strategy.value} strategy ---")
        
        # Create new tuner with this strategy
        tuner = BiasTuner(
            project_path,
            strategy=strategy,
            dry_run=False
        )
        
        try:
            # Run baseline
            tuner.run_baseline_measurement()
            
            # Compensate layer 1
            tuner.executor.set_mock_state("layer1")
            result = tuner.tune_single_layer(1)
            
            # Get statistics
            stats = result['statistics'][1]
            improvement = (0.005578 - stats['abs_mean']) / 0.005578 * 100
            
            logger.info(f"  Result: {stats['abs_mean']:.6f} ({improvement:.1f}% improvement)")
            
            results[strategy.value] = {
                'final_error': stats['abs_mean'],
                'improvement': improvement
            }
            
        except Exception as e:
            logger.error(f"  Failed: {e}")
            results[strategy.value] = {'error': str(e)}
    
    # Summary
    logger.info("\n--- Strategy Comparison Summary ---")
    for strategy, result in results.items():
        if 'error' in result:
            logger.info(f"  {strategy}: FAILED - {result['error']}")
        else:
            logger.info(f"  {strategy}: {result['final_error']:.6f} "
                       f"({result['improvement']:.1f}% improvement)")
    
    return results


def run_full_simulation():
    """Run complete end-to-end simulation test."""
    # Set up logging
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_dir = Path(__file__).parent / "logs" / f"simulation_{timestamp}"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure main logger with file output
    main_logger = setup_logger(
        name="bias_tuner",
        log_dir=log_dir,
        console_level='DEBUG',
        file_level='DEBUG'
    )
    
    logger = get_logger('simulation_test')
    
    logger.info("="*80)
    logger.info("BIAS TUNER END-TO-END SIMULATION TEST")
    logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Log directory: {log_dir}")
    logger.info("="*80)
    
    start_time = time.time()
    
    try:
        # Phase 0: Setup
        test_dir = Path(__file__).parent / "test_output"
        test_dir.mkdir(exist_ok=True)
        project_path = setup_test_environment(test_dir)
        
        # Create main tuner instance
        logger.info("\nCreating BiasTuner instance...")
        tuner = BiasTuner(
            project_path,
            strategy=CompensationStrategy.SAME_PHASE,
            dry_run=False  # Using mock mode instead
        )
        logger.info("BiasTuner created successfully")
        
        # Phase 1: Baseline measurement
        baseline = test_baseline_measurement(tuner)
        
        # Phase 2: Single layer compensation
        layer1_result = test_single_layer_compensation(tuner, layer_idx=1)
        
        # Phase 3: Sequential compensation
        sequential_results = test_sequential_compensation(tuner)
        
        # Phase 4: Optimization test
        opt_result = test_optimization(tuner)
        
        # Phase 5: Report generation
        report_path = test_report_generation(tuner, log_dir)
        
        # Phase 6: Different strategies
        strategy_results = test_different_strategies(project_path)
        
        # Final summary
        elapsed_total = time.time() - start_time
        
        logger.info("\n" + "="*80)
        logger.info("SIMULATION COMPLETED SUCCESSFULLY")
        logger.info("="*80)
        logger.info(f"Total time: {elapsed_total:.2f}s")
        logger.info(f"Log files in: {log_dir}")
        logger.info(f"Report saved to: {report_path}")
        logger.info("="*80)
        
        return True
        
    except Exception as e:
        logger.error("\n" + "="*80)
        logger.error("SIMULATION FAILED")
        logger.error("="*80)
        logger.error(f"Error: {e}", exc_info=True)
        logger.error("="*80)
        return False
        
    finally:
        # Cleanup: disable mock mode
        set_mock_mode(False)
        logger.info("\nMock mode disabled")


if __name__ == "__main__":
    success = run_full_simulation()
    sys.exit(0 if success else 1)