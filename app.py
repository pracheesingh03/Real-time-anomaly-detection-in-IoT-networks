from flask import Flask, jsonify, request
from hdfs import InsecureClient
import pandas as pd
import os
from flask_cors import CORS
import threading
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

HDFS_URL = 'http://localhost:9870'
HDFS_DIR = '/Bot_Iot_dataSet'
hdfs_client = InsecureClient(HDFS_URL, user='hadoop')

# Shared data structure to hold combined data
combined_data = []
# Set to keep track of processed files
processed_files = set()
# Lock to ensure thread safety
data_lock = threading.Lock()

def process_new_files():
    global combined_data, processed_files
    while True:
        try:
            # List all CSV files in the HDFS directory
            files = hdfs_client.list(HDFS_DIR)
            csv_files = [file for file in files if file.endswith('.csv')]

            print(f"CSV files in HDFS directory '{HDFS_DIR}': {csv_files}")

            # Find new files that haven't been processed yet
            new_files = [file for file in csv_files if file not in processed_files]

            if new_files:
                for csv_file in new_files:
                    print(f"Reading new file: {csv_file}")
                    with hdfs_client.read(f"{HDFS_DIR}/{csv_file}") as f:
                        df = pd.read_csv(f)
                        # Acquire lock before modifying shared data
                        with data_lock:
                            # Append new data to combined_data
                            combined_data.extend(df.to_dict(orient='records'))
                    # Add the file to the set of processed files
                    processed_files.add(csv_file)
                    print(f"Processed file: {csv_file}")
            else:
                print("No new files found.")

            # Sleep for a specified interval before checking again
            time.sleep(5)  # Check for new files every 5 seconds

        except Exception as e:
            print(f"Error processing files: {str(e)}")
            time.sleep(5)  # Wait before retrying in case of error

@app.route('/')
def home():
    return "Welcome to the Real-time IoT Anomaly Detection Dashboard"

@app.route('/data', methods=['GET'])
def get_data():
    try:
        # Acquire lock before accessing shared data
        with data_lock:
            # Return the combined data as JSON
            return jsonify(combined_data)
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start the file processing in a separate thread
    file_thread = threading.Thread(target=process_new_files, daemon=True)
    file_thread.start()

    # Run the Flask app
    app.run(debug=True)
