from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

# Database setup
hawaii_db = './Resources/hawaii.sqlite'
engine = create_engine(f'sqlite:///{hawaii_db}')
# Reflect existing database into new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)
# Initialize table classes
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create session link to DB
session = Session(bind=engine)

# Flask setup
app = Flask(__name__)

# Flask routes
@app.route('/')
def home():
	print('Received request for "Home" page...')
	return (
		f'<h1>Welcome!</h1>\
		<strong>Available API routes:</strong>\
		<ul>\
		<li><a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a></li>\
		<li><a href="/api/v1.0/stations">/api/v1.0/stations</a></li>\
		<li><a href="/api/v1.0/tobs">/api/v1.0/tobs</a></li>\
		<li>/api/v1.0/START_DATE</li>\
		<li>/api/v1.0/START_DATE/END_DATE</ul>'
		)

@app.route('/api/v1.0/precipitation')
def prcp():
	# Query to return past years precipitation data
	last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).all()[0][0]
	ld_dt = dt.datetime.strptime(last_date, '%Y-%m-%d').date()
	year_ago = ld_dt - dt.timedelta(days=365)
	year_prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).order_by(Measurement.date).all()
	# Iterate through precipitation query results, storing date as key, list of prcp values as value
	prcp_dict = {}
	for day in year_prcp_data:
	    prcp_dict[day[0]] = []
	for day in year_prcp_data:
	    prcp_dict[day[0]].append(day[1])
	# Return the prcp_dict 
	return jsonify(prcp_dict)

@app.route('/api/v1.0/stations')
def stations():
	# Query to return the stations from the dataset
	stations = session.query(Station).all()
	# Store information about each station as a dictionary within station_data list
	station_data = []
	for station in stations:
		station_data.append(
    	{
        'id': station.id,
        'station': station.station,
        'name': station.name,
        'latitude': station.latitude,
        'longitude': station.longitude,
        'elevation': station.elevation,
    	})

	return jsonify(station_data)

@app.route('/api/v1.0/tobs')
def tobs():
	# Identify past years worth of data
	last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).all()[0][0]
	ld_dt = dt.datetime.strptime(last_date, '%Y-%m-%d').date()
	year_ago = ld_dt - dt.timedelta(days=365)
	# Query to return the observed temperatures from each station for the past year
	tobs = session.query(Measurement.date, Measurement.tobs).join(Station, Station.station == Measurement.station).filter(Measurement.date >= year_ago).all()
	# Iterate through query results and store them in tobs_data dictionary 
	# Key for each unique date, list of temps as values
	tobs_data = {}
	for day in tobs:
	    tobs_data[day[0]] = []
	for day in tobs:
	    tobs_data[day[0]].append(day[1])

	return jsonify(tobs_data)

@app.route('/api/v1.0/<start_date>')
def temp_start(start_date):
	# Normalize dates to datetime.date
	start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
	# Query to find date, min, avg, max temps with date >= start_date
	temp_range = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).group_by(Measurement.date).all()
	# Store results in dictionary with date key, temp data values list
	temp_range_data = {date[0]:[] for date in temp_range}
	for date_temps in temp_range:
		temp_range_data[date_temps[0]].append(date_temps[1])
		temp_range_data[date_temps[0]].append(date_temps[2])
		temp_range_data[date_temps[0]].append(date_temps[3])
    
	return jsonify(temp_range_data)

@app.route('/api/v1.0/<start_date>/<end_date>')
def temp_range(start_date, end_date):
	# Normalize dates to datetime.date
	start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
	end_date = dt.datetime.strptime(end_date, '%Y-%m-%d').date()
	# Query to find date, min, avg, max temps with date >= start_date <= end_date
	temp_range = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).group_by(Measurement.date).all()
	# Store results in dictionary with date key, temp data values list
	temp_range_data = {date[0]:[] for date in temp_range}
	for date_temps in temp_range:
		temp_range_data[date_temps[0]].append(date_temps[1])
		temp_range_data[date_temps[0]].append(date_temps[2])
		temp_range_data[date_temps[0]].append(date_temps[3])
    
	return jsonify(temp_range_data)

if __name__ == '__main__':
	app.run(debug=True)
