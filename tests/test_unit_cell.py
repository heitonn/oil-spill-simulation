import pytest
import numpy as np

from src.simulation.mesh.cellfactory import CellFactory
from src.simulation.mesh.cell import Cell
from src.simulation.mesh.line import Line 
from src.simulation.mesh.triangle import Triangle


@pytest.fixture
def cell_factory():
    return CellFactory()


# Test cases for Triangle cells with calculated expected values for area, center, and normals
# Names and details of the triangels are based on the suoper_simple_test_mesh.msh
TRIANGLE_CASES = [
    {
        "name": "T_0_4_5",
        "input": {
            "type": "triangle",
            "id": 1,
            "nodes": (0, 4, 5),
            "coords": {0:(0.0,0.0), 4:(0.25,0.5), 5:(0.0,1.0)},
        },
        "expected": {
            "area": 0.125,
            "center": (1/12, 1/2),  # (0.083333..., 0.5)
            "scaled_outer_normals": {
                (0, 4): np.array([ 0.5 , -0.25]),
                (4, 5): np.array([ 0.5 ,  0.25]),
                (0, 5): np.array([-1.0 ,  0.0 ]),
            },
        },
    },
    {
        "name": "T_1_3_4",
        "input": {
            "type": "triangle",
            "id": 2,
            "nodes": (1, 3, 4),
            "coords": {1:(0.5,0.0), 3:(0.5,0.5), 4:(0.25,0.5)},
        },
        "expected": {
            "area": 0.0625,
            "center": (5/12, 1/3),  # (0.416666..., 0.333333...)
            "scaled_outer_normals": {
                (1, 3): np.array([ 0.5 ,  0.0 ]),
                (3, 4): np.array([ 0.0 ,  0.25]),
                (1, 4): np.array([-0.5 , -0.25]),
            },
        },
    },
    {
        "name": "T_2_3_7",
        "input": {
            "type": "triangle",
            "id": 3,
            "nodes": (2, 3, 7),
            "coords": {2:(1.0,0.0), 3:(0.5,0.5), 7:(1.0,1.0)},
        },
        "expected": {
            "area": 0.25,
            "center": (5/6, 1/2),  # (0.833333..., 0.5)
            "scaled_outer_normals": {
                (2, 3): np.array([-0.5 , -0.5 ]),
                (3, 7): np.array([-0.5 ,  0.5 ]),
                (2, 7): np.array([ 1.0 ,  0.0 ]),
            },
        },
    },
]


@pytest.fixture(params=TRIANGLE_CASES, ids=lambda c: c["name"])
def triangle_case(request):
    # fixed parameterized fixture for triangle test cases
    return request.param


# Test cases for Line cells
# Names, nodes, ids and coordinates based on super_simple_test_mesh.msh
LINE_CASES = [
    {
        "name": "L_0_1_bottom",
        "input": {
            "type": "line",
            "id": 101,
            "nodes": (0, 1),
            "coords": {0: (0.0, 0.0), 1: (0.5, 0.0)},
        },
        "expected": {
            "edge": (0, 1),
            "length": 0.5,
        },
    },
    {
        "name": "L_1_2_bottom",
        "input": {
            "type": "line",
            "id": 102,
            "nodes": (1, 2),
            "coords": {1: (0.5, 0.0), 2: (1.0, 0.0)},
        },
        "expected": {
            "edge": (1, 2),
            "length": 0.5,
        },
    },
    {
        "name": "L_2_7_right_vertical", 
        "input": {
            "type": "line",
            "id": 103,
            "nodes": (2, 7),
            "coords": {2: (1.0, 0.0), 7: (1.0, 1.0)},
        },
        "expected": {
            "edge": (2, 7),
            "length": 1.0,
        },
    },
]


@pytest.fixture(params=LINE_CASES, ids=lambda c: c["name"])
def line_case(request):
    # fixed parameterized fixture for line test cases
    return request.param


# Test cases for CellFactory and cell properties
def test_cellfactory_creates_triangle(cell_factory, triangle_case):
    cell = cell_factory(triangle_case["input"])
    assert (isinstance(cell, Triangle)
            ), "CellFactory did not create Triangle cell type"


def test_cellfactory_sets_cell_id(cell_factory, triangle_case):
    cell = cell_factory(triangle_case["input"])
    assert (cell.id == triangle_case["input"]["id"]
            ), "Cell ID does not match expected ID"


