import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from datetime import datetime as dt
from datetime import timedelta

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# In the home page, need to see all the routes available
@app.route("/")
def home():
    return(
        f"Welcome to the Justice League API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

### Create precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the data
    # Calculate the date 1 year ago from the last data point in the database
    lastdate = session.query(Measurement.date).\
    order_by(Measurement.date.desc()).first()
    lastdate = str(lastdate[0])
    lastdateobj = dt.strptime(lastdate, '%Y-%m-%d')
    delta = timedelta(days=365)
    oneyearago = lastdateobj - delta
    oneyearago = str(oneyearago)[:10]
    # Design a query to retrieve the last 12 months of precipitation data
    oneyrprcp = session.query(Measurement.date, func.avg(Measurement.prcp)).\
    filter(Measurement.date >= oneyearago).group_by(Measurement.date).all()
    oneyrprcp_dict = dict(oneyrprcp)
    # Close section and return the jsonified dictionary
    session.close()
    return jsonify(oneyrprcp_dict)

### Create stations route    
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the data for list of stations
    allstations = session.query(Measurement.station).group_by(Measurement.station).all()
    allstations_dict = dict(allstations)
    # Close section and return the jsonified dictionary
    session.close()
    return jsonify(allstations)

### Create tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the dates and temperature observations of the most active station for the latest year of data.
    temps = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= oneyearago).\
        filter_by(station='USC00519281').\
        group_by(Measurement.date).all()
    temps_dict = dict(temps)
    # Close section and return the jsonified dictionary
    session.close()
    return jsonify(temps)
      
### Create <start> route
@app.route("/api/v1.0/<start>")
def dateparam(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the dates and temperature observations of the most active station for the latest year of data.
    tempsstart = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    # Close section and return the jsonified dictionary
    session.close()
    return jsonify(tempsstart)

# Create <start>/<end> route
@app.route("/api/v1.0/<start>/<end>")
def rangeparam(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the dates and temperature observations of the most active station for the latest year of data.
    tempsrange = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
   
    # Close section and return the jsonified dictionary
    session.close()
    return jsonify(tempsrange)

if __name__ == "__main__":
    app.run(debug=True)
