from src.simulation.mesh.cell import Cell

import numpy as np
from numpy.typing import NDArray
from typing import Dict, Tuple, List

class Triangle(Cell):
    """
    Class for triangles. Holds topological information about neigbours. Get updates from Mesh and Simulation classes.

    Neighbour information is calculated in Mesh class. 

    Attributes:
        center_point(float): calculated in-class
        normals: calculated in-class
        mean_flow: calculated by Simulation class
        concentration: calculated by Simulation class
    """
    _type = "triangle"

    def __init__(self, cell_id, nodes, coords):
        super().__init__(cell_id, nodes, coords)
        self._center_point: Tuple[float, float] = self.compute_center_point()
        self._normals: Dict[Tuple[int, int], NDArray[np.float64, np.float64]] = self.compute_normal()
        self._area: float = self.compute_area()
        self._mean_flow: Dict[Tuple[int, int], Tuple[float, float]] = {}
        self._concentration: float = 0.0

    @property
    def type(self):
        return "triangle"

    @property
    def center_point(self):
        return self._center_point

    @property
    def normals(self):
        return self._normals

    @property
    def area(self):
        return self._area

    @property
    def mean_flow(self):
        return self._mean_flow

    @property
    def concentration(self):
        return self._concentration
    
    @concentration.setter
    def concentration(self, value):
        self._concentration = value

    def compute_center_point(self):
        """Calculate center point for cell"""
        xs = np.mean([i[0] for i in self._coords.values()])
        ys = np.mean([i[1] for i in self._coords.values()])
        return (xs, ys)

    def compute_area(self):
        """Calculate area for cell"""
        p1, p2, p3 = self._coords.values()
        # area formula
        return abs((p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1])) / 2.0)

    def define_edges(self):
        """Find node numbers for edges"""
        assert len(self._nodes) == 3, "Wrong number of nodes in Triangel object"
        edge_list = [
            tuple(sorted((self._nodes[0], self._nodes[1]))),
            tuple(sorted((self._nodes[1], self._nodes[2]))),
            tuple(sorted((self._nodes[2], self._nodes[0]))),
        ]
        return edge_list

    def compute_normal(self) -> Dict[Tuple[int, int], NDArray[np.float64]]:
        """Calculate scaled normals for all edges in cell."""
        scaled_normals = {}

        for edge in self._edges:
            p1 = np.array(self._coords[edge[0]])
            p2 = np.array(self._coords[edge[1]])

            edge_vector = p2 - p1

            # Rotate 90 degrees: (x, y) -> (-y, x)
            normal_vector = np.array([-edge_vector[1], edge_vector[0]])

            # Normalize
            norm = np.linalg.norm(normal_vector)
            if norm == 0:
                raise ValueError(f"Zero length edge found at {edge}")
            normal_vector = normal_vector / norm

            # Check Direction (Outward pointing)
            midpoint = (p1 + p2) / 2
            to_center = np.array(self._center_point) - midpoint

            # If dot product > 0, normal points IN. Flip it.
            if np.dot(normal_vector, to_center) > 0:
                normal_vector = -normal_vector

            # Scale to edge length
            edge_length = np.linalg.norm(edge_vector)

            # Store as Numpy Array
            scaled_normals[edge] = tuple(normal_vector * edge_length)

        return scaled_normals

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
            f"Centerpoint:   {self._center_point}\n"
            f"Area:          {self._area}\n"
            f"Normals:       {format_dict(self._normals)}\n"
            f"Mean Flow:     {format_dict(self._mean_flow)}\n"
            f"Concentration: {self._concentration:.4f}\n"
        )
