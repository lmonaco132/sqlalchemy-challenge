# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np
from flask import Flask, jsonify



# create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# set up base with automap_base
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)



# define function for use in start and end date routes
# this function returns the row object from a query which filtered by date
# the row has the date, the min temp, max temp, and average temp
# argument is the date to filter for
def date_temps(start):
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date == start).all()
    # result is a list even though its just one row, return just the row 
    return results[0]




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
        f"/api/v1.0/year-month-day<br/>"
        f"/api/v1.0/year-month-day/year-month-day<br/>"
    )



# precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return 12 months of precipitation data"""

    # Query precipitation and date from Measurement table
    # filtered by most recent year in dataset
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > dt.date(2016, 8, 23)).all()

    # close session so we don't run into problems later
    session.close()

    # now make the results into a dictionary, with date as key and prcp as value
    rows = {}
    for date, prcp in results:
        rows[date] = prcp

    # return jsonified list of dictionaries 
    return jsonify(rows)



# stations route
@app.route("/api/v1.0/stations")
def stations():
    # Create session link from python to db
    session = Session(engine)

    """Return JSON list of stations in the dataset"""

    # Query precipitation and date from Measurement table
    # filtered by most recent year in dataset
    results = session.query(Station.station).all()

    # close session so we don't run into problems later
    session.close()

    all_stations = list(np.ravel(results))

    # return results
    return jsonify(all_stations)



# tobs route
@app.route("/api/v1.0/tobs")
def temp():
    # Create session link from python to db
    session = Session(engine)

    """Return JSON list of temperature observations for most active station in the last year of data"""

    # query for temperature observations for the specific station USC00519281 (most active) in last year of data
    results_station = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date > dt.date(2016, 8, 23)).all()

     # close session so we don't run into problems later
    session.close()

    # create list for jsonify (doesnt like row type objects)
    stations_list = []

    # pull the tobs value from the row, put it into our list
    for row in results_station:
        stations_list.append(row.tobs)

    # return the formed list, jsonified
    return jsonify(stations_list)



# start date route
@app.route("/api/v1.0/<start>")
def start_date(start):
    # create session link from python to db
    session = Session(engine)

    """Return JSON list of minimum, maximum, and average temperature observations after the given date"""

    # need to iterate through all the given dates
    # and pull desired info from each one

    # going to call my function which returns a list of row objects
    # row objects are index-able, with values in order as date, min temp, max temp, avg temp

    date_rows = []
    
    time_range = dt.date(2017,8,23) - dt.datetime.strptime(start, '%Y-%m-%d').date()

    for i in range(time_range.days):
        day = dt.datetime.strptime(start, '%Y-%m-%d').date() + dt.timedelta(days=i)
        date_rows.append(date_temps(day))
        
    
    # now date_rows is a list of rows
    # we need to iterate through the rows and pull out the values
    results_date = []
    for row in date_rows:
        row_dict = {}
        row_dict['date'] = row[0]
        row_dict['min'] = row[1]
        row_dict['max'] = row[2]
        row_dict['avg'] = row[3]
        results_date.append(row_dict)


     # close session so we don't run into problems later
    session.close()

    # return as json 
    return jsonify(results_date)



# start + end dates route   
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # create session link from python to db
    session = Session(engine)

    """Return JSON list of minimum, maximum, and average temperature observations between the given dates"""

    # again we need to call my function for this, now the time range is defined by start and end date instead of just start
    date_rows = []
    
    # time range is the number of days from the start date to the end date, how many rows we need to return
    time_range = dt.datetime.strptime(end, '%Y-%m-%d').date() - dt.datetime.strptime(start, '%Y-%m-%d').date()

    # iterate through all the dates, for each one call my function to get min, max, and avg temperature 
    for i in range(time_range.days):
        day = dt.datetime.strptime(start, '%Y-%m-%d').date() + dt.timedelta(days=i)
        date_rows.append(date_temps(day))
        
    
    # now date_rows is a list of rows
    # we need to iterate through the rows and pull out the values
    results_date = []
    for row in date_rows:
        row_dict = {}
        row_dict['date'] = row[0]
        row_dict['min'] = row[1]
        row_dict['max'] = row[2]
        row_dict['avg'] = row[3]
        results_date.append(row_dict)


     # close session so we don't run into problems later
    session.close()

    # return as json 
    return jsonify(results_date)



if __name__ == '__main__':
    app.run(debug=True)
