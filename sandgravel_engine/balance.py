from dataclasses import dataclass, field
from typing import Callable, Optional
from .models import MaterialStream, SizeDistribution, BalanceResult, EquipmentSelection


@dataclass
class ProcessNode:
    """Process flow node"""
    name: str
    node_type: str  # "crusher", "screen", "splitter", "sink"
    params: dict = field(default_factory=dict)


@dataclass
class FlowConfig:
    """Process flow configuration"""
    nodes: list[ProcessNode]
    edges: list[tuple[str, str]]  # (from_node, to_node)
    recirculation_edges: list[tuple[str, str]] = field(default_factory=list)


class ConvergenceError(Exception):
    """Balance calculation did not converge"""
    pass


class BalanceEngine:
    """Material balance engine for aggregate processing flow"""

    def __init__(self, max_iterations: int = 100, tolerance: float = 1e-4):
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self._processors: dict[str, Callable] = {}

    def register_processor(self, node_type: str, processor: Callable[[MaterialStream], MaterialStream]):
        """Register a process function for a node type"""
        self._processors[node_type] = processor

    def solve(self, feed: MaterialStream, config: FlowConfig) -> BalanceResult:
        """Execute material balance calculation on a process flow DAG"""
        streams: dict[str, MaterialStream] = {"feed": feed}
        equipment: list[EquipmentSelection] = []

        for node in config.nodes:
            streams[node.name] = MaterialStream(name=node.name, tonnage=0.0)

        # Build node lookup for processor dispatch
        node_map = {n.name: n for n in config.nodes}

        iterations = 0
        prev_total: Optional[float] = None

        while iterations < self.max_iterations:
            for node in config.nodes:
                streams[node.name] = MaterialStream(name=node.name, tonnage=0.0)

            for from_node, to_node in config.edges + config.recirculation_edges:
                if from_node not in streams or streams[from_node].tonnage <= 0:
                    continue

                material = streams[from_node]

                # Apply processor if the source node has a registered type
                if from_node in node_map:
                    processor = self._processors.get(node_map[from_node].node_type)
                    if processor:
                        material = processor(material)
                        material.name = f"{from_node}_processed"

                streams[to_node] = MaterialStream(
                    name=streams[to_node].name,
                    tonnage=streams[to_node].tonnage + material.tonnage,
                    grading=material.grading,
                )

            total_flow = sum(s.tonnage for s in streams.values() if s.name != "feed")
            if prev_total is None:
                error = float("inf")
            else:
                error = abs(total_flow - prev_total)
                if error < self.tolerance:
                    break

            prev_total = total_flow
            iterations += 1

        return BalanceResult(
            streams=streams,
            equipment=equipment,
            iterations=iterations + 1,
            convergence_error=error if iterations > 0 else 0.0,
        )


class RecirculationSolver:
    """Iterative solver for closed-circuit recirculation"""

    def __init__(self, max_iter: int = 100, tol: float = 1e-4):
        self.max_iter = max_iter
        self.tol = tol

    def solve(self, initial_feed: MaterialStream,
              process_fn: Callable[[MaterialStream], MaterialStream],
              recirc_fn: Callable[[MaterialStream], MaterialStream],
              recirc_ratio_fn: Callable[[MaterialStream], float]) -> BalanceResult:
        """Solve closed-circuit recirculation iteratively"""
        current_feed = initial_feed
        prev_tonnage = current_feed.tonnage
        error = float("inf")

        for i in range(self.max_iter):
            product = process_fn(current_feed)
            recirc_ratio = recirc_ratio_fn(product)
            recirc = MaterialStream(
                name=f"recirc_{i}",
                tonnage=product.tonnage * recirc_ratio,
                grading=product.grading,
            )
            recirc_processed = recirc_fn(recirc)

            total_tonnage = initial_feed.tonnage + recirc_processed.tonnage
            # Blend fresh feed grading with recirculated grading proportionally
            w_fresh = initial_feed.tonnage / total_tonnage
            w_recirc = recirc_processed.tonnage / total_tonnage
            blended_grading = initial_feed.grading * w_fresh + recirc_processed.grading * w_recirc

            next_feed = MaterialStream(
                name=f"feed_iter_{i}",
                tonnage=total_tonnage,
                grading=blended_grading,
            )

            error = abs(next_feed.tonnage - prev_tonnage)
            if error < self.tol:
                return BalanceResult(
                    streams={"feed": next_feed, "product": product, "recirc": recirc},
                    equipment=[],
                    iterations=i + 1,
                    convergence_error=error,
                )

            current_feed = next_feed
            prev_tonnage = next_feed.tonnage

        raise ConvergenceError(
            f"Failed to converge within {self.max_iter} iterations, current error={error:.6f}"
        )