def test_cellfactory_sets_nodes(cell_factory, triangle_case):
    cell = cell_factory(triangle_case["input"])
    assert (cell.nodes == triangle_case["input"]["nodes"]
            ), "Nodes do not match expected nodes"


def test_cellfactory_sets_first_coord(cell_factory, triangle_case):
    cell = cell_factory(triangle_case["input"])
    n0 = triangle_case["input"]["nodes"][0]
    assert (cell.coords[n0] == triangle_case["input"]["coords"][n0]
            ), "First coordinate does not match expected coordinate"


def test_cellfactory_sets_second_coord(cell_factory, triangle_case):
    cell = cell_factory(triangle_case["input"])
    n1 = triangle_case["input"]["nodes"][1]
    assert (cell.coords[n1] == triangle_case["input"]["coords"][n1]
            ), "Second coordinate does not match expected coordinate"


# Test cases for Triangle properties
def test_triangle_area(cell_factory, triangle_case):
    tri = cell_factory(triangle_case["input"])
    assert (tri.area == pytest.approx(triangle_case["expected"]["area"])
            ), "Triangle area does not match expected area"


def test_triangle_xcenter(cell_factory, triangle_case):
    tri = cell_factory(triangle_case["input"])
    cx, cy = tri.center_point
    assert (cx == pytest.approx(triangle_case["expected"]["center"][0])
            ), "Triangle center x-coordinate does not match expected x coordinate"


def test_triangle_ycenter(cell_factory, triangle_case):
    tri = cell_factory(triangle_case["input"])  
    cx, cy = tri.center_point
    assert (cy == pytest.approx(triangle_case["expected"]["center"][1])
            ), "Triangle center y-coordinate does not match expected y coordinate"


def test_triangle_edges(cell_factory, triangle_case):
    tri = cell_factory(triangle_case["input"])
    n0, n1, n2 = triangle_case["input"]["nodes"]
    expected_edges = {
        tuple(sorted((n0, n1))),
        tuple(sorted((n1, n2))),
        tuple(sorted((n2, n0))),
    }
    assert (set(tri.edges) == expected_edges
            ), "Triangle edges do not match expected edges"


def test_triangle_scaled_outer_normals(cell_factory, triangle_case):
    tri = cell_factory(triangle_case["input"])
    expected_normals = triangle_case["expected"]["scaled_outer_normals"]

    for edge, normal in expected_normals.items():
        assert (np.array(tri.normals[edge]) == pytest.approx(np.array(normal))
                ), "Scaled outer normal does not match expected value"


def test_triangle_outer_normals_length(cell_factory, triangle_case):
    tri = cell_factory(triangle_case["input"])

    for edge in tri.edges:
        p1 = np.array(tri.coords[edge[0]])
        p2 = np.array(tri.coords[edge[1]])
        edge_length = np.linalg.norm(p2 - p1)

        normal_vec = np.array(tri.normals[edge])
        normal_length = np.linalg.norm(normal_vec)

        assert (normal_length == pytest.approx(edge_length)
                ), "Outer normal length does not match edge length"


def test_outer_normal_points_outwards(cell_factory, triangle_case):
    tri = cell_factory(triangle_case["input"])

    center = np.array(tri.center_point)

    for edge in tri.edges:
        p1 = np.array(tri.coords[edge[0]])
        p2 = np.array(tri.coords[edge[1]])
        midpoint = (p1 + p2) / 2

        n = np.array(tri.normals[edge])  # scaled normal

        # Vector from midpoint on edge towards center:
        to_center = center - midpoint

        # Checks if dot(n, to_center) <= 0/close to zero
        assert (np.dot(n, to_center) <= 1e-12
                ), "Outer normal does not point outwards"


def test_triangle_area_non_negative(cell_factory, triangle_case):
    tri = cell_factory(triangle_case["input"])
    assert (tri.area >= 0
            ), "Triangle area is negative"


def test_triangle_coords_match_nodes(cell_factory, triangle_case):
    tri = cell_factory(triangle_case["input"])
    assert (set(tri.coords.keys()) == set(tri.nodes)
            ), "Triangle coords keys do not match nodes"


def test_triangle_has_three_edges(cell_factory, triangle_case):
    tri = cell_factory(triangle_case["input"])
    assert (len(tri.edges) == 3
            ), "Triangle does not have exactly three edges"


