import types
import pytest

import src.simulation.controller as controller


@pytest.fixture
def cfg_ok():
    # Minimal config/output for a successful run_config
    return {
        "n_steps": 10,
        "t_end": 20.0,
        "mesh_name": "dummy.msh",
        "borders": [[0.5, 0.65], [0.3, 0.6]],
        "log_name": "run",
        "write_frequency": None,
    }


def test_parse_input_defaults(monkeypatch):
    """
     Test that parse_input returns default values when no CLI args are given.
     """
    monkeypatch.setattr("sys.argv", ["main.py"]) # simulate no args
    args = controller.parse_input()
    assert args.config_file == "input.toml", "default toml file is not set correctly"


def test_run_simulation_with_config_calls_run_config(monkeypatch):
    """ Test that run_simulation_with_config calls run_config with correct path. """
    args = types.SimpleNamespace(find_all=False, folder=None, config_file="my.toml")
    monkeypatch.setattr(controller, "parse_input", lambda: args)

    called = {"x": False} # flag to check if run_config was called
    monkeypatch.setattr(controller, "run_config", lambda path: called.__setitem__("x", True))

    controller.run_simulation_with_config()
    assert called["x"] is True, "run_config path is not set correctly"


def test_run_config_returns_on_config_error(monkeypatch, tmp_path):
    """
    Test that run_config handles ConfigError and does not proceed.
    """

    class DummyConfigError(Exception):
        pass

    monkeypatch.setattr(controller, "ConfigError", DummyConfigError)

    def raise_config_error(_):
        # always raises config error
        raise DummyConfigError("bad config")

    monkeypatch.setattr(controller, "load_config", raise_config_error)
    mesh_created = {"x": False} # flag to check if Mesh was created

    class FakeMesh:
        def __init__(self):
            mesh_created["x"] = True # indicate Mesh was created

    monkeypatch.setattr(controller, "Mesh", FakeMesh) # fake Mesh class

    controller.run_config(tmp_path / "bad.toml") # should handle error internally
     # Mesh should not have been created due to config error
    assert mesh_created["x"] is False, "Program should have stopped due to config error, but did not."


def test_run_config_creates_results_folder(monkeypatch, tmp_path, cfg_ok):
    """
    Test that run_config creates a results folder for a valid config.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(controller, "load_config", lambda _: cfg_ok)

    # Fake Mesh and Simulation so that we do not run anything real
    class FakeMesh:
        def read_mesh(self, file): pass
        def create_cells(self): pass
        def build_topology(self): pass
        def assign_neighbours(self): pass

    class FakeSim:
        def __init__(self, *args, **kwargs): pass
        def initial_conditions(self): pass
        def solver(self, *args, **kwargs): pass
        def plot_mesh(self, *args, **kwargs): pass
        def create_video(self, *args, **kwargs): pass
    monkeypatch.setattr(controller, "Mesh", FakeMesh)
    monkeypatch.setattr(controller, "Simulation", FakeSim)

    # Avoid actual deletion (and avoid caring about tmp)
    monkeypatch.setattr(controller.shutil, "rmtree", lambda *args, **kwargs: None)

    controller.run_config("case.toml")

    # "results/<stem>"
    assert (tmp_path / "results" / "case").is_dir(), "No valid directory for this config file cerated"
