from src.simulation.mesh.cellfactory import CellFactory

import meshio
from collections import defaultdict

class Mesh:
    def __init__(self) -> None:
        """
        Reads mesh data file, calls CellFactory and builds mesh topology.

        After cells are created and the edges are defined, neighbours are assigned
        to edges, and finally neighbour IDs are assigned to the cells.

        Attributes:
        _points (tuple): A collection of (x, y) coordinates for all nodes.
        cells (list[Cell]): All cell objects (Triangles/Lines) in the mesh.
        _mesh_edges (dict): Maps edge tuples (n1, n2) to a list of neighbor cell IDs.
        """
        self._points: Tuple[Tuple[float, float], ...] = ()
        self._cells: List['Cell'] = []
        self._mesh_cell_blocks: List['CellBlock'] = []
        self._mesh_edges: Dict[Tuple[int, int], List[int]] = defaultdict(list)

    @property
    def cells(self):
        return self._cells
    
    @property
    def points(self):
        return self._points
    
    @property
    def mesh_edges(self):
        return self._mesh_edges

    def read_mesh(self, file="bay.msh"):
        """
        Read the mesh data file and store data in meshio data structure.
        """
        msh = meshio.read(file)
        self._mesh_cell_blocks = msh.cells
        # Create tuple of 2D coordinate tuples
        self._points = tuple((p[0], p[1]) for p in msh.points)

    def create_cells(self):
        """
        Loops over all cells in meshio data structure, gets point coordinates
        and hands over dict with cell information to  CellFactory, which
        instanciates the cell objects (lines or triangles).
        """
        factory = CellFactory()
        for cell_block in self._mesh_cell_blocks:
            if cell_block.type in ["vertex"]:
                continue
            for cell in cell_block.data:
                self._cells.append(factory({
                    "type": cell_block.type,
                    "id": len(self._cells),
                    "nodes": cell.tolist(),
                    "coords": {int(p): self._points[p] for p in cell}
                }))

    def build_topology(self):
        """
        Visits every cell in the mesh, every edge in each cell and store
        neighbour information for the edge in mesh_edges dictionary.
        Keys in the dict is edge points numbers (nodes) tuple.
        """
        for cell in self._cells:
            for edge in cell._edges:
                self._mesh_edges[edge].append(cell._id)

    def assign_neighbours(self):
        """
        Visits every cell in the mesh, gets the edges and
        looks up the same edge in mesh_edges dict.
        Stores the "outside" neigbour to the edge as a neighbour_id.
        neighbour_ids is stored with edge as key.
        """
        for cell in self._cells:
            for edge in cell.edges:
                edge_neighbour_ids = self._mesh_edges[edge]
                for neighbour_id in edge_neighbour_ids:
                    if neighbour_id != cell._id:
                        cell.neighbour_ids[edge] = neighbour_id

