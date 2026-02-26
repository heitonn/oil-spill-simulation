from pathlib import Path
import toml

class ConfigError(Exception):
    """
    Class that validates and returns input-data from .toml files to dictonary. If one of the validations fails, the custom exception is raised.
    """
    pass

def load_config(path): # eksempelinput: "configs/test.toml"
    """
    Checking respectively,
    - If the file actually exists and if it can be parsed
    - If []..
    """
    config_path = Path(path)

    if not config_path.is_file():
        raise ConfigError(f"Config file '{config_path}' does not exist")

    try: 
        raw_data = toml.load(config_path)
    except toml.TomlDecodeError as toml_syntax_error:
        raise ConfigError(f"Invalid TOML syntax in '{config_path}': {toml_syntax_error}")

    if "settings" not in raw_data:
        raise ConfigError("Missing [settings] section i config file")

    if "geometry" not in raw_data:
        raise ConfigError("Missing [geometri] section in config file")

    settings = raw_data["settings"] # Mandatory
    geometry = raw_data["geometry"] # Mandatory
    io = raw_data.get("IO",{}) # Not mandatory

    if "nSteps" not in settings:
        raise ConfigError("missing 'nSteps' in [settings]")
    if "tEnd" not in settings:
        raise ConfigError("Missing 'tEnd' in [settings].")

    n_steps = settings["nSteps"]
    t_end = settings["tEnd"]

    if not isinstance(n_steps, int) or n_steps <= 0: 
        raise ConfigError("'nSteps' must be a positive integer")
    if not isinstance(t_end, (int, float)) or t_end <= 0: 
        raise ConfigError("'tEnd' must be a positive number")
    
    if "meshName" not in geometry:
        raise ConfigError("missing 'meshName' in [geometry]")
    if "borders" not in geometry:
        raise ConfigError("Missing 'borders' in [geometry]")
    
    mesh_name = geometry["meshName"]
    borders = geometry["borders"]

    if not isinstance(mesh_name, str) or not mesh_name:
        raise ConfigError("meshName must be a string that is not empty")
    
    for row in borders:
        if not isinstance(row, (list,tuple)) or len(row) != 2:
            raise ConfigError("[borders] needs to be in the format of [[xmin,xmax],[ymin,ymax]]")

    xmin, xmax = borders[0]
    ymin, ymax = borders[1]
    
    for value in (xmin, xmax, ymin, ymax):
        if not isinstance(value, (int, float)):
            raise ConfigError("Borders for fishing grounds needs to be a number")
        
    
    if xmin >= xmax or ymin >= ymax:
        raise ConfigError("Borders for fishing grounds needs to make geometrical sense")
    
    log_name = io.get("logName", "logfile")
    
    if not isinstance(log_name, str): 
        raise ConfigError("Log name needs to be a string value")
    
    write_frequency = io.get("writeFrequency")
    if write_frequency is not None:
        if not isinstance(write_frequency, int) or write_frequency <= 0:
            raise ConfigError("writeFrequency needs to be a positive integer")

    return {
            "n_steps": n_steps, # int
            "t_end": float(t_end), # float
            "mesh_name": mesh_name, # str
            "borders": ((float(xmin), float(xmax)), # ((xmin,xmax),(ymin,ymax))
                        (float(ymin), float(ymax))),
            "log_name": log_name, # str
            "write_frequency": write_frequency, # int eller None
        }


