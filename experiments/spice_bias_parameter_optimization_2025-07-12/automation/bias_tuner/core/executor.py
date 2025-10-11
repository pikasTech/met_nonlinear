"""
Command execution module for bias tuner.
Handles subprocess calls to cli.py and monitors execution.
"""

import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import threading
import queue
import shutil

from ..utils import get_logger, read_json
from ..config.defaults import EXECUTION_CONFIG, MOCK_CONFIG
from ..utils.path_finder import find_cli
from ..exceptions import (
    CommandNotFoundError,
    MockResourcesError,
    InferenceError,
    InferenceTimeoutError,
    AnalysisError,
    ExecutionError
)

# Module-specific logger
logger = get_logger('bias_tuner.core.executor')


# Global mock mode control
_MOCK_MODE = False
_MOCK_RESOURCES_PATH = None


def set_mock_mode(enabled: bool, resources_path: Optional[Path] = None):
    """
    Enable or disable mock mode globally.
    
    Args:
        enabled: Whether to enable mock mode
        resources_path: Path to test resources (required if enabled)
    """
    global _MOCK_MODE, _MOCK_RESOURCES_PATH
    _MOCK_MODE = enabled
    _MOCK_RESOURCES_PATH = Path(resources_path) if resources_path else None
    
    if enabled and not _MOCK_RESOURCES_PATH:
        raise ValueError("Mock resources path required when enabling mock mode")
    
    logger.info(f"Mock mode {'enabled' if enabled else 'disabled'}")


def is_mock_mode() -> bool:
    """Check if mock mode is enabled."""
    return _MOCK_MODE


