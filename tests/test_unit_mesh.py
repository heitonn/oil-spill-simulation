import pytest
from pathlib import Path

from src.simulation.mesh.mesh import Mesh


@pytest.fixture
def simple_mesh():
    mesh = Mesh()
    mesh_path = Path(__file__).parent / "super_simple_test_mesh.msh"
    mesh.read_mesh(str(mesh_path))
    mesh.create_cells()
    mesh.build_topology()
    mesh.assign_neighbours()
    return mesh


# Unit tests based on the simple test mesh
# Simple test mesh has 8 points, 14 cells (6 lines, 8 triangles)
def test_mesh_reads_points_count(simple_mesh):
    assert len(simple_mesh.points) == 8, "incorrect number of points read"


def test_mesh_creates_expected_cell_count(simple_mesh):
    assert len(simple_mesh.cells) == 14, "incorrect number of cells created"


def test_mesh_contains_triangles(simple_mesh):
    assert (any(cell.type == "triangle" for cell in simple_mesh.cells)
            ), "No triangle found in mesh"


def test_mesh_contains_lines(simple_mesh):
    assert (any(cell.type == "line" for cell in simple_mesh.cells)
            ), "No line found in mesh"


def test_build_topology_has_edges(simple_mesh):
    assert len(simple_mesh.mesh_edges) > 0, "No edges fond in mesh"


def test_build_topology_all_edges_have_2_cells(simple_mesh):
    assert (all(len(ids) == 2 for ids in simple_mesh.mesh_edges.values())
            ), "Not all edges have exactly two cells"


def test_mesh_has_at_least_one_triangle_line_edge(simple_mesh):
    assert any(
        sum(simple_mesh.cells[cid].type == "line" for cid in ids) == 1
        for ids in simple_mesh.mesh_edges.values()
    ), "No edge shared by both line and triangle found"


def test_build_topology_every_cell_id_is_registered_on_its_edges(simple_mesh):
    assert all(
        cell.id in simple_mesh.mesh_edges[edge]
        for cell in simple_mesh.cells
        for edge in cell.edges
    ), "Cell ID missing from one of its edges"


def test_assign_neighbours_no_self_reference(simple_mesh):
    # makes sure the neighbour ids do not include the cell's own id
    assert all(
        nid != cell.id
        for cell in simple_mesh.cells
        for nid in cell.neighbour_ids.values()
    ), "Cell has itself as neighbour"


def test_lines_have_exactly_one_neighbour(simple_mesh):
    assert all(
        len(cell.neighbour_ids) == 1
        for cell in simple_mesh.cells
        if cell.type == "line"
    ), "Line cell does not have exactly one neighbour"


def test_lines_neighbour_is_triangle(simple_mesh):
    # all line cells must have a triangle as neighbour
    assert all(
        simple_mesh.cells[next(iter(cell.neighbour_ids.values()))].type == "triangle"
        for cell in simple_mesh.cells
        if cell.type == "line"
    ), "Line cell has non-triangle neighbour"


def test_triangle_neighbour_count_is_always_three(simple_mesh):
    # all triangle cells must have exactly three neighbours (three edges)
    assert all(
        len(cell.neighbour_ids) == 3
        for cell in simple_mesh.cells
        if cell.type == "triangle"
    ), "Triangle cell  not have exactly three neighbours"


def test_triangle_neighbour_keys_match_edges(simple_mesh):
    # all triangle cells must have neighbour ids for all their edges
    assert all(
        set(cell.neighbour_ids.keys()) == set(cell.edges)
        for cell in simple_mesh.cells
        if cell.type == "triangle"
    ), "Triangle neighbour keys do not match edges"
