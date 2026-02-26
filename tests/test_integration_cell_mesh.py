import pytest
from pathlib import Path

from src.simulation.mesh.mesh import Mesh


@pytest.fixture
def built_mesh():
    mesh = Mesh()
    mesh_path = Path(__file__).parent / "super_simple_test_mesh.msh"
    mesh.read_mesh(str(mesh_path))
    mesh.create_cells()
    mesh.build_topology()
    mesh.assign_neighbours()
    return mesh


# Integration tests for cell mesh relationships and properties
def test_mesh_neighbour_edge_in_cell1(built_mesh):
    # For every edge shared by two cells, cell_1 lists the edge as a neighbour
    for edge, cell_ids in built_mesh.mesh_edges.items():
        if len(cell_ids) == 2:
            cell_1 = built_mesh.cells[cell_ids[0]]
            assert (edge in cell_1.neighbour_ids
                    ), "Neighbour edge missing in cell 1"


def test_mesh_neighbour_edge_in_cell2(built_mesh):
    # For every edge shared by two cells, cell_2 lists the edge as a neighbour
    for edge, cell_ids in built_mesh.mesh_edges.items():
        if len(cell_ids) == 2:
            cell_2 = built_mesh.cells[cell_ids[1]]
            assert (edge in cell_2.neighbour_ids
                    ), "Neighbour edge missing in cell 2"


def test_mesh_neighbour_id_consistency(built_mesh):
    # For every edge shared by two cells, each cell lists the other as a neighbour
    for edge, cell_ids in built_mesh.mesh_edges.items():
        if len(cell_ids) == 2:
            cell_1 = built_mesh.cells[cell_ids[0]]
            cell_2 = built_mesh.cells[cell_ids[1]]
        assert (
            cell_1.neighbour_ids[edge] == cell_2.id or
            cell_2.neighbour_ids[edge] == cell_1.id
        ), "Neighbour ID inconsistency"


def test_mesh_connectivity(built_mesh):
    # Traverse neighbors from first triangle, ensure all cells are reachable
    visited = set()  # track visited cell ids
    to_visit = [built_mesh.cells[0].id]  # start from first cell
    while to_visit:
        cell_id = to_visit.pop() 
        if cell_id in visited:
            continue
        visited.add(cell_id)
        cell = built_mesh.cells[cell_id]
        to_visit.extend(neighbour_id for neighbour_id in cell.neighbour_ids.values() if neighbour_id not in visited)
    assert (len(visited) == len(built_mesh.cells)
            ), "Not all cells are reachable via neighbours"


def test_mesh_edge_sharing(built_mesh):
    # Every edge is shared by exactly two cells
    for edge, cell_ids in built_mesh.mesh_edges.items():
        assert (len(cell_ids) == 2
                ), "Edge sharing count incorrect(should be 2)"


def test_mesh_neighbor_type_relationships_line(built_mesh):
    # For every line cell, its neighbour is a triangle; 
    for cell in built_mesh.cells:
        if cell.type == "line":
            neighbour_id = next(iter(cell.neighbour_ids.values()))
            neighbour = built_mesh.cells[neighbour_id]
            assert (neighbour.type == "triangle"
                    ), "Line neighbour type incorrect"


def test_mesh_neighbor_type_relationships_triangle(built_mesh):
    # For every triangle, neighbours are triangle or line
    for cell in built_mesh.cells:     
        if cell.type == "triangle":
            for neighbour_id in cell.neighbour_ids.values():
                neighbour = built_mesh.cells[neighbour_id]
                assert (neighbour.type in ("triangle", "line")
                        ), "Triangle neighbour type incorrect"
