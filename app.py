# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
# reflect the tables
# Save references to each table
# Create our session (link) from Python to the DB
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)



#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    return (
        f"Welcome to the Flask API for Hawaii Climate Analysis!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - Precipitation data for the last year<br/>"
        f"/api/v1.0/stations - List of weather stations<br/>"
        f"/api/v1.0/tobs - Temperature observations for the last year<br/>"
        f"/api/v1.0/start_date - Min, Max, and Avg temperatures from a given start date<br/>"
        f"/api/v1.0/start_date/end_date - Min, Max, and Avg temperatures within a date range"
    )
@app.route('/api/v1.0/precipitation')
def precipitation():
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=366)
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

@app.route('/api/v1.0/stations')
def stations():
    
    results = session.query(Station.station, Station.name).all()
    station_list = []
    for station, name in results:
        station_dict = {
            'station': station,
            'name': name
        }
        station_list.append(station_dict)

    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs():
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=366)
    active_stations = session.query(Measurement.station,\
    func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()
    active_stations
    most_active_station = active_stations[0][0]
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()
    tobs_data = {date: tobs for date, tobs in results}

    return jsonify(tobs_data)

@app.route('/api/v1.0/<start>')
def temp_stats_start(start):
    
    temperature_stats = session.query(func.min(Measurement.tobs),
                                      func.max(Measurement.tobs),
                                      func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()

    temp_stats = {
        'start_date': start,
        'min_temp': temperature_stats[0][0],
        'max_temp': temperature_stats[0][1],
        'avg_temp': temperature_stats[0][2]
    }

    return jsonify(temp_stats)


@app.route('/api/v1.0/<start>/<end>')
def temp_stats_range(start, end):
    
    temperature_stats = session.query(func.min(Measurement.tobs),
                                      func.max(Measurement.tobs),
                                      func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    temp_stats = {
        'start_date': start,
        'end_date': end,
        'min_temp': temperature_stats[0][0],
        'max_temp': temperature_stats[0][1],
        'avg_temp': temperature_stats[0][2]
    }

    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)