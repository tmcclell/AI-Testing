"""
Test Reporter
============

Generates test reports and manages logging output.
Creates comprehensive reports of test execution results.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import csv

from .config_manager import Config
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent_orchestrator import TestResult


class TestReporter:
    """
    Generates comprehensive test reports and manages output.
    
    Creates both human-readable and machine-readable reports
    for test execution results.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.report_data = {}
        self.start_time = None
        self.end_time = None
        
    async def initialize(self):
        """Initialize the test reporter."""
        self.logger.info("Initializing test reporter...")
        self.start_time = datetime.now()
        
        # Initialize report data
        self.report_data = {
            'test_info': {
                'scenario': self.config.scenario,
                'start_time': self.start_time.isoformat(),
                'target_iterations': self.config.iteration_count,
                'target_controllers': self.config.target_controllers,
                'target_network': self.config.target_network,
                'dry_run': self.config.dry_run
            },
            'iterations': [],
            'errors': [],
            'summary': {}
        }
        
        self.logger.info("Test reporter initialized successfully")
    
    async def cleanup(self):
        """Clean up resources."""
        self.logger.info("Cleaning up test reporter...")
        self.end_time = datetime.now()
    
    def log_iteration_start(self, iteration: int):
        """Log the start of a test iteration."""
        iteration_data = {
            'iteration': iteration,
            'start_time': datetime.now().isoformat(),
            'actions': [],
            'status': 'in_progress'
        }
        
        self.report_data['iterations'].append(iteration_data)
        self.logger.info(f"Started iteration {iteration}")
    
    def log_action(self, iteration: int, action: str, result: str, duration: float = 0.0):
        """Log an action within a test iteration."""
        action_data = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'result': result,
            'duration_seconds': duration
        }
        
        # Find the current iteration
        for iter_data in self.report_data['iterations']:
            if iter_data['iteration'] == iteration:
                iter_data['actions'].append(action_data)
                break
        
        self.logger.debug(f"Iteration {iteration}: {action} -> {result}")
    
    def log_iteration_complete(self, iteration: int, success: bool, error_message: Optional[str] = None):
        """Log the completion of a test iteration."""
        end_time = datetime.now()
        
        # Find and update the iteration
        for iter_data in self.report_data['iterations']:
            if iter_data['iteration'] == iteration:
                iter_data['end_time'] = end_time.isoformat()
                iter_data['status'] = 'completed' if success else 'failed'
                iter_data['success'] = success
                
                if error_message:
                    iter_data['error_message'] = error_message
                
                # Calculate duration
                start_time = datetime.fromisoformat(iter_data['start_time'])
                iter_data['duration_seconds'] = (end_time - start_time).total_seconds()
                break
        
        status = "completed successfully" if success else f"failed: {error_message}"
        self.logger.info(f"Iteration {iteration} {status}")
    
    def log_error(self, error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None):
        """Log an error that occurred during testing."""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': error_message,
            'context': context or {}
        }
        
        self.report_data['errors'].append(error_data)
        self.logger.error(f"{error_type}: {error_message}")
    
    async def generate_report(self, test_result: "TestResult"):
        """
        Generate comprehensive test report.
        
        Args:
            test_result: Final test result
        """
        self.logger.info("Generating test report...")
        
        # Finalize report data
        self.end_time = datetime.now()
        
        self.report_data['summary'] = {
            'end_time': self.end_time.isoformat(),
            'total_duration_seconds': test_result.total_time_seconds,
            'success': test_result.success,
            'iterations_completed': test_result.iterations_completed,
            'iterations_requested': self.config.iteration_count,
            'summary_text': test_result.summary,
            'error_message': test_result.error_message
        }
        
        # Generate different report formats
        await self._generate_json_report()
        await self._generate_text_report()
        await self._generate_csv_report()
        
        # Set the log file path in the result
        test_result.log_file_path = str(self.config.output_dir / "test_report.txt")
        
        self.logger.info("Test report generation completed")
    
    async def _generate_json_report(self):
        """Generate JSON format report."""
        json_file = self.config.output_dir / "test_report.json"
        
        with open(json_file, 'w') as f:
            json.dump(self.report_data, f, indent=2)
        
        self.logger.info(f"JSON report saved: {json_file}")
    
    async def _generate_text_report(self):
        """Generate human-readable text report."""
        text_file = self.config.output_dir / "test_report.txt"
        
        report_lines = []
        
        # Header
        report_lines.extend([
            "=" * 60,
            "AI-Assisted UI Automation Test Report",
            "=" * 60,
            ""
        ])
        
        # Test Information
        test_info = self.report_data['test_info']
        summary = self.report_data['summary']
        
        report_lines.extend([
            "TEST INFORMATION:",
            f"  Scenario: {test_info['scenario']}",
            f"  Start Time: {test_info['start_time']}",
            f"  End Time: {summary['end_time']}",
            f"  Duration: {summary['total_duration_seconds']:.1f} seconds",
            f"  Target Controllers: {test_info['target_controllers']}",
            f"  Target Network: {test_info['target_network']}",
            f"  Dry Run: {test_info['dry_run']}",
            ""
        ])
        
        # Summary
        report_lines.extend([
            "SUMMARY:",
            f"  Result: {'SUCCESS' if summary['success'] else 'FAILED'}",
            f"  Iterations Completed: {summary['iterations_completed']}/{summary['iterations_requested']}",
            f"  Summary: {summary['summary_text']}",
        ])
        
        if summary.get('error_message'):
            report_lines.append(f"  Error: {summary['error_message']}")
        
        report_lines.append("")
        
        # Iterations Detail
        if self.report_data['iterations']:
            report_lines.extend([
                "ITERATION DETAILS:",
                "-" * 40
            ])
            
            for iteration in self.report_data['iterations']:
                status_symbol = "✓" if iteration.get('success', False) else "✗"
                duration = iteration.get('duration_seconds', 0)
                
                report_lines.extend([
                    f"Iteration {iteration['iteration']} {status_symbol}",
                    f"  Duration: {duration:.1f} seconds",
                    f"  Status: {iteration['status']}"
                ])
                
                if iteration.get('error_message'):
                    report_lines.append(f"  Error: {iteration['error_message']}")
                
                # Action summary
                actions = iteration.get('actions', [])
                if actions:
                    report_lines.append(f"  Actions: {len(actions)} performed")
                
                report_lines.append("")
        
        # Errors
        if self.report_data['errors']:
            report_lines.extend([
                "ERRORS:",
                "-" * 40
            ])
            
            for error in self.report_data['errors']:
                report_lines.extend([
                    f"Time: {error['timestamp']}",
                    f"Type: {error['type']}",
                    f"Message: {error['message']}",
                    ""
                ])
        
        # Footer
        report_lines.extend([
            "=" * 60,
            "End of Report",
            "=" * 60
        ])
        
        # Write report
        with open(text_file, 'w') as f:
            f.write('\n'.join(report_lines))
        
        self.logger.info(f"Text report saved: {text_file}")
    
    async def _generate_csv_report(self):
        """Generate CSV format report for data analysis."""
        csv_file = self.config.output_dir / "test_results.csv"
        
        rows = []
        
        # Add header
        rows.append([
            'Iteration', 'Status', 'Success', 'Duration_Seconds', 
            'Actions_Count', 'Error_Message', 'Start_Time', 'End_Time'
        ])
        
        # Add iteration data
        for iteration in self.report_data['iterations']:
            rows.append([
                iteration['iteration'],
                iteration['status'],
                iteration.get('success', False),
                iteration.get('duration_seconds', 0),
                len(iteration.get('actions', [])),
                iteration.get('error_message', ''),
                iteration['start_time'],
                iteration.get('end_time', '')
            ])
        
        # Write CSV
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        self.logger.info(f"CSV report saved: {csv_file}")
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current test statistics."""
        completed_iterations = len([
            i for i in self.report_data['iterations'] 
            if i['status'] == 'completed'
        ])
        
        successful_iterations = len([
            i for i in self.report_data['iterations'] 
            if i.get('success', False)
        ])
        
        return {
            'total_iterations': len(self.report_data['iterations']),
            'completed_iterations': completed_iterations,
            'successful_iterations': successful_iterations,
            'error_count': len(self.report_data['errors']),
            'success_rate': successful_iterations / max(completed_iterations, 1) * 100
        }
