import logging
import numpy as np
import matplotlib.pyplot as plt
import server as sv

from tabulate import tabulate

logger = logging.getLogger(__name__)


class MM1Simulation:
    def __init__(self, lambd: float, mu: float, time: float, dt: float = 0.1):
        self.lambd: float = lambd
        self.mu: float = mu
        self.T: float = time
        self.dt: float = dt

        self.server: sv.QueueServer = sv.QueueServer()

        self.arrival_times: list[float] = []
        self.service_times: list[float] = []
        self.start_times: list[float] = []
        self.end_times: list[float] = []
        self.waiting_times: list[float] = []

        self.Wq_sim: float | None = None
        self.L_sim: float | None = None
        self.Lq_sim: float | None = None

    def _exp(self, rate: float) -> float:
        return np.random.exponential(1.0 / rate)

    def generate_arrivals(self) -> None:
        assert self.T > 0, "Simulation time cannot be less than 0"
        assert self.lambd > 0, "Intensity of inflow cannot be less than 0"

        t: float = 0.0
        while True:
            t += self._exp(self.lambd)
            if t > self.T:
                break
            self.arrival_times.append(t)

    def generate_services(self) -> None:
        assert self.mu > 0, "Intensity of service cannot be less than 0"
        self.service_times = np.random.exponential(
            1.0 / self.mu, size=len(self.arrival_times)
        )

    def run(self) -> None:
        logger.info("Simulation started. It may take a while...")

        try:
            self.generate_arrivals()
            self.generate_services()
        except ValueError as e:
            logger.error(f"Invalid simulation parameters: {e}")
            raise 
        except ZeroDivisionError as e:
            logger.error("Division by zero while generating arrivals or services.")
            raise
        except Exception as e:
            logger.error(f"Unexpected error occured while generating arrivals or services: {e}")
            raise

        try:
            for arr, ser in zip(self.arrival_times, self.service_times):
                start, end, wait = self.server.process_customer(arr, ser)
                assert start > 0, "Start time must be a possitive number."
                assert end > 0, "End time must be a possitive number."
                assert wait >= 0, "Wait time must be a possitive number or at least zero."
                self.start_times.append(start)
                self.end_times.append(end)
                self.waiting_times.append(wait)
        except Exception as e:
            logger.error(f"Something went wrong while processing the queue simulation: {e}. Exiting event loop.")
            raise

        self.compute_statistics()

        logger.info("Simulation ended successfully.")

    def compute_statistics(self) -> None:
        self.Wq_sim = np.mean(self.waiting_times)

        time_grid = np.arange(0.0, self.T, self.dt)

        arrivals = np.searchsorted(self.arrival_times, time_grid, side="right")
        departures = np.searchsorted(self.end_times, time_grid, side="right")

        in_system = arrivals - departures
        in_queue = np.maximum(0, in_system - 1)

        self.L_sim = np.mean(in_system)
        self.Lq_sim = np.mean(in_queue)

        logger.info(f"Basic statistics have been determined.")

    def compare_with_theory(self) -> None:
        try:
            theory: dict[str, float] | None = self.compute(self.lambd, self.mu)
        except ZeroDivisionError:
            logger.error("Invalid parameters for theoretical results.")
            raise

        table: list[list[str]] = []

        if theory is None:
            logger.warning(
                "System is unstable (rho >= 1). "
                "Theoretical values will tend towards infinity."
            )
            table.append(["Wq", "Unknown", f"{self.Wq_sim:.2f}"])
            table.append(["L",  "Unknown", f"{self.L_sim:.2f}"])
            table.append(["Lq", "Unknown", f"{self.Lq_sim:.2f}"])
        else:
            table.append(["Wq", f"{theory['Wq']:.2f}", f"{self.Wq_sim:.2f}"])
            table.append(["L",  f"{theory['L']:.2f}",  f"{self.L_sim:.2f}"])
            table.append(["Lq", f"{theory['Lq']:.2f}", f"{self.Lq_sim:.2f}"])

        print(
            tabulate(
                table,
                headers=["Metric", "Theory", "Simulation"],
                tablefmt='pipe',
                stralign='center'
            )
        )
        print("\nLegend:")
        print("Wq - average waiting time")
        print("L - average number of customers in the system")
        print("Lq - average queue length")
    
    @staticmethod
    def compute(lambd: float, mu: float) -> dict[str, float] | None:
        if mu == 0:
            logger.warning("Mu parameter is equal to zero.")
            return None

        rho: float = lambd / mu
        if rho >= 1.0:
            logger.warning("Rho parameter exceeded the limit for stable simulation.")
            return None

        return {
            "Wq": rho / (mu - lambd),
            "L": rho / (1 - rho),
            "Lq": (rho ** 2) / (1 - rho)
        }

    def plot_queue_length(self) -> None:
        time_grid = np.arange(0.0, self.T, self.dt)
        arrivals = np.searchsorted(self.arrival_times, time_grid, side="right")
        departures = np.searchsorted(self.end_times, time_grid, side="right")
        in_queue = np.maximum(0, arrivals - departures - 1)

        plt.plot(time_grid, in_queue, 'k', linewidth=0.5, marker='o', markersize=1, linestyle='None')
        plt.xlabel("Time [s]")
        plt.ylabel("Queue length")
        plt.title("Queue length over time")
        plt.show()


def main() -> None:
    #sim = MM1Simulation(lambd=0.9, mu=0.5, time=100)
    sim = MM1Simulation(lambd=0.9, mu=2.1, time=500)
    #sim = MM1Simulation(lambd=0.9, mu=0.9, time=100)
    #sim = MM1Simulation(lambd=0.0, mu=0.0, time=100)
    #sim = MM1Simulation(lambd=1.0, mu=1.01, time=100)
    #sim = MM1Simulation(lambd=1.0, mu=2.0, time=-100)
    #sim = MM1Simulation(lambd=-1.0, mu=2.0, time=100)
    sim.run()
    sim.compare_with_theory()
    sim.plot_queue_length()


if __name__ == "__main__":
    logging.basicConfig(filename='queue.log', level=logging.INFO)
    main()