class CommandExecutor:
    """Executes cli.py commands and monitors results."""
    
    def __init__(self, cli_path: Optional[Path] = None, python_env: str = "python"):
        """
        Initialize command executor.
        
        Args:
            cli_path: Path to cli.py (auto-detected if None)
            python_env: Python command or conda env command
        """
        if not _MOCK_MODE:
            if cli_path is None:
                # Auto-detect cli.py in parent directories
                self.cli_path = self._find_cli()
            else:
                self.cli_path = Path(cli_path)
        else:
            self.cli_path = Path("mock_cli.py")  # Dummy path for mock mode
            
        self.python_env = python_env
        self.execution_history: List[Dict[str, Any]] = []
        self._mock_state = "baseline"  # Track mock state for testing
        
    def _find_cli(self) -> Path:
        """Find cli.py in parent directories."""
        cli_path = find_cli()
        if cli_path is None:
            raise CommandNotFoundError(
                "Could not find cli.py. Please specify path explicitly."
            )
        logger.info(f"Found cli.py at: {cli_path}")
        return cli_path
    
    def run_inference(
        self, 
        project_name: str, 
        timeout: Optional[int] = None,
        monitor_progress: bool = True
    ) -> Tuple[bool, str]:
        """
        Run inference for a project.
        
        Args:
            project_name: Project name
            timeout: Timeout in seconds (uses config default if None)
            monitor_progress: Whether to monitor progress
            
        Returns:
            Tuple of (success, output_message)
        """
        if timeout is None:
            timeout = EXECUTION_CONFIG["inference_timeout"]
        if _MOCK_MODE:
            return self._mock_inference(project_name)
        
        cmd = [self.python_env, str(self.cli_path), "-i", "-f", project_name]
        
        logger.info(f"Running inference: {' '.join(cmd)}")
        
        start_time = time.time()
        
        try:
            if monitor_progress:
                success, output = self._run_with_monitoring(cmd, timeout)
            else:
                success, output = self._run_simple(cmd, timeout)
            
            elapsed = time.time() - start_time
            
            # Log execution
            self._log_execution({
                "command": "inference",
                "project": project_name,
                "success": success,
                "elapsed_seconds": elapsed,
                "output_preview": output[:500] if output else ""
            })
            
            if success:
                logger.info(f"Inference completed in {elapsed:.1f}s")
            else:
                logger.error(f"Inference failed: {output}")
            
            return success, output
            
        except Exception as e:
            logger.error(f"Inference execution error: {e}")
            return False, str(e)
    
    def run_analysis(
        self, 
        project_name: str,
        timeout: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Run error analysis for a project.
        
        Args:
            project_name: Project name
            timeout: Timeout in seconds (uses config default if None)
            
        Returns:
            Tuple of (success, output_message)
        """
        if timeout is None:
            timeout = EXECUTION_CONFIG["analysis_timeout"]
        if _MOCK_MODE:
            return self._mock_analysis(project_name)
        
        cmd = [self.python_env, str(self.cli_path), "-a", project_name]
        
        logger.info(f"Running analysis: {' '.join(cmd)}")
        
        start_time = time.time()
        
        try:
            success, output = self._run_simple(cmd, timeout)
            
            elapsed = time.time() - start_time
            
            # Log execution
            self._log_execution({
                "command": "analysis",
                "project": project_name,
                "success": success,
                "elapsed_seconds": elapsed,
                "output_preview": output[:500] if output else ""
            })
            
            if success:
                logger.info(f"Analysis completed in {elapsed:.1f}s")
            else:
                logger.error(f"Analysis failed: {output}")
            
            return success, output
            
        except Exception as e:
            logger.error(f"Analysis execution error: {e}")
            return False, str(e)
    
    def _run_simple(self, cmd: List[str], timeout: int) -> Tuple[bool, str]:
        """
        Run command without progress monitoring.
        
        Args:
            cmd: Command to run
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (success, output)
        """
        try:
            # In mock mode, use current directory
            cwd = Path.cwd() if _MOCK_MODE else self.cli_path.parent
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd
            )
            
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            
            return success, output
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout}s")
            return False, f"Timeout after {timeout}s"
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return False, str(e)
    
    def _run_with_monitoring(
        self, 
        cmd: List[str], 
        timeout: int
    ) -> Tuple[bool, str]:
        """
        Run command with real-time output monitoring.
        
        Args:
            cmd: Command to run
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (success, output)
        """
        output_lines = []
        output_queue = queue.Queue()
        
        def read_output(pipe, queue):
            """Read output from pipe and put in queue."""
            for line in iter(pipe.readline, ''):
                if line:
                    queue.put(line.strip())
            pipe.close()
        
        try:
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=self.cli_path.parent
            )
            
            # Start output reader thread
            reader_thread = threading.Thread(
                target=read_output,
                args=(process.stdout, output_queue)
            )
            reader_thread.daemon = True
            reader_thread.start()
            
            # Monitor output with timeout
            start_time = time.time()
            last_output_time = start_time
            
            while True:
                # Check timeout
                if time.time() - start_time > timeout:
                    process.terminate()
                    logger.error(f"Process timed out after {timeout}s")
                    return False, f"Timeout after {timeout}s"
                
                # Check if process finished
                if process.poll() is not None:
                    break
                
                # Read output
                try:
                    line = output_queue.get(timeout=0.1)
                    output_lines.append(line)
                    last_output_time = time.time()
                    
                    # Log progress indicators
                    if "Layer" in line and "output" in line:
                        logger.debug(f"Progress: {line}")
                    elif "Error" in line or "error" in line:
                        logger.warning(f"Process output: {line}")
                        
                except queue.Empty:
                    # Check for stall
                    stall_timeout = EXECUTION_CONFIG["stall_detection_timeout"]
                    if time.time() - last_output_time > stall_timeout:
                        logger.warning(f"No output for {stall_timeout}s, process may be stalled")
                
                time.sleep(EXECUTION_CONFIG["monitoring_interval"])
            
            # Get remaining output
            reader_thread.join(timeout=EXECUTION_CONFIG["thread_join_timeout"])
            while not output_queue.empty():
                try:
                    output_lines.append(output_queue.get_nowait())
                except queue.Empty:
                    break
            
            success = process.returncode == 0
            output = "\n".join(output_lines)
            
            return success, output
            
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            return False, str(e)
    
    def verify_inference_outputs(self, project_path: Path) -> Dict[str, bool]:
        """
        Verify that inference outputs exist.
        
        Args:
            project_path: Path to project
            
        Returns:
            Dict of output_type -> exists
        """
        inference_dir = project_path / "data" / "inference"
        
        checks = {
            "error_analysis": (inference_dir / "error_analysis.json").exists(),
            "nn_layers": (inference_dir / "nn_layers").exists(),
            "spice_layers": (inference_dir / "spice_layers").exists(),
            "numpy_layers": (inference_dir / "numpy_layers").exists(),
        }
        
        logger.debug(f"Output verification: {checks}")
        return checks
    
    def wait_for_file(
        self, 
        filepath: Path, 
        timeout: Optional[int] = None,
        check_interval: Optional[float] = None
    ) -> bool:
        """
        Wait for a file to be created.
        
        Args:
            filepath: Path to wait for
            timeout: Maximum wait time (uses config default if None)
            check_interval: Check interval in seconds (uses config default if None)
            
        Returns:
            True if file appeared within timeout
        """
        if timeout is None:
            timeout = EXECUTION_CONFIG["file_wait_timeout"]
        if check_interval is None:
            check_interval = EXECUTION_CONFIG["file_check_interval"]
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if filepath.exists():
                logger.debug(f"File appeared: {filepath}")
                return True
            
            time.sleep(check_interval)
        
        logger.warning(f"File did not appear within {timeout}s: {filepath}")
        return False
    
    def _log_execution(self, record: Dict[str, Any]) -> None:
        """Log execution record."""
        record["timestamp"] = time.time()
        self.execution_history.append(record)
        
        # Keep only last N executions
        max_history = EXECUTION_CONFIG["max_history_size"]
        if len(self.execution_history) > max_history:
            self.execution_history = self.execution_history[-max_history:]
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.execution_history:
            return {"total_executions": 0}
        
        stats = {
            "total_executions": len(self.execution_history),
            "successful": sum(1 for r in self.execution_history if r.get("success")),
            "failed": sum(1 for r in self.execution_history if not r.get("success")),
            "average_time": sum(r.get("elapsed_seconds", 0) for r in self.execution_history) / len(self.execution_history)
        }
        
        return stats
    
    def _mock_inference(self, project_name: str) -> Tuple[bool, str]:
        """Mock inference execution for testing."""
        logger.info(f"[MOCK] Running inference for {project_name}")
        
        # Simulate some delay
        time.sleep(MOCK_CONFIG["inference_delay"])
        
        # Log execution
        self._log_execution({
            "command": "inference",
            "project": project_name,
            "success": True,
            "elapsed_seconds": 0.1,
            "output_preview": "[MOCK] Inference completed"
        })
        
        output = f"[MOCK] Inference output for {project_name}\n"
        output += "NN inference: 5 layers processed\n"
        output += "SPICE inference: 5 layers processed\n"
        output += "NumPy inference: 5 layers processed\n"
        
        return True, output
    
    def _mock_analysis(self, project_name: str) -> Tuple[bool, str]:
        """Mock analysis execution for testing."""
        logger.info(f"[MOCK] Running analysis for {project_name}")
        
        # Determine which error analysis file to copy based on mock state
        if not _MOCK_RESOURCES_PATH:
            return False, "Mock resources path not set"
        
        # Map mock states to error analysis files
        state_to_file = MOCK_CONFIG["mock_states"]
        
        error_file = state_to_file.get(self._mock_state, "error_analysis_baseline.json")
        source_file = _MOCK_RESOURCES_PATH / "error_analysis_samples" / error_file
        
        if not source_file.exists():
            return False, f"Mock error analysis file not found: {source_file}"
        
        # Find project directory
        # For mock mode, look for the project in common locations
        project_path = None
        cwd = Path.cwd()
        logger.info(f"[MOCK] Current working directory: {cwd}")
        
        # Check various possible locations
        possible_paths = [
            cwd / project_name,  # Direct subdirectory
            cwd / "test_output" / project_name,  # Test output directory
            cwd.parent / project_name,  # Parent directory
            cwd  # Current directory itself might be the project
        ]
        
        for candidate in possible_paths:
            logger.info(f"[MOCK] Checking candidate path: {candidate}")
            if candidate.exists() and (candidate / "config.json").exists():
                project_path = candidate
                logger.info(f"[MOCK] Found project at: {project_path}")
                break
        
        if project_path is None:
            # Fallback: assume CWD is project path
            project_path = cwd
            logger.warning(f"[MOCK] Could not find project directory, using CWD: {project_path}")
        
        # Create inference directory
        inference_dir = project_path / "data" / "inference"
        inference_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy the appropriate error analysis file
        dest_file = inference_dir / "error_analysis.json"
        shutil.copy(source_file, dest_file)
        
        # Simulate delay
        time.sleep(MOCK_CONFIG["analysis_delay"])
        
        # Log execution
        self._log_execution({
            "command": "analysis",
            "project": project_name,
            "success": True,
            "elapsed_seconds": 0.05,
            "output_preview": f"[MOCK] Analysis completed with {error_file}"
        })
        
        output = f"[MOCK] Analysis output for {project_name}\n"
        output += f"Using mock state: {self._mock_state}\n"
        output += f"Copied {error_file} to {dest_file}\n"
        output += "Bias error analysis completed\n"
        
        return True, output
    
    def set_mock_state(self, state: str):
        """Set mock state for testing progression."""
        from ..core.mock_state import MockState
        
        # Validate state
        try:
            mock_state = MockState.from_string(state)
        except ValueError as e:
            raise MockResourcesError(str(e))
        
        self._mock_state = state
        logger.debug(f"Set mock state to: {state}")