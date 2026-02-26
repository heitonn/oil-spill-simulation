from src.simulation.mesh import Mesh
from src.simulation.mesh.triangle import Triangle
from src.simulation.mesh.line import Line

import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.patches import Rectangle


class Simulation:
    """
    Manages simulation of oil flow over mesh of cells.

    The Simulation class must be instanciated with a Mesh class instance as constructor.
    Simulation parameters is given in toml files.

    Attributes
    ----------
    cells (Mesh): The area for the simulation

    Methods
    -------
    initial_conditions  : Sets initial oil concentration and flow field values for every cell. 
    solver              : Executes the simulation
    plot_mesh           : Makes plot of oil distribution 
    create_video        : Makes a video of oil distribution over time
    """

    def __init__(self, mesh, borders, logger=None):
        self._mesh = mesh
        self._borders = borders
        self._logger = logger
        self._oil_in_fishing_grounds = []
        self._source_point = np.array([0.305, 0.45])

    def initial_oil_concentration(self, location):
        """
        Calculate initial oil concentration at given point.

        Parameters
        ----------
        location : array_like, x and y coordinate

        Returns
        -------
        float
            The calculated oil concentration (unitless value between 0 and 1).

        """
        return np.exp(-np.linalg.norm(location - self._source_point)**2/0.01)

    @staticmethod
    def compute_flow_field(point):
        """
        Calculates the flow at given point.

        Parameters
        ----------
        point : array_like, x and y coordinate

        Returns
        -------
        vector

`       Notes
        -----
        Velocity field v(x) = (y - 0.2x, -x)
        """
        x = point[0]
        y = point[1]
        return (y - 0.2 * x, -x)

    @staticmethod
    def oil_velocity(outer_normal, mean_flow, concentration, concentration_neighbour):
        """
        Calculatate sum of oil flux over one edge in a cell.

        Parameters
        ----------
        outer_normal            : vector
        mean_flow               : vector 
        concentration           : float
        concentration_neighbour : float

        Returns
        -------
        edge_flux               : float
        """
        velocity_oil_direction = np.dot(mean_flow, outer_normal)
        if velocity_oil_direction > 0:
            edge_flux = concentration * velocity_oil_direction
        else:
            edge_flux = concentration_neighbour * velocity_oil_direction
        return edge_flux

    def initial_conditions(self):
        """
        Calculate initial values, oil concentration for all cells, and flow field
        for all edges.

        Notes
        -----
        Uses instance variables
        _mesh       : give access to cells

        Updates
        _mesh.cells : cell.concentration
        _mesh.cells : cell.mean_flow (for each edge)
        """
        for cell in self._mesh.cells:

            # Do not calculate anything for line cells
            if isinstance(cell, Line):
                continue

            cell.concentration = self.initial_oil_concentration(cell.center_point)

            for edge in cell.edges:
                # Calculate and store average flow for neighbouring cells
                # flow_field_current cell
                vectors = [self.compute_flow_field(cell.center_point)]
                # flow_field neighbour (if there is a neighbour)
                neighbour_id = cell.neighbour_ids[edge]
                if neighbour_id:
                    neighbour_cell = self._mesh.cells[neighbour_id]
                    if neighbour_cell.type != "line":
                        vectors.append(self.compute_flow_field(neighbour_cell.center_point))

                # average flow_field and store to edge
                mean_flow_array = np.mean(vectors, axis=0)
                cell.mean_flow[edge] = tuple(mean_flow_array)

    def solver(self, number_of_steps=20, delta_t=0.01, write_frequency=None, tmp_dir=None):
        """
        Run the simulation for all cells over all time steps.

        Parameters
        ----------
        number_of_steps : int
        delta_t         : float
        write_frequency : int
        tmp_dir         : str

        Notes
        -----
        Uses instance variables
        _mesh       : give access to cells

        Updates
        _mesh.cells : cell.concentration
        _mesh.cells : cell.mean_flow (for each edge)
        _oil_in_fishing_grounds
        """
        print()
        print("Solving . . .")
        self._number_of_steps = number_of_steps
        step = 0
        while step < number_of_steps:
            # Dict to store new oil concentration results for current step
            concentration_tmp = {}

            for cell in self._mesh.cells:
                # Do not calculate anything for line cells
                if cell.type == "line":
                    continue

                concentration = cell.concentration

                edges_net_flux = []
                for edge in cell.edges:
                    # Look up neigbouring cell and its concentration
                    neighbour_id = cell.neighbour_ids[edge]
                    neighbour_cell = self._mesh.cells[neighbour_id]             
                    # Do not calculate flux to line cell neighbours
                    if neighbour_cell.type == "line":
                        continue

                    # Collect data for flux calculation
                    concentration_neighbour = neighbour_cell.concentration
                    outer_normal = cell.normals[edge]
                    mean_flow = cell.mean_flow[edge]

                    # Flux per edge
                    edge_flux = self.oil_velocity(
                        outer_normal, mean_flow, concentration, concentration_neighbour)
                    edges_net_flux.append(edge_flux)
             
                # Find total flux and new concentration value
                total_flux = -(sum(edges_net_flux) * delta_t) / cell.area
                new_concentration = concentration + total_flux

                # Store total flux to temporary dict
                concentration_tmp[cell.id] = new_concentration

            # After each step - store new concentration values in cells
            for cell_id, new_concentration in concentration_tmp.items():
                self._mesh.cells[cell_id].concentration = concentration_tmp[cell_id]

            # Calculate and store oil volume for cells inside fish ground
            total_oil = sum(cell.concentration*cell.area for cell in self._mesh.cells
                            if not isinstance(cell, Line)
                            and self._borders[0][0] <= cell.center_point[0] <= self._borders[0][1]
                            and self._borders[1][0] <= cell.center_point[1] <= self._borders[1][1])
            self._oil_in_fishing_grounds.append(total_oil)

            if self._logger:
                self._logger.info(f"Step {step}: total oil in fishing grounds = {total_oil}")

            if write_frequency is not None and step % write_frequency == 0:
                plot_path = tmp_dir / f"simulation_plot{step}.png"
                self.plot_mesh(plot_path)

            step = step + 1
        print()

    def plot_mesh(self, plotfile="simulation_plot.png"):
        """
        Makes plot of oil distribution.

        Parameters
        ----------
        plotfile            : str
        """
        plotfile = str(plotfile)
        fig, (ax_mesh, ax_plot) = plt.subplots(1, 2, figsize=(14, 6))
        cmap = plt.get_cmap("coolwarm")

        # Oil mesh
        for cell in self._mesh.cells:
            if isinstance(cell, Line):
                continue
            triangle = tuple(cell.coords.values())
            if len(triangle) < 3:
                continue
            poly = Polygon(triangle, closed=True, facecolor=cmap(cell.concentration))
            ax_mesh.add_patch(poly)

        ax_mesh.set_aspect('equal')
        (fg_xmin, fg_xmax), (fg_ymin, fg_ymax) = self._borders
        fishing_grounds = Rectangle(
            (fg_xmin, fg_ymin),
            fg_xmax - fg_xmin,
            fg_ymax - fg_ymin,
            linewidth=2,
            facecolor="green",
            alpha=0.5,
            label="Fishing grounds"
        )
        ax_mesh.add_patch(fishing_grounds)
        ax_mesh.legend()
        sm = plt.cm.ScalarMappable(cmap=cmap)
        sm.set_array([])
        fig.colorbar(sm, ax=ax_mesh, label="Oil concentration [%]")
        ax_mesh.set_title("Oil concentration mesh")

        # Oil over time
        if self._oil_in_fishing_grounds:
            steps = range(len(self._oil_in_fishing_grounds))
            ax_plot.plot(steps, self._oil_in_fishing_grounds, color='orange', marker='o')
            ax_plot.set_xlabel("Step")
            ax_plot.set_ylabel("Total oil in fishing grounds")
            ax_plot.set_title("Oil over time [area]")
            ax_plot.grid(True)
            if hasattr(self, '_number_of_steps'):
                ax_plot.set_xlim(0, self._number_of_steps)
        fig.tight_layout()
        fig.savefig(plotfile)
        plt.close(fig)
        print(f"Plot saved to {plotfile}")

    def create_video(self, tmp_dir, frame_rate=5, output_file="simulation.mp4"):
        """
        Makes a video of oil distribution over time.
        Parameters
        ----------
        tmp_dir     : str
        frame_rate  : int
        output_file : str
        """
        # Get the list of image files in the directory
        # Adjust range and step as needed
        # images = [f"tmp/simulation_plot{i}.png" for i in range(0, number_of_steps, write_frequency)]
        images = sorted(tmp_dir.glob("simulation_plot*.png"),
                        key=lambda p: int(p.stem.replace("simulation_plot", "")))

        # determine dimension from first image
        frame = cv2.imread(str(images[0]))
        height, width, layers = frame.shape
        # Define the codec and create a VideoWriter object
        # or 'XVID', 'DIVX', 'mp4v' etc.
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(output_file, fourcc,
                                frame_rate, (width, height))
        for image in images:
            img = cv2.imread(str(image))
            if img is not None:
                video.write(img)
            else:
                print(f"Could not read image: {image}")
        video.release()
        print(f"Video saved to {output_file}")
