from src.simulation.mesh.mesh import Mesh
from src.simulation.simulation import Simulation

import argparse
import shutil
import logging
from pathlib import Path
from config import load_config, ConfigError


def parse_input():
    """
    Parses command line input (CLI) to arguments for configuration selection.

    Returns
    -------
    argparse.Namespace
        Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="Oil spill simulation")
    parser.add_argument("-c", "--config_file", default="input.toml", help="Choose a config file to read (Default: input.toml)")
    parser.add_argument("--find_all", action="store_true", help="Find and run all config files")
    parser.add_argument("-f", "--folder", default=None, help="Folder to search for configs when using --find_all")
    return parser.parse_args()


def run_config(config_path):
    """
    Runs simulation for a single configuration file and stores results.

    Parameters
    ----------
    config_path : str or Path
        Path to the configuration (.toml) file.

    Notes
    -----
    Creates a results folder for the simulation output. 
    Will not overwrite existing results.
    """
    print(f"Running simulation for config: {config_path}")

    config_path = Path(config_path)
    try:
        cfg = load_config(config_path)
    except ConfigError as error:
        print(f"Config error in {config_path}: {error}")
        return

    # Input variables (cfg is a dict with these data)
    n_steps = cfg["n_steps"] 
    t_end = cfg["t_end"]
    delta_t = t_end / n_steps
    mesh_name = cfg["mesh_name"] 
    borders = cfg["borders"]
    log_name = cfg["log_name"]
    write_frequency = cfg["write_frequency"]

    # Setting up mesh instances
    manager = Mesh()
    manager.read_mesh(file=mesh_name)
    manager.create_cells()
    manager.build_topology()
    manager.assign_neighbours()

    result_folder = Path("results") / config_path.stem
    if result_folder.exists():
        if not result_folder.is_dir():
            raise RuntimeError(f"{result_folder} already exists and is not a directory")
        raise RuntimeError(f"{result_folder} already exists, will not overwrite")
    result_folder.mkdir(parents=True, exist_ok=False)

    # Setting up logger
    logger = logging.getLogger(config_path.stem)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(result_folder / f"{log_name}.log")
    file_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Simulation parameters:")
    for key, value in cfg.items():
        logger.info(f"{key}: {value}")

    sim = Simulation(manager, borders, logger)
    sim.initial_conditions()
    tmp_dir = result_folder / "tmp"
    tmp_dir.mkdir()

    sim.solver(delta_t=delta_t, write_frequency=write_frequency, tmp_dir=tmp_dir, number_of_steps=n_steps)

    plot_path = result_folder / "simulation_plot.png"
    sim.plot_mesh(plotfile=str(plot_path))

    video_path = result_folder / "simulation.mp4"

    if write_frequency is not None:
        sim.create_video(
            tmp_dir=tmp_dir,
            output_file=str(video_path),
            frame_rate=5
        )

    # Deletes all plot files in the folder tmp, but not the tmp folder itself
    shutil.rmtree(tmp_dir, ignore_errors=True)

    print(f"Finished running {config_path}. Results can be seen in {result_folder}")


def run_simulation_with_config():
    """
    Parses CLI arguments and runs one or multiple simulations based on 
    configuration files.

    Notes
    -----
    Supports running all .toml files in a folder with --find_all,
    or a single file with -c/--config_file.
    """
    args = parse_input()

    # CLI option 1: --find_all that runs all .toml-files
    if args.find_all:
        folder = Path(args.folder) if args.folder is not None else Path(".")

        if not folder.is_dir():
            print(f"{folder} does not exist")
            return

        toml_files = sorted(folder.glob("*.toml"))

        if not toml_files:
            print("Did not find any toml files")
            return

        for cfg_file in toml_files:
            run_config(cfg_file)

    # CLI option 2: -c or --config_file that only runs one config file
    else:
        run_config(args.config_file)