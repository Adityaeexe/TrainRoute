import json
import re

import pandas as pd

from flask import Flask, request, render_template, redirect, url_for

from typing import Dict, List, Optional, Tuple

from RailywayStation import RailwayStation

from Train import Train

from Route import Route, create_railway_graph, find_path_with_berth_animation

app = Flask(__name__)
app.secret_key = "MySecret"
ctx = app.app_context()
ctx.push()

with ctx:
    pass
user_id = ""
emailid = ""

message = ""
msgType = ""
uploaded_file_name = ""


def initialize():
    global message, msgType
    message = ""
    msgType = ""


@app.route("/")
def index():
    global user_id, emailid
    return render_template("Login.html")


@app.route("/processLogin", methods=["POST"])
def processLogin():
    global user_id, emailid
    emailid = request.form["emailid"]
    password = request.form["password"]
    sdf = pd.read_csv("static/System.csv")
    for k, v in sdf.iterrows():
        if v['emailid'] == emailid and str(v['password']) == password:
            return render_template("Dashboard.html")
    return render_template("Login.html", processResult="Invalid UserID and Password")


@app.route("/Dashboard")
def Dashboard():
    global user_id, emailid
    return render_template("Dashboard.html")


@app.route("/Information")
def Information():
    global message, msgType
    return render_template("Information.html", msgType=msgType, message=message)


station_df = pd.read_csv('static/stations.csv').set_index("key")
train_df = pd.read_csv('static/Train.csv').set_index("key")
route_df = pd.read_csv('static/Route.csv')
route_df["route_id"] = route_df["route_id"].astype("int32")
route_df["from_station_id"] = route_df["from_station_id"].astype("int32")
route_df["to_station_id"] = route_df["to_station_id"].astype("int32")
route_df["train_id"] = route_df["train_id"].astype("int32")
print(route_df.info())


@app.route("/ShowDataset")
def ShowDataset():
    return render_template("ShowDataset.html", displayResult=False)


@app.route("/ProcessShowDataset", methods=['POST'])
def process_ShowDataset():
    return render_template("ShowDataset.html", displayResult=True, station_df=station_df, train_df=train_df,
                           route_df=route_df)


@app.route("/OptimizeTrainRoute")
def OptimizeTrainRoute():
    return render_template("OptimizeTrainRoute.html", displayResult=False, train_df=train_df, station_df=station_df)


@app.route("/ProcessOptimizeTrainRoute", methods=['POST'])
def process_OptimizeTrainRoute():
    stations_data = {}

    for key, value in station_df.T.to_dict().items():
        stations_data[key] = RailwayStation(**value)

    trains_data = {}
    for key, value in train_df.T.to_dict().items():
        trains_data[key] = Train(**value)

    route_df = pd.read_csv('static/Route.csv')
    routes_data = []
    for key, value in route_df.iterrows():
        stations = [value['from_station_id'], value['to_station_id']]
        routes_data.append(
            Route(value['route_id'], stations, value['distance'], value['travel_time'], value['train_id'], ))



    travel_date = request.form["travelDate"]
    availability_dict = {}
    for key, row in train_df.iterrows():
        v = request.form[f"availability{key}"]
        trains_data[key].availability[travel_date] = int(v)
    rail_graph = create_railway_graph(stations_data, routes_data)

    start_station_name = request.form['fromStation']
    start_node_id = [s.station_id for s in stations_data.values() if s.name == start_station_name][0]
    end_station_name = request.form['toStation']
    end_node_id = [s.station_id for s in stations_data.values() if s.name == end_station_name][0]

    shortest_path = find_path_with_berth_animation(rail_graph, stations_data, trains_data, start_node_id, end_node_id,
                                                   travel_date)
    msg = ""
    msg2 = ""
    if shortest_path:
        path_nodes, distance = shortest_path
        path_names = [stations_data[node_id].name for node_id in path_nodes]
        msg = f"\nShortest Path with Berth Availability from {start_station_name} to {end_station_name} on {travel_date}: {path_names}"
        msg2 = f"Total Distance: <b>{distance:.2f} km</b>"
    else:
        msg = f"\nNo path found with available berths from {start_station_name} to {end_station_name} on {travel_date}."
    return render_template("OptimizeTrainRoute.html", displayResult=True, train_df=train_df, station_df=station_df, msg=msg, msg2=msg2)


if __name__ == "__main__":
    app.run()
