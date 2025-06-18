#!/usr/bin/env python3
"""
Test runner script for GeoNode-GeoServer integration tests.

This script provides a command-line interface for running the test suite
with various options and configurations.
"""

import argparse
import sys
import os
import logging
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config, get_config_for_environment


def setup_logging(verbose: bool = False, log_file: Optional[str] = None) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=handlers
    )


def validate_environment() -> bool:
    """Validate that the environment is properly set up."""
    logger = logging.getLogger(__name__)
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    
    # Check required files
    required_files = [
        "requirements.txt",
        "notebooks/geonode_geoserver_tests_improved.ipynb",
        "config.py"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            logger.error(f"Required file not found: {file_path}")
            return False
    
    # Check if papermill is available
    try:
        import papermill
        logger.info(f"Papermill version: {papermill.__version__}")
    except ImportError:
        logger.error("Papermill is not installed. Run: pip install papermill")
        return False
    
    return True


def install_dependencies(upgrade: bool = False) -> bool:
    """Install required Python dependencies."""
    logger = logging.getLogger(__name__)
    
    try:
        cmd = ["pip", "install"]
        if upgrade:
            cmd.append("--upgrade")
        cmd.extend(["-r", "requirements.txt"])
        
        logger.info("Installing dependencies...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Dependencies installed successfully")
            return True
        else:
            logger.error(f"Failed to install dependencies: {result.stderr}")
            return False
    
    except Exception as e:
        logger.error(f"Error installing dependencies: {e}")
        return False


def run_notebook_tests(
    notebook_path: str,
    output_path: str,
    parameters: Dict[str, Any] = None,
    timeout: int = 1800
) -> bool:
    """Run notebook tests using papermill."""
    logger = logging.getLogger(__name__)
    
    try:
        import papermill as pm
        
        logger.info(f"Running notebook: {notebook_path}")
        logger.info(f"Output will be saved to: {output_path}")
        
        # Prepare parameters
        params = parameters or {}
        
        # Execute notebook
        pm.execute_notebook(
            input_path=notebook_path,
            output_path=output_path,
            parameters=params,
            log_output=True,
            progress_bar=True,
            request_save_on_cell_execute=True,
            autosave_cell_every=30,
            timeout=timeout
        )
        
        logger.info("Notebook execution completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Notebook execution failed: {e}")
        return False


def generate_report(output_notebook: str) -> Dict[str, Any]:
    """Generate a summary report from the output notebook."""
    logger = logging.getLogger(__name__)
    
    try:
        import nbformat
        
        # Read the output notebook
        with open(output_notebook, 'r') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Extract test results (simplified - in practice, you'd parse the actual results)
        report = {
            "execution_time": datetime.now().isoformat(),
            "notebook_path": output_notebook,
            "total_cells": len(nb.cells),
            "executed_cells": sum(1 for cell in nb.cells if cell.get('execution_count')),
            "status": "completed",
            "errors": []
        }
        
        # Check for errors in cells
        for i, cell in enumerate(nb.cells):
            if cell.cell_type == 'code' and cell.get('outputs'):
                for output in cell.outputs:
                    if output.get('output_type') == 'error':
                        report["errors"].append({
                            "cell": i,
                            "error": output.get('ename', 'Unknown error')
                        })
        
        if report["errors"]:
            report["status"] = "completed_with_errors"
        
        logger.info(f"Generated report: {len(report['errors'])} errors found")
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        return {"status": "report_generation_failed", "error": str(e)}


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="GeoNode-GeoServer Integration Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                          # Run with default settings
  python run_tests.py --verbose               # Run with verbose logging
  python run_tests.py --environment production # Run with production config
  python run_tests.py --install-deps          # Install dependencies first
  python run_tests.py --timeout 3600          # Set custom timeout
        """
    )
    
    parser.add_argument(
        "--environment", "-e",
        choices=["development", "production", "testing"],
        default="development",
        help="Environment configuration to use"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--log-file",
        help="Log file path (optional)"
    )
    
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install dependencies before running tests"
    )
    
    parser.add_argument(
        "--upgrade-deps",
        action="store_true",
        help="Upgrade dependencies before running tests"
    )
    
    parser.add_argument(
        "--notebook",
        default="notebooks/geonode_geoserver_tests_improved.ipynb",
        help="Path to the test notebook"
    )
    
    parser.add_argument(
        "--output-dir",
        default="./output",
        help="Output directory for test results"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=1800,
        help="Timeout for notebook execution (seconds)"
    )
    
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip environment validation"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose, args.log_file)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting GeoNode-GeoServer integration test runner")
    logger.info(f"Environment: {args.environment}")
    
    # Validate environment
    if not args.skip_validation and not validate_environment():
        logger.error("Environment validation failed")
        sys.exit(1)
    
    # Install dependencies if requested
    if args.install_deps or args.upgrade_deps:
        if not install_dependencies(args.upgrade_deps):
            logger.error("Failed to install dependencies")
            sys.exit(1)
    
    # Load configuration
    config = get_config_for_environment(args.environment)
    logger.info(f"Configuration loaded for environment: {args.environment}")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_notebook = output_dir / f"test_results_{timestamp}.ipynb"
    
    # Prepare parameters for notebook execution
    parameters = {
        "GEONODE_URL": config.GEONODE_URL,
        "GEOSERVER_URL": config.GEOSERVER_URL,
        "USERNAME": config.USERNAME,
        "PASSWORD": config.PASSWORD,
        "SAMPLE_SHAPEFILE_PATH": config.SAMPLE_SHAPEFILE_PATH,
        "SAMPLE_RASTER_PATH": config.SAMPLE_RASTER_PATH,
        "DEFAULT_TIMEOUT": config.DEFAULT_TIMEOUT,
        "MAX_RETRY_ATTEMPTS": config.MAX_RETRY_ATTEMPTS,
        "ENABLE_CLEANUP": config.ENABLE_CLEANUP,
        "VERBOSE_LOGGING": config.VERBOSE_LOGGING
    }
    
    # Run the tests
    success = run_notebook_tests(
        args.notebook,
        str(output_notebook),
        parameters,
        args.timeout
    )
    
    if success:
        # Generate report
        report = generate_report(str(output_notebook))
        
        # Save report
        report_file = output_dir / f"test_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Test execution completed. Results saved to: {output_notebook}")
        logger.info(f"Report saved to: {report_file}")
        
        if report.get("errors"):
            logger.warning(f"Tests completed with {len(report['errors'])} errors")
            sys.exit(1)
        else:
            logger.info("All tests completed successfully")
            sys.exit(0)
    else:
        logger.error("Test execution failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
