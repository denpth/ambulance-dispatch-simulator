import csv
import heapq
from collections import defaultdict
from time import perf_counter

import pandas as pd

"""
This program implements an ambulance dispatch program that takes the following steps:
1. Read the required CSV files into memory for processing.
2. Process ambulance locations, call priorities, network data, and emergency calls.
3. Establishes a call priority queue for dispatching ambulances based on priority code and order recieved.

The program uses CSV files for input data and implements a priority-based dispatch system.
"""

# File path constants
AMB_FILE = "ambulance.csv"  # CSV file containing ambulance information and staging locations
CALL_PRI_FILE = "call_priority.csv"  # CSV file containing call types and their priority levels
CALLS_FILE = "calls.csv"  # CSV file containing emergency call information
NETWORK_FILE = "location_network.csv"  # CSV file containing the network of locations and travel times
LOG_FILE = "ambulance_call_priority.csv"  # Output file for logging ambulance dispatch details

def read_ambulance_data():
    """
    Reads ambulance data from the ambulance CSV file.

    Returns:
        dict: A dictionary mapping ambulance numbers to their staging locations.
    """
    ambulances = {}
    with open(AMB_FILE, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ambulances[row['Ambulance Number']] = row['Staging Location']
    return ambulances

def read_call_priority_data():
    """
    Reads call priority data from the call priority CSV file.

    Returns:
        dict: A dictionary mapping call types to their priority levels.
    """
    priorities  = {}
    with open(CALL_PRI_FILE, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            priorities[row['Call Type']] = row['Priority']
    return priorities

def read_network_data():
    """
    Reads location network data from the network CSV file.

    Returns:
        defaultdict: A graph representation of the location network where keys are starting locations
                    and values are lists of tuples containing (destination, travel_time).
                    Travel time includes both base travel time and traffic delay.
    """
    network = defaultdict(list)
    with open(NETWORK_FILE, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            time = float(row['Travel Time']) + float(row['Traffic Delay'])
            network[row['Start']].append((row['End'], time))
    return network

def read_calls(priorities):    
    """
    Reads emergency call data from the calls CSV file and assigns priorities.

    Args:
        priorities (dict): A dictionary mapping call types to priority levels.

    Returns:
        list: A list of dictionaries representing emergency calls, sorted by priority
              and then by Call ID. Each dictionary contains Call ID, Call Type,
              Location, and Priority.
    """
    calls = []
    with open(CALLS_FILE, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            priority = priorities.get(row['Call Type'], 99) 
            calls.append({
                'Call ID': int(row['Call ID']), # Changed to int to avoid String Sort
                'Call Type': row['Call Type'],
                'Location': row['Location'],
                'Priority': priority,
            })
    calls.sort(key=lambda r: (r['Priority'], r['Call ID']))
    return calls

def bellman_ford(graph, start, end):
    """
    Implements the Bellman-Ford algorithm to find the shortest path between two locations.

    Unlike Dijkstra's algorithm, Bellman-Ford can handle graphs with negative edge weights
    (though this implementation doesn't check for negative cycles).

    Args:
        graph (defaultdict): A graph representation of the location network.
        start (str): The starting location.
        end (str): The destination location.

    Returns:
        tuple: A tuple containing:
            - float: The total cost (travel time) to reach the destination.
            - list: The path from start to end as a list of locations.
              Returns (float('inf'), []) if no path is found.
    """
    # Initialize distances dictionary with infinity for all nodes except the start node
    # The distance to the start node is 0 (no cost to reach itself)
    dist = {start: 0.0}

    # Initialize predecessors dictionary to track the optimal path
    # The start node has no predecessor (it's the origin)
    pred = {start: None}

    # Get all vertices in the graph to iterate through them
    vertices = list(graph.keys())

    # Main Bellman-Ford relaxation loop
    # We need at most |V|-1 iterations to find shortest paths in a graph with |V| vertices
    # This is because the longest possible simple path has |V|-1 edges
    for _ in range(len(vertices) - 1):
        updated = False  # Flag to track if any distance was updated in this iteration

        # Iterate through all vertices that have a known distance
        for u in vertices:
            if u not in dist:
                continue  # Skip vertices we haven't reached yet

            # For each vertex, examine all its outgoing edges
            for v, w in graph.get(u, []):
                # Calculate potential new distance to neighbor v through current vertex u
                new_cost = dist[u] + w

                # If we found a shorter path to v, update its distance and predecessor
                if v not in dist or new_cost < dist[v]:
                    dist[v] = new_cost  # Update the shortest distance
                    pred[v] = u  # Update the predecessor in the shortest path
                    updated = True  # Mark that we made an update

        # Optimization: if no distances were updated in this iteration,
        # we can terminate early as no further improvements are possible
        if not updated:
            break

    # If the destination is not in our distance dictionary, it's unreachable
    if end not in dist:
        return float('inf'), []  # Return infinity cost and empty path

    # Reconstruct the shortest path by working backwards from the destination
    path = []
    node = end
    while node is not None:
        path.append(node)  # Add current node to the path
        node = pred.get(node)  # Move to the predecessor

    # Reverse the path to get it in the correct order (start to end)
    path.reverse()

    # Return the total cost to the destination and the complete path
    return dist[end], path

def dispatch_ambulances():
    """
    Main function that coordinates the ambulance dispatch process.

    This function:
    1. Loads ambulance location data
    2. Loads network data for travel times
    3. Loads call priority data
    4. Loads and prioritizes emergency calls

    The actual dispatch logic will be implemented here to assign ambulances
    to emergency calls based on location, priority, and travel time.
    """
    # Load all necessary data from CSV files
    ambulances = read_ambulance_data()
    network = read_network_data()
    priorities = read_call_priority_data()
    calls = read_calls(priorities)  # Calls are already sorted by priority and call ID
    total_processing_time = 0.0 # Variable to show total time required for actual route calculation algorithm
    # Process each call in priority order
    for call in calls:

        # Initialize variables to track the fastest ambulance
        fastest = None  # Best travel time found so far
        fastest_record = None  # Tuple of (ambulance_id, route) for the fastest ambulance
        start_time = perf_counter() * 1000 #Record start time for performance measurement
        # Find the ambulance with the shortest travel time to the call location
        for ambulance, staging in ambulances.items():
            # Calculate travel time and route from ambulance staging location to call location
            time_to_call, route = bellman_ford(network, staging, call['Location'])

            # Update if this is the first ambulance checked or if it's faster than previous best
            if fastest is None or time_to_call < fastest:
                fastest = time_to_call
                fastest_record = (ambulance, route)

        # Skip if no valid route was found for any ambulance
        if fastest_record is None:
            continue
        total_processing_time += perf_counter() * 1000 - start_time #Record total time required for actual route calculation algorithm
        # Extract the fastest ambulance and its route
        amb, route = fastest_record

        # Create a record of the dispatch decision
        record = {
            'Call ID': int(call['Call ID']),
            'Call Type': call['Call Type'],
            'Call Location': call['Location'],
            'Ambulance': amb,
            'Route to Call Location': '->'.join(route),  # Format route as a string with arrows
            'Time to the Call Location': f"{fastest:.2f}"  # Format time with 2 decimal places
        }

        # Format the record as a comma-separated string of key-value pairs
        log_entry = ','.join([f"{k}:{v}" for k, v in record.items()])

        # Append the dispatch record to the log file
        with open(LOG_FILE, 'a') as file:
            file.write(log_entry + '\n')
    print (f"Total processing time: {total_processing_time:.3f} ms") #Print total time required for actual route calculation algorithm

# Entry point of the program when run as a script
if __name__=="__main__":
    dispatch_ambulances()
