from flask import Flask, render_template, request
import requests
import json
import logging

app = Flask(__name__)

# Read the OpenSky Network credentials from the credentials.txt file
with open('credentials.txt', 'r') as file:
    credentials = dict(line.strip().split('=') for line in file)

username = credentials['USERNAME']
password = credentials['PASSWORD']

# Set up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/', methods=['POST'])
def search():
    # Get the flight number from the search form
    flight_number = request.form['flight_number'].upper()

    # Log the flight number
    logging.info(f"Searching for flight {flight_number}")

    # Make a request to the OpenSky Network REST API to get live tracking data for the flight
    response = requests.get(f"https://opensky-network.org/api/tracks/all?icao24={flight_number}&time=0", auth=(username, password))

    # Log the response status code
    logging.info(f"Response status code: {response.status_code}")

    # Check if the response was successful
    if response.status_code == 200:
        # Parse the response JSON data
        data = json.loads(response.content)

        # Check if the flight was found
        if len(data) == 0:
            logging.warning(f"Flight {flight_number} not found")
            return render_template('error.html', message=f'Flight {flight_number} not found.')

        # Extract the flight data
        flight_data = data[0]
        latitude = flight_data['latitude']
        longitude = flight_data['longitude']
        altitude = flight_data['baro_altitude']
        velocity = flight_data['velocity']
        heading = flight_data['heading']

        # Render the search results template with the flight data
        return render_template('search_results.html', flight_number=flight_number,
                               latitude=latitude, longitude=longitude,
                               altitude=altitude, velocity=velocity, heading=heading)
    else:
        # Render an error template if the response was not successful
        logging.error(f"An error occurred while retrieving live tracking data for flight {flight_number}")
        return render_template('error.html', message='An error occurred while retrieving live tracking data for the flight.')

if __name__ == '__main__':
    app.run(debug=True)