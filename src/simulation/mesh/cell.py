from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, Tuple, List


class Cell(ABC):
    """
    Base class for cells; Lines and Triangles.

    Attributes:
        id: unique identifier
        edges: tuples with node numbers for the edge - used as key for other attributes
        coords: tuples with node coordinates, nodes as key
        neighbour_id: list with neighbour ids, edge as key
    """

    def __init__(self, cell_id, nodes, coords):
        self._id: int = cell_id
        self._nodes: Tuple[int, ...] = tuple(node for node in nodes)
        self._edges: List[Tuple[int, int]] = self.define_edges()
        self._coords: Dict[int, Tuple[float, float]] = coords
        self._neighbour_ids: Dict[Tuple[int, int], List[int]] = defaultdict(list)

    @property
    @abstractmethod
    def type(self) -> str:
        """Returns the type of the cell ('triangle' or 'line')."""
        pass

    @property
    def id(self):
        return self._id
    
    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        return self._edges

    @property
    def coords(self):
        return self._coords

    @property
    def neighbour_ids(self):
        return self._neighbour_ids

    @abstractmethod
    def define_edges():
        pass
