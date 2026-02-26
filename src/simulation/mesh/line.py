from src.simulation.mesh.cell import Cell

class Line(Cell):
    """
    Class for cells of type line. Holds topological information about neigbours, which get updated from Mesh.

    Do not hold any data used in simulation other than informing the Simulation class that this is the border of
    the area, and the oil flow stops here.
    """
    _type = "line"

    def __init__(self, cell_id, nodes, coords):
        super().__init__(cell_id, nodes, coords)

    @property
    def type(self):
        return "line"

    def define_edges(self):
        """Find node numbers for cell"""
        assert len(self._nodes) == 2, "Wrong number of nodes in Line object"
        return [tuple(sorted((self._nodes[0], self._nodes[1])))]

    def __str__(self):
        """Formats print of cell information"""
        def format_dict(d, indent=4):
            if not d:
                return " None"
            # Creates a string like: "\n    Key: Value"
            items = [f"\n{' ' * indent}{k}: {v}" for k, v in d.items()]
            return "".join(items)

        return (
            f"--- Cell {self._id} ({self._type}) ---\n"
            f"Nodes:         {self._nodes}\n"
            f"Edges:         {self._edges}\n"
            f"Neighbours:    {format_dict(self._neighbour_ids)}\n"
            f"Coordinates:   {format_dict(self._coords)}\n"
        )
