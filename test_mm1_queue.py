import unittest
import mm1_queue
import server

class TestDiffusion(unittest.TestCase):

    def test_lambd_minus(self):
        with self.assertRaises(AssertionError):
            mm1_queue.MM1Simulation(lambd=-1.0, mu=2.0, time=100).run()
    def test_time_minus(self):
        with self.assertRaises(AssertionError):
            mm1_queue.MM1Simulation(lambd=1.0, mu=2.0, time=-500).run()
    def test_arrival_zero(self):
        queue_server = server.QueueServer()
        with self.assertRaises(AssertionError):
            queue_server.process_customer(arrival_time=0.0, service_time=1.0)

if __name__ == '__main__':
    unittest.main()