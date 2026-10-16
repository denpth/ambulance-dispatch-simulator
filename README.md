# Priority-Aware Ambulance Dispatch Simulator

## Project context

Developed during Western Governors University coursework. This repository is a record of my implementation and learning, not a client engagement, deployed operational system, or claim of a new algorithm. Supplied requirements, starter components, datasets, and third-party libraries are distinct from my own implementation. Where their exact provenance or redistribution terms have not been established, they are not represented as my original work or as cleared for public release.


A Python dispatch simulation that prioritizes emergency calls, evaluates travel paths through a weighted location network, and assigns the ambulance with the lowest calculated travel time to each incident.

## What it demonstrates

- Graph modeling with adjacency lists
- Bellman-Ford shortest-path routing
- Priority-based emergency-call processing
- CSV-backed data ingestion and dispatch logging
- Runtime measurement for route-calculation performance
- Deterministic assignment logic based on call priority, call order, and travel time

## How it works

The program loads ambulance staging locations, emergency calls, call-priority definitions, and a weighted road network from CSV files. Calls are ordered by priority and then by call ID. For each call, the application evaluates the route from every ambulance staging location and selects the ambulance with the shortest computed travel time.

Travel cost includes both base travel time and modeled traffic delay. The selected route and dispatch decision are written to an output log for later analysis.

## Project structure

- `dispatch.py` — dispatch pipeline and Bellman-Ford implementation
- `ambulance.csv` — ambulance identifiers and staging locations
- `call_priority.csv` — call types and assigned priorities
- `calls.csv` — emergency-call workload
- `location_network.csv` — directed network edges, travel times, and traffic delays
- `ambulance_call_priority.csv` — generated dispatch output

## Running the simulator

```bash
python dispatch.py
```

The script processes calls in priority order, selects the fastest route candidate, records the route and travel time, and prints the aggregate route-calculation processing time.

## Algorithmic notes

Bellman-Ford is used to compute shortest paths across the network. For each emergency call, the algorithm is run from each ambulance staging location to the call location, making the project a useful demonstration of applying graph algorithms to an operational dispatch problem rather than an isolated textbook example.

## October 2026 routing comparison

`compare_routes.py` compares the existing Bellman–Ford function with Dijkstra on independently generated, nonnegative directed graphs. The existing dispatch policy is unchanged. Three workloads vary graph size and the number of candidate-ambulance/incident route queries. Costs must agree before timing; repeated timings alternate algorithm order and report every run plus median/range. The comparison includes function overhead and is not an end-to-end dispatch or emergency-response validation.

Run `python -m unittest discover -s tests`, then `python compare_routes.py --output routing-comparison.json`. Requires pandas for the existing `dispatch.py` import. A recorded run is in `results/routing-comparison.json`; timings describe that local run only.

## Public portfolio release

This is a publication copy of my WGU coursework implementation and subsequent revisions. The original development history is retained privately. Assessment documents, student identifiers, and training-data snapshots are excluded from this public history. Notebook outputs are cleared; recorded evaluation artifacts are retained separately where available. The academic origin and third-party dependencies remain attributed.

The top-level dispatch CSVs are a new, small synthetic demonstration. Their output is not the historical dispatch run or the separately recorded shortest-path benchmark.
