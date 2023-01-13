import numpy as np 
import datetime as dt 
import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


##Database creation 
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)


####Flask setup
app = Flask(__name__)


#routes
@app.route("/")
def home():
    """List all available routes."""
    return (
        f"<h1>Available Routes:</h1><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"(start: A date string in the format YYYY-mm-dd)<br/>"
        f"/api/v1.0/start/end<br/>"
        f"(start/end: A date string in the format YYYY-mm-dd)<br/>"
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    """Converts Query results to a Dictionary using `date` as the key and `prcp` as the value."""
    lastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    lastYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    precip_data = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>=lastYear).order_by(Measurement.date).all()
    
    precipDict = []
    for date, prcp in precip_data:
        precipResultsDict = {}
        precipResultsDict["date"] = date
        precipResultsDict["prcp"] = prcp
        precipDict.append(precipResultsDict)
    
    return jsonify(precipDict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations"""
    
    results = session.query(Station.station).all()

    return jsonify(results)


@app.route("/api/v1.0/tobs")
def tobs():
    """Query for the dates and temperature observations from a year from the last data point."""
 
    lastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    lastYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    """* Return a JSON list of Temperature Observations (tobs) for the previous year."""
    tobsData = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>=lastYear).order_by(Measurement.date).all()
    

    return jsonify(tobsData)



@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == '__main__':
    app.run(debug=True)