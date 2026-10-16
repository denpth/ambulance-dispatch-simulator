import math
import unittest
from compare_routes import dijkstra,workload
from dispatch import bellman_ford

class RoutingComparisonTests(unittest.TestCase):
    def test_same_minimum_cost_for_all_pairs(self):
        graph,_=workload(18,2,2,17)
        for source in graph:
            for destination in graph:
                expected,path=bellman_ford(graph,source,destination)
                actual,route=dijkstra(graph,source,destination)
                self.assertEqual(actual,expected)
                self.assertEqual(route[0],source);self.assertEqual(route[-1],destination)
                cost=sum(next(w for v,w in graph[a] if v==b) for a,b in zip(route,route[1:]))
                self.assertEqual(cost,actual)
    def test_unreachable_zero_and_negative(self):
        self.assertEqual(dijkstra({'a':[],'b':[]},'a','b'),(math.inf,[]))
        self.assertEqual(dijkstra({'a':[]},'a','a'),(0.,['a']))
        with self.assertRaises(ValueError):dijkstra({'a':[('b',-1)]},'a','b')

if __name__=='__main__':unittest.main()
