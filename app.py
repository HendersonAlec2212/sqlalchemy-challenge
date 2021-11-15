from flask import Flask, jsonify

import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

##############################################################
# Notes_development:
#
# follow database creation
# pull info from ipynb
# close session after data pull per route
# fancy formatting:
# return jsonify(list_label=list)

# remember that each route must have all aspects needed for query
# this wont be executing like JPNB

# track routes for home page (do that last)
# consider method of combining last two routes
##############################################################

###############################
# Database Setup
###############################

hawaii_sqlite = 'resources\\hawaii.sqlite'
# create engine to hawaii.sqlite
engine = create_engine(f"sqlite:///{hawaii_sqlite}")
# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# save references for each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# create session
session = Session(engine)

###############################
# Flask setup
###############################
app = Flask(__name__)


###############################
# Flask Routes
###############################

@app.route("/")
def home():
    return(
        # f"</br>"
        f"Welcome to the Hawaii Temperature analysis API</br>"
        f"</br>"
        f"Return the precipitation data for the last year.</br>"
        f"/api/v1.0/precipitation</br>"
        f"</br>"
        f"Return list of stations.</br>"
        f"/api/v1.0/stations</br>"
        f"</br>"
        f"Return the Temperature Observations (TOBS) for the past year.</br>"
        f"/api/v1.0/tobs</br>"
        f"</br>"
        f"Return TempMIN, TempMAX, AND TempAVG of input date.</br>"
        f"/api/v1.0/temp_data/<start></br>"
        f"</br>"
        f"Return TempMIN, TempMAX, AND TempAVG of input dates.</br>"
        f"/api/v1.0/temp_data_between/<start><end></br>"
        
        f"================</br>"
        f"Date Formatting:</br>"
        f"----------------</br>"
        f"</br>"
        f"Example Date: 03-04-2010</br>"
        f"/api/v1.0/temp_data/03042010</br>"
        f"</br>"
        f"Example Date: 03-04-2010 & 04-05-2010</br>"
        f"/api/v1.0/temp_data_between/start/end</br>"
        f"/api/v1.0/temp_data_between/03042010/04052010</br>"
        f"================</br>"


    )


@app.route("/api/v1.0/precipitation")
def precip():
    """retrieve the precipitation data for the past year"""
    # Calculate the date one year from the last date in data set.

    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precip_q = session.query(Measurement.date, Measurement.prcp) \
        .filter(Measurement.date >= year_ago).all()

    session.close()
# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

# precip_q exists as a list of tuples, use dict() to convert to dictionary
    precip = dict(precip_q)
    return jsonify(precipitation=precip)

@app.route("/api/v1.0/stations")
def stations():
    """return a list of stations"""
    station_q = session.query(Station.station).all()

    session.close()
    # Return a JSON list of stations from the dataset
    # use list(np.ravel(list_var))
    stations = list(np.ravel(station_q))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """return temperature observations (tobs) for previous year"""
    # Query the dates and temperature observations of the most active station for the last year of data.
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # query the most active station
    active_station_list = session.query(Measurement.station, func.count(Measurement.station)) \
        .group_by(Measurement.station) \
        .order_by(func.count(Measurement.station) \
        .desc()).all()

    # whittle down to just the station ID
    most_act_station = active_station_list[0][0]

    # use variable as station ID in case dynamic data
    tobs_past_year = session.query(Measurement.tobs)\
    .filter(Measurement.station == most_act_station)\
    .filter(Measurement.date >= year_ago).all()

    session.close()
    # Return a JSON list of temperature observations (TOBS) for the previous year.
    tobs_list = list(np.ravel(tobs_past_year))
    return jsonify(temp_obvs=tobs_list)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature
# for a given start or start-end range.

# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal
# to the start date.

# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the
# start and end date inclusive.

@app.route("/api/v1.0/temp_data/<start>")
def start_only(start):
    """return TMIN, TMAX, AND TAVG of input date"""
    #select statement
    sel = [func.min(Measurement.tobs),
           func.max(Measurement.tobs),
           func.avg(Measurement.tobs)]

    # data query
    start = dt.datetime.strptime(start.replace(" ", ""), "%m%d%Y")
    date_query = session.query(*sel). \
        filter(Measurement.date >= start).all()

    session.close()

    # return json list
    temps = list(np.ravel(date_query))
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp_data_between/<start>/<end>")
def start_end(start, end):
    """return TMIN, TMAX, AND TAVG between input dates"""
    #select statement
    sel = [func.min(Measurement.tobs),
           func.max(Measurement.tobs),
           func.avg(Measurement.tobs)]

    # create variables to hold start and end dates, strip as needed
    start = dt.datetime.strptime(start.replace(" ", ""), "%m%d%Y")
    end = dt.datetime.strptime(end.replace(" ", ""), "%m%d%Y")

    # data query, inclusive - >= start, <= end
    date_query = session.query(*sel) \
        .filter(Measurement.date >= start)\
        .filter(Measurement.date <= end).all()

    session.close()

    # return json list
    temps = list(np.ravel(date_query))
    return jsonify(temps=temps)


if __name__ == "__main__":
    app.run(debug=True)