def test_area_zero_for_colinear_points(cell_factory):
    tri = cell_factory({
        # special triangle with colinear points
        "type": "triangle",
        "id": 0,
        "nodes": (0, 1, 2),
        "coords": {
            0: (0.0, 0.0),
            1: (1.0, 0.0),
            2: (2.0, 0.0),  # colinear
        },
    })
    assert (tri.area == pytest.approx(0.0)
            ), "Triangle area is not approximately zero for colinear points"


def test_cellfactory_creates_line(cell_factory, line_case):
    cell = cell_factory(line_case["input"])
    assert (isinstance(cell, Line)
            ), "CellFactory did not create Line cell type"


def test_line_sets_cell_id(cell_factory, line_case):
    line = cell_factory(line_case["input"])
    assert (line.id == line_case["input"]["id"]
            ), "Line id does not match expected id"


def test_line_sets_nodes(cell_factory, line_case):
    line = cell_factory(line_case["input"])
    assert (line.nodes == line_case["input"]["nodes"]
            ), "Line nodes do not match expected nodes"


def test_line_sets_coords(cell_factory, line_case):
    line = cell_factory(line_case["input"])
    for nid, xy in line_case["input"]["coords"].items():
        assert (line.coords[nid] == xy
                ), "Line coords do not match expected coords"


def test_line_has_one_edge(cell_factory, line_case):
    line = cell_factory(line_case["input"])
    assert (len(line.edges) == 1
            ), "Line does not have exactly one edge"


def test_line_edge_matches_expected(cell_factory, line_case):
    line = cell_factory(line_case["input"])
    assert (line.edges[0] == tuple(sorted(line_case["expected"]["edge"]))
            ), "Line edge does not match expected edge"


def test_line_edge_length_matches_expected_length(cell_factory, line_case):
    line = cell_factory(line_case["input"])

    edge = line.edges[0]
    p1 = np.array(line.coords[edge[0]])
    p2 = np.array(line.coords[edge[1]])
    length = np.linalg.norm(p2 - p1)

    assert (length == pytest.approx(line_case["expected"]["length"])
            ), "Line edge length does not match expected length"


def test_line_coords_match_nodes(cell_factory, line_case):
    line = cell_factory(line_case["input"])
    assert (set(line.coords.keys()) == set(line.nodes)
            ), "Line coords keys do not match nodes"


# Test CellFactory registration of new cell types
class DummyRectangle(Cell):
    """
    Dummy cell used only for testing CellFactory.register().
    """
    _type = "rectangle"

    @property
    def type(self):
        return self._type

    def define_edges(self):
        # abstract method implementation
        # Four nodes and edges
        assert len(self._nodes) == 4, "Rectangle must have 4 nodes"

        n0, n1, n2, n3 = self._nodes
        return [
            tuple(sorted((n0, n1))),
            tuple(sorted((n1, n2))),
            tuple(sorted((n2, n3))),
            tuple(sorted((n3, n0))),
        ]

# Tetst CellFactory registration of new cell types using DummyRectangle
def test_cellfactory_registers_new_type(cell_factory):
    cell_factory.register("rectangle", DummyRectangle)
    assert ("rectangle" in cell_factory._cell_types
    ), "New cell type not registered in CellFactory"


def test_cellfactory_creates_registered_type(cell_factory):
    cell_factory.register("rectangle", DummyRectangle)

    cell_data = {
        "type": "rectangle",
        "id": 99,
        "nodes": (0, 1, 2, 3),
        "coords": {
            0: (0.0, 0.0),
            1: (1.0, 0.0),
            2: (1.0, 1.0),
            3: (0.0, 1.0),
        },
    }
    cell = cell_factory(cell_data)
    assert (isinstance(cell, DummyRectangle)
            ), "CellFactory did not create registered cell type"


def test_cellfactory_creates_registered_type_id(cell_factory):
    cell_factory.register("rectangle", DummyRectangle)
    cell_data = {
        "type": "rectangle",
        "id": 99,
        "nodes": (0, 1, 2, 3),
        "coords": {
            0: (0.0, 0.0),
            1: (1.0, 0.0),
            2: (1.0, 1.0),
            3: (0.0, 1.0),
        },
    }
    cell = cell_factory(cell_data)
    assert cell._id == 99  # random id
