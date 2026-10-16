"""Synthetic routing-kernel comparison, not a dispatch effectiveness study."""
import argparse
import heapq
import json
import math
import platform
import random
import statistics
from pathlib import Path
from time import perf_counter
from dispatch import bellman_ford


def dijkstra(graph,start,end):
    if any(weight<0 for edges in graph.values() for _,weight in edges):
        raise ValueError('Dijkstra comparison requires nonnegative edge weights')
    dist={start:0.};prev={start:None};queue=[(0.,start)]
    while queue:
        cost,node=heapq.heappop(queue)
        if cost!=dist[node]:continue
        if node==end:
            path=[]
            while node is not None:path.append(node);node=prev[node]
            return cost,path[::-1]
        for nxt,weight in graph.get(node,[]):
            value=cost+weight
            if value<dist.get(nxt,math.inf):
                dist[nxt]=value;prev[nxt]=node;heapq.heappush(queue,(value,nxt))
    return math.inf,[]


def workload(nodes,ambulances,incidents,seed):
    rng=random.Random(seed);graph={str(i):[] for i in range(nodes)}
    # Directed ring guarantees reachability; random edges add route alternatives.
    for i in range(nodes):
        destinations={(i+1)%nodes}
        destinations.update(rng.randrange(nodes) for _ in range(3))
        graph[str(i)]=[(str(j),float(rng.randint(1,30))) for j in sorted(destinations) if j!=i]
    origins=[str(rng.randrange(nodes)) for _ in range(ambulances)]
    calls=[str(rng.randrange(nodes)) for _ in range(incidents)]
    return graph,[(origin,call) for call in calls for origin in origins]


def compare(repeats=5):
    rows=[]
    for nodes,ambulances,incidents in [(50,4,10),(150,8,20),(400,12,30)]:
        graph,pairs=workload(nodes,ambulances,incidents,42)
        reference=[bellman_ford(graph,a,b)[0] for a,b in pairs]
        alternative=[dijkstra(graph,a,b)[0] for a,b in pairs]
        if reference!=alternative:raise AssertionError('Route costs differ')
        elapsed={name:[] for name in ['bellman_ford','dijkstra']}
        # Warm once above, alternate timed algorithm order to reduce ordering bias.
        for repeat in range(repeats):
            names=['bellman_ford','dijkstra'] if repeat%2==0 else ['dijkstra','bellman_ford']
            for name in names:
                function=bellman_ford if name=='bellman_ford' else dijkstra
                start=perf_counter()
                for a,b in pairs:function(graph,a,b)
                elapsed[name].append((perf_counter()-start)*1000)
        rows.append({'nodes':nodes,'edges':sum(map(len,graph.values())),'candidate_ambulances':ambulances,'incidents':incidents,'route_queries':len(pairs),'equal_shortest_path_costs':True,
            'timing_ms':{name:{'runs':values,'median':statistics.median(values),'minimum':min(values),'maximum':max(values)} for name,values in elapsed.items()}})
    return {'evaluation_date':'2026-10-15','seed':42,'python':platform.python_version(),'system':platform.system(),'machine':platform.machine(),'repeats':repeats,'workloads':rows,'scope':'Synthetic nonnegative graphs. Timing covers complete route-function calls, including Dijkstra weight validation. Candidate ambulance and incident counts only determine query volume; no priority, availability, reassignment, patient outcome, or end-to-end dispatch policy is evaluated. Equal cost does not require equal paths when ties exist. Warm local timing is not a production latency guarantee.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--repeats',type=int,default=5);args=parser.parse_args()
    if args.output.exists():parser.error('Refusing to overwrite report')
    if args.repeats<2:parser.error('At least two repeats required')
    args.output.write_text(json.dumps(compare(args.repeats),indent=2)+'\n');print(args.output)
