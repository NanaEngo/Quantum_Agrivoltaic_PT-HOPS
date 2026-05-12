"""
Resume Capability Module for Quantum Agrivoltaic PT-HOPS Pipeline

Provides checkpoint management, state tracking, and recovery from OOM/failures.
Enables step-by-step result saving and resumption from last successful checkpoint.
"""

import os
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class ExecutionCheckpoint:
    """Manages execution state and checkpoints for pipeline recovery."""
    
    def __init__(self, checkpoint_dir: str = "reproducibility/checkpoints"):
        """
        Initialize checkpoint manager.
        
        Parameters
        ----------
        checkpoint_dir : str
            Directory to store checkpoint files
        """
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)
        self.state_file = os.path.join(checkpoint_dir, "execution_state.json")
        self.state = self._load_state()
        logger.info(f"Checkpoint manager initialized at {checkpoint_dir}")
    
    def _load_state(self) -> Dict[str, Any]:
        """Load execution state from disk."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                logger.info(f"Loaded execution state from {self.state_file}")
                return state
            except Exception as e:
                logger.warning(f"Failed to load state: {e}. Starting fresh.")
                return self._init_state()
        return self._init_state()
    
    def _init_state(self) -> Dict[str, Any]:
        """Initialize fresh execution state."""
        return {
            "start_time": datetime.now().isoformat(),
            "steps_completed": [],
            "steps_failed": [],
            "intermediate_results": {},
            "config_hash": None,
            "last_checkpoint": None,
        }
    
    def _save_state(self) -> None:
        """Save execution state to disk."""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2, default=str)
        logger.debug(f"Saved execution state to {self.state_file}")
    
    def mark_step_complete(self, step_name: str, result_path: Optional[str] = None) -> None:
        """
        Mark a step as completed.
        
        Parameters
        ----------
        step_name : str
            Name of the completed step
        result_path : str, optional
            Path to the result file
        """
        if step_name not in self.state["steps_completed"]:
            self.state["steps_completed"].append(step_name)
            if result_path:
                self.state["intermediate_results"][step_name] = result_path
            self.state["last_checkpoint"] = datetime.now().isoformat()
            self._save_state()
            logger.info(f"✅ Step '{step_name}' marked as complete")
    
    def mark_step_failed(self, step_name: str, error: str) -> None:
        """
        Mark a step as failed.
        
        Parameters
        ----------
        step_name : str
            Name of the failed step
        error : str
            Error message
        """
        if step_name not in self.state["steps_failed"]:
            self.state["steps_failed"].append(step_name)
        self._save_state()
        logger.error(f"❌ Step '{step_name}' failed: {error}")
    
    def is_step_complete(self, step_name: str) -> bool:
        """Check if a step has been completed."""
        return step_name in self.state["steps_completed"]
    
    def get_result_path(self, step_name: str) -> Optional[str]:
        """Get the result path for a completed step."""
        return self.state["intermediate_results"].get(step_name)
    
    def set_config_hash(self, config_dict: Dict[str, Any]) -> str:
        """
        Set and return the configuration hash.
        
        Parameters
        ----------
        config_dict : dict
            Configuration dictionary
            
        Returns
        -------
        str
            SHA-256 hash of the configuration
        """
        config_str = json.dumps(config_dict, sort_keys=True, default=str)
        config_hash = hashlib.sha256(config_str.encode()).hexdigest()[:12]
        self.state["config_hash"] = config_hash
        self._save_state()
        return config_hash
    
    def get_status_report(self) -> str:
        """Get a human-readable status report."""
        report = "\n" + "=" * 70 + "\n"
        report += "EXECUTION STATUS REPORT\n"
        report += "=" * 70 + "\n"
        report += f"Start Time: {self.state['start_time']}\n"
        report += f"Last Checkpoint: {self.state['last_checkpoint']}\n"
        report += f"Config Hash: {self.state['config_hash']}\n\n"
        
        report += f"Completed Steps ({len(self.state['steps_completed'])}):\n"
        for step in self.state["steps_completed"]:
            result_path = self.state["intermediate_results"].get(step, "N/A")
            report += f"  ✅ {step}\n"
            if result_path != "N/A":
                report += f"     → {result_path}\n"
        
        if self.state["steps_failed"]:
            report += f"\nFailed Steps ({len(self.state['steps_failed'])}):\n"
            for step in self.state["steps_failed"]:
                report += f"  ❌ {step}\n"
        
        report += "=" * 70 + "\n"
        return report


class StepByStepSaver:
    """Saves results incrementally to enable recovery from failures."""
    
    def __init__(self, results_dir: str = "reproducibility/results"):
        """
        Initialize step-by-step saver.
        
        Parameters
        ----------
        results_dir : str
            Directory to store results
        """
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        logger.info(f"Step-by-step saver initialized at {results_dir}")
    
    def save_convergence_audit(self, audit_data: Dict[str, Any], config_hash: str) -> str:
        """
        Save convergence audit results.
        
        Parameters
        ----------
        audit_data : dict
            Audit data from convergence_audit
        config_hash : str
            Configuration hash
            
        Returns
        -------
        str
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(
            self.results_dir, 
            f"convergence_audit_{config_hash}_{timestamp}.csv"
        )
        
        # Extract MAE values
        maes = audit_data.get('audit_maes', {})
        df_data = {
            'hierarchy_depth': list(maes.keys()),
            'mean_absolute_error': list(maes.values()),
        }
        df = pd.DataFrame(df_data)
        df.to_csv(filepath, index=False, float_format='%.10e')
        
        logger.info(f"Convergence audit saved to {filepath}")
        return filepath
    
    def save_fmo_dynamics_intermediate(
        self,
        label: str,
        time_points: np.ndarray,
        populations: np.ndarray,
        coherences: np.ndarray,
        config_hash: str,
        metrics: Optional[Dict[str, np.ndarray]] = None,
    ) -> str:
        """
        Save intermediate FMO dynamics results (filtered or broadband).
        
        Parameters
        ----------
        label : str
            'filtered' or 'broadband'
        time_points : np.ndarray
            Time axis
        populations : np.ndarray
            Population data
        coherences : np.ndarray
            Coherence data
        config_hash : str
            Configuration hash
        metrics : dict, optional
            Additional metrics (QFI, entropy, IPR)
            
        Returns
        -------
        str
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(
            self.results_dir,
            f"fmo_dynamics_{label}_{config_hash}_{timestamp}.csv"
        )
        
        # Build DataFrame
        data_dict = {"time_fs": time_points}
        
        # Add populations for each site
        n_sites = populations.shape[1] if len(populations.shape) > 1 else 1
        if n_sites > 1:
            for i in range(n_sites):
                data_dict[f"population_site_{i + 1}"] = populations[:, i]
        else:
            data_dict["populations"] = populations
        
        data_dict["coherences"] = coherences
        
        # Add metrics if provided
        if metrics:
            for metric_name, metric_values in metrics.items():
                if isinstance(metric_values, np.ndarray):
                    if len(metric_values) == len(time_points):
                        data_dict[metric_name] = metric_values
                    else:
                        # Pad or truncate
                        n = len(time_points)
                        if len(metric_values) >= n:
                            data_dict[metric_name] = metric_values[:n]
                        else:
                            padded = np.full(n, np.nan)
                            padded[:len(metric_values)] = metric_values
                            data_dict[metric_name] = padded
        
        df = pd.DataFrame(data_dict)
        df.to_csv(filepath, index=False, float_format='%.10e')
        
        logger.info(f"FMO {label} dynamics saved to {filepath}")
        return filepath
    
    def save_temperature_sweep_progress(
        self,
        temperatures: np.ndarray,
        eta_values: np.ndarray,
        eta_errors: np.ndarray,
        config_hash: str,
    ) -> str:
        """
        Save temperature sweep progress (can be called incrementally).
        
        Parameters
        ----------
        temperatures : np.ndarray
            Temperature points
        eta_values : np.ndarray
            Enhancement values
        eta_errors : np.ndarray
            Error bars
        config_hash : str
            Configuration hash
            
        Returns
        -------
        str
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(
            self.results_dir,
            f"temperature_sweep_{config_hash}_{timestamp}.csv"
        )
        
        df = pd.DataFrame({
            'temperature_k': temperatures,
            'eta': eta_values,
            'eta_error': eta_errors,
        })
        df.to_csv(filepath, index=False, float_format='%.10e')
        
        logger.info(f"Temperature sweep progress saved to {filepath}")
        return filepath
    
    def save_disorder_sampling_progress(
        self,
        disorder_samples: np.ndarray,
        config_hash: str,
    ) -> str:
        """
        Save disorder sampling progress (can be called incrementally).
        
        Parameters
        ----------
        disorder_samples : np.ndarray
            Disorder samples collected so far
        config_hash : str
            Configuration hash
            
        Returns
        -------
        str
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(
            self.results_dir,
            f"disorder_samples_{config_hash}_{timestamp}.csv"
        )
        
        df = pd.DataFrame({
            'sample_index': np.arange(len(disorder_samples)),
            'eta': disorder_samples,
        })
        df.to_csv(filepath, index=False, float_format='%.10e')
        
        logger.info(f"Disorder sampling progress saved to {filepath}")
        return filepath


class ResumableParallelExecutor:
    """Manages resumable parallel execution with checkpoint recovery."""
    
    def __init__(self, checkpoint_dir: str = "reproducibility/checkpoints"):
        """
        Initialize resumable executor.
        
        Parameters
        ----------
        checkpoint_dir : str
            Directory for checkpoints
        """
        self.checkpoint = ExecutionCheckpoint(checkpoint_dir)
        self.completed_tasks = set()
        self._load_completed_tasks()
    
    def _load_completed_tasks(self) -> None:
        """Load list of completed tasks from checkpoint."""
        tasks_file = os.path.join(self.checkpoint.checkpoint_dir, "completed_tasks.json")
        if os.path.exists(tasks_file):
            try:
                with open(tasks_file, 'r') as f:
                    self.completed_tasks = set(json.load(f))
                logger.info(f"Loaded {len(self.completed_tasks)} completed tasks")
            except Exception as e:
                logger.warning(f"Failed to load completed tasks: {e}")
    
    def _save_completed_tasks(self) -> None:
        """Save list of completed tasks to checkpoint."""
        tasks_file = os.path.join(self.checkpoint.checkpoint_dir, "completed_tasks.json")
        with open(tasks_file, 'w') as f:
            json.dump(list(self.completed_tasks), f)
    
    def mark_task_complete(self, task_id: str) -> None:
        """
        Mark a task as completed.
        
        Parameters
        ----------
        task_id : str
            Unique task identifier
        """
        self.completed_tasks.add(task_id)
        self._save_completed_tasks()
        logger.debug(f"Task '{task_id}' marked as complete")
    
    def is_task_complete(self, task_id: str) -> bool:
        """Check if a task has been completed."""
        return task_id in self.completed_tasks
    
    def get_pending_tasks(self, all_tasks: List[str]) -> List[str]:
        """
        Get list of tasks that still need to be executed.
        
        Parameters
        ----------
        all_tasks : list of str
            All task IDs
            
        Returns
        -------
        list of str
            Tasks that haven't been completed yet
        """
        pending = [t for t in all_tasks if not self.is_task_complete(t)]
        logger.info(f"Pending tasks: {len(pending)}/{len(all_tasks)}")
        return pending
    
    def get_recovery_info(self) -> Dict[str, Any]:
        """Get information for recovery from failure."""
        return {
            "completed_tasks": len(self.completed_tasks),
            "last_checkpoint": self.checkpoint.state.get("last_checkpoint"),
            "config_hash": self.checkpoint.state.get("config_hash"),
        }


def create_resume_checkpoint(
    checkpoint_dir: str = "reproducibility/checkpoints",
) -> Tuple[ExecutionCheckpoint, StepByStepSaver, ResumableParallelExecutor]:
    """
    Create all checkpoint management objects.
    
    Parameters
    ----------
    checkpoint_dir : str
        Directory for checkpoints
        
    Returns
    -------
    tuple
        (ExecutionCheckpoint, StepByStepSaver, ResumableParallelExecutor)
    """
    checkpoint = ExecutionCheckpoint(checkpoint_dir)
    saver = StepByStepSaver()
    executor = ResumableParallelExecutor(checkpoint_dir)
    
    return checkpoint, saver, executor


def print_recovery_instructions(checkpoint: ExecutionCheckpoint) -> None:
    """
    Print recovery instructions if execution was interrupted.
    
    Parameters
    ----------
    checkpoint : ExecutionCheckpoint
        Checkpoint manager
    """
    if checkpoint.state["steps_completed"]:
        print("\n" + "=" * 70)
        print("RECOVERY INFORMATION")
        print("=" * 70)
        print(checkpoint.get_status_report())
        print("\nTo resume from the last checkpoint, run:")
        print("  mamba run -n MesoHOP-sim python -u reproducibility/main.py --resume")
        print("=" * 70 + "\n")
