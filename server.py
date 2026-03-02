class QueueServer:
    def __init__(self):
        self.free_at: float = 0.0

    def process_customer(self, arrival_time: float, service_time: float) -> tuple[float, float, float]:
        assert arrival_time > 0, "Arrival time cannot be a negative number or zero."
        assert service_time > 0, "Service time cannot be a negative number or zero."
        start: float = max(self.free_at, arrival_time)
        end: float = start + service_time
        waiting: float = start - arrival_time
        self.free_at = end
        return start, end, waiting