from typing import List, Dict

import networkx as nx
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt, animation

from RailywayStation import RailwayStation
from Train import get_berth_availability
from Train import Train


class Route:
    def __init__(self, route_id: int, stations: List[int], distance: float, travel_time: float, train_id: int):
        self.route_id = route_id
        self.stations = stations
        self.distance = distance
        self.travel_time = travel_time
        self.train_id = train_id

def create_railway_graph(stations: Dict[int, RailwayStation], routes: List[Route]) -> nx.Graph:
    graph = nx.Graph()
    for station_id, station in stations.items():
        graph.add_node(station_id, name=station.name, pos=(station.x, station.y))
    for route in routes:
        u_id, v_id = route.stations[0], route.stations[1]
        graph.add_edge(u_id, v_id, distance=route.distance, travel_time=route.travel_time, train_id=route.train_id)
    nx.draw(graph,with_labels=True, node_size=1500, node_color="skyblue", font_size=15, font_weight="bold")
    plt.savefig("static/TrainRouteGraph.png", bbox_inches='tight')
    return graph

def find_path_with_berth_animation(graph: nx.Graph, stations: Dict[int, RailwayStation], trains: Dict[int, Train],
                                   start_node_id: int, end_node_id: int, date: str):
    shortest_path = None
    visited = set()
    queue = [(start_node_id, [start_node_id], 0)]  # (current_node, path, total_distance)
    path_history = []

    fig, ax = plt.subplots(figsize=(8, 6))
    pos = nx.get_node_attributes(graph, 'pos')

    def update(frame):
        ax.clear()
        nx.draw(graph, pos, with_labels=True, node_color='lightblue', node_size=800, font_size=8, ax=ax)
        nx.draw_networkx_nodes(graph, pos, nodelist=[start_node_id], node_color='green', node_size=800, ax=ax)
        nx.draw_networkx_nodes(graph, pos, nodelist=[end_node_id], node_color='red', node_size=800, ax=ax)

        if frame < len(path_history):
            path, distance = path_history[frame]
            path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
            nx.draw_networkx_edges(graph, pos, edgelist=path_edges, edge_color='blue', width=2, ax=ax)
            ax.set_title(f"Searching... Distance: {distance:.2f}")
        elif shortest_path:
            path, distance = shortest_path
            path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
            nx.draw_networkx_edges(graph, pos, edgelist=path_edges, edge_color='green', width=3, ax=ax)
            ax.set_title(f"Shortest Path Found! Distance: {distance:.2f}")
        else:
            ax.set_title("Searching...")

        return ax

    while queue:
        current_node, path, current_distance = queue.pop(0)
        if current_node == end_node_id:
            shortest_path = (path, current_distance)
            break
        visited.add(current_node)
        path_history.append((list(path), current_distance))  # Store path for animation

        for neighbor in graph.neighbors(current_node):
            if neighbor not in visited:
                weight = graph[current_node][neighbor].get('distance', float('inf'))
                train_id = graph[current_node][neighbor].get('train_id')
                if train_id and get_berth_availability(trains, train_id, date) > 0:
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append((neighbor, new_path, current_distance + weight))
                elif train_id is None:  # Allow traversal if no specific train is associated (for graph exploration)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append((neighbor, new_path, current_distance + weight))

    ani = animation.FuncAnimation(fig, update, frames=len(path_history) + 5, interval=5, repeat_delay=100, blit=False)
    ani.save('static/MyRouting.mp4', writer='ffmpeg', fps=30)
    # plt.show()

    return shortest_path
