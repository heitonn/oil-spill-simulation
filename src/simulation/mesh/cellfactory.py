from src.simulation.mesh.triangle import Triangle
from src.simulation.mesh.line import Line

class CellFactory:
    """
    Creates instances of cells, based on data in dictionary it receives in the call.

    CellFactory is called from Mesh class and creates instances of Triangle and Line classes.

    Parameters:
        cell_id(int): unique identifier for cell
        nodes(List): Node (point) numbers
        coords(Dict): Dictionary with node numbers and coordinate pairs
    """

    def __init__(self):
        self._cell_types = {"line": Line, "triangle": Triangle}
    
    def register(self, key, type):
        if key not in self._cell_types:
            self._cell_types[key] = type

    def __call__(self, cell):
        key = cell["type"]
        return self._cell_types[key](cell["id"], cell["nodes"], cell["coords"])