import pytest
import numpy as np

from src.simulation.simulation import Simulation
from src.simulation.mesh import Mesh

# Unit tests (isolated logic, mocks, static methods) 


def test_oil_velocity_positive_flux():
    # mean_flow and outer_normal aligned, positive flux
    outer_normal = np.array([1, 0])
    mean_flow = np.array([2, 0])
    concentration = 0.5
    concentration_neighbour = 0.2
    result = Simulation.oil_velocity(outer_normal, mean_flow, concentration, concentration_neighbour)
    assert result == pytest.approx(1.0) , "Positive flux should use own concentration"


def test_oil_velocity_negative_flux():
    # mean_flow and outer_normal anti-aligned, negative flux
    outer_normal = np.array([-1, 0])
    mean_flow = np.array([2, 0])
    concentration = 0.5
    concentration_neighbour = 0.2
    result = Simulation.oil_velocity(outer_normal, mean_flow, concentration, concentration_neighbour)
    assert result == pytest.approx(-0.4), "Negative flux should use neighbour concentration"


def test_initial_conditions_runs(monkeypatch):
    # Minimal mock mesh and cell to test initial_conditions runs without error
    # Mock cell is located at source_point, concentration should be 1.0
    # Since there are no neighbours, no mean_flow is set.
    class MockCell:
        def __init__(self):
            self.center_point = np.array([0.305, 0.45])
            self.edges = [0]
            self.neighbour_ids = {0: None}
            self.concentration = 0.0
            self.mean_flow = {}
            self.type = "triangle"
    
    class MockMesh:
        def __init__(self):
            self.cells = [MockCell()]
    mesh = MockMesh()
    borders = [(0.0, 1.0), (0.0, 1.0)]
    sim = Simulation(mesh, borders)
    sim.initial_conditions()
    assert mesh.cells[0].concentration == pytest.approx(1.0), "test_initial_conditions_runs failed to set concentration" 

# Integration-style tests (real Mesh/Simulation interaction)
@pytest.fixture
def simple_mesh():
    borders = [(0.0, 0.0), (1.0, 1.0)]
    mesh = Mesh()
    sim = Simulation(mesh, borders)
    return sim

@pytest.mark.parametrize("location, concentration", [
    (((0.4, 0.5), (0.305, 0.45)), 0.31584616612145),
    (((0.0, 0.0), (0.305, 0.45)), 0.0),
])
def test_initial_oil_concentration(simple_mesh, location, concentration):
    assert simple_mesh.initial_oil_concentration(location) == pytest.approx(concentration), \
        f"Error in calculation for initial_oil_concentration at {location}"

@pytest.mark.parametrize("point, flow_vector", [
    ((0.4, 0.5), (0.42, -0.4)),
    ((0.0, 0.0), (0.0, 0.0))
])
def test_compute_flow_field(simple_mesh, point, flow_vector):
    assert simple_mesh.compute_flow_field(point) == pytest.approx(flow_vector), \
        f"Error in calculation for compute_flow_field at point {point}"
