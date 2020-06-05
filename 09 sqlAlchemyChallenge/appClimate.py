import sqlalchemy
from datetime import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import pandas as pd
import datetime as dt

# Database Setup

engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup

app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/finish_date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of last 12 months data for precipitation"""
    # Find query date
    max_date = pd.read_sql("select * from Measurement order by date desc",engine)['date'][:1][0]
    max_date = datetime.strptime(max_date,'%Y-%m-%d')
    query_date = max_date - dt.timedelta(days=365)
    query_date = query_date.strftime('%Y-%m-%d')    
    
    # Query
    results = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= query_date).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_dates
    all_dates = []
    for date, prcp in results:
        dates_dict = {}
        dates_dict["date"] = date
        dates_dict["prcp"] = prcp
        all_dates.append(dates_dict)

    return jsonify(all_dates)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of available stations"""  
    # Query
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for station, name, latitude, longitude, elevation in results:
        stations_dict = {}
        stations_dict["station"] = station
        stations_dict["name"] = name
        stations_dict["latitude"] = latitude
        stations_dict["longitude"] = longitude
        stations_dict["elevation"] = elevation
        all_stations.append(stations_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of last 12 months data for temperature for the most active station"""  
     # Find query date
    max_date = pd.read_sql("select * from Measurement order by date desc",engine)['date'][:1][0]
    max_date = datetime.strptime(max_date,'%Y-%m-%d')
    query_date = max_date - dt.timedelta(days=365)
    query_date = query_date.strftime('%Y-%m-%d')

    # Query
    results = session.query(Measurement.date, Measurement.tobs)\
    .filter(Measurement.station == 'USC00519281')\
    .filter(Measurement.date >= query_date).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_tobs
    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a min, max and avg temperature for a given space of time"""  
    # Query
    results = session.query(func.max(Measurement.tobs).label("max_score"),
                func.min(Measurement.tobs).label("min_score"),
                func.avg(Measurement.tobs).label("avg_score")
                ).filter(Measurement.date >= start)
    session.close()

    # Create a dictionary from the row data and append to a list of all_tobs
    res = results.one()
    max = res.max_score
    min = res.min_score
    avg = res.avg_score

    start = ({
        
        'min':min,
        'max':max,
        'avg':avg

    })

    return jsonify(start)

@app.route("/api/v1.0/<start>/<finish>")
def start_finish(start,finish):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a min, max and avg temperature for a given space of time"""  
    # Query
    results = session.query(func.max(Measurement.tobs).label("max_score"),
                func.min(Measurement.tobs).label("min_score"),
                func.avg(Measurement.tobs).label("avg_score")
                ).filter(Measurement.date >= start).filter(Measurement.date <= finish)
    session.close()

    # Create a dictionary from the row data and append to a list of all_tobs
    res = results.one()
    max = res.max_score
    min = res.min_score
    avg = res.avg_score

    start = ({
        
        'min':min,
        'max':max,
        'avg':avg

    })

    return jsonify(start)

if __name__ == '__main__':
    app.run(debug=True)
