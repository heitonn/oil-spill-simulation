import subprocess
import sys
from pathlib import Path

"""
Acceptance test for oil-spill-simulation:
runs the main program with a known config and checks for expected output files.
"""


def _run_simulation_and_get_results(tmp_path):
    """
    Helper to run the simulation and return the results directory and process result.
    """
    test_dir = tmp_path  # use temporary directory for test

    # Copy necessary files to temp directory
    config_src = Path(__file__).parent.parent / "input.toml"
    mesh_src = Path(__file__).parent.parent / "bay.msh"

    config_dst = test_dir / "input.toml"
    mesh_dst = test_dir / "bay.msh"

    config_dst.write_text(config_src.read_text())
    mesh_dst.write_text(mesh_src.read_text())

    main_py = Path(__file__).parent.parent / "main.py"
    python_exe = sys.executable  # current python executable ensures correct environment

    # Run the main.py with the test config as a subprocess
    result = subprocess.run([
        python_exe, str(main_py), "-c", str(config_dst.name)
    ], cwd=test_dir, capture_output=True, text=True)
    results_dir = test_dir / "results" / config_dst.stem
    return results_dir, result


def test_acceptance_results_folder_created(tmp_path):
    results_dir, result = _run_simulation_and_get_results(tmp_path)
    assert results_dir.exists(), f"Results folder {results_dir} not created"


def test_acceptance_log_file_created(tmp_path):
    results_dir, result = _run_simulation_and_get_results(tmp_path)
    assert (results_dir / "log.log").exists(), "Log file not created"


def test_acceptance_plot_file_created(tmp_path):
    results_dir, result = _run_simulation_and_get_results(tmp_path)
    assert (results_dir / "simulation_plot.png").exists(), "Plot file not created"


def test_acceptance_video_file_created(tmp_path):
    results_dir, result = _run_simulation_and_get_results(tmp_path)
    assert (results_dir / "simulation.mp4").exists(), "Video file not created"
