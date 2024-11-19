import os
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
import json
from sklearn.preprocessing import LabelEncoder
from kafka import KafkaConsumer
import pickle 
import pandas as pd
from hdfs import InsecureClient
import time
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load your pre-trained Random Forest model
try:
    # Load the model using pickle
    model = pickle.load(open('random_forest_model.sav', 'rb'))
    logging.info("Random Forest model loaded successfully.")
except Exception as e:
    logging.error(f"Error loading Random Forest model: {e}")
    sys.exit(1)

# Initialize Kafka Consumer
try:
    consumer = KafkaConsumer(
    'iot-stream',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='iot-group',
    consumer_timeout_ms=1000,
    session_timeout_ms=10000,
    max_poll_records=100
    )
    logging.info("Kafka consumer initialized.")
except Exception as e:
    logging.error(f"Error initializing Kafka consumer: {e}")
    sys.exit(1)

# Initialize HDFS client
try:
    hdfs_client = InsecureClient('http://127.0.0.1:9870', user='hadoop')
    logging.info("Connected to HDFS successfully.")
except Exception as e:
    logging.error(f"Error connecting to HDFS: {e}")
    sys.exit(1)

# HDFS directory where data will be stored
hdfs_dir = '/Bot_Iot_dataSet'
batch_size = 100
results = []

with open('le_flgs.pkl', 'rb') as f:
    le_flgs = pickle.load(f)

with open('le_proto.pkl', 'rb') as f:
    le_proto = pickle.load(f)
try:
    while True:
        for message in consumer:
            try:
                data = json.loads(message.value.decode('utf-8'))
                logging.info(f"Consumed: {data}")
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON: {e}")
                continue

            # Extract features for the ML model
            # Adjust this based on your model's expected input
            # For example, if your model expects multiple features:
            # features = [data['feature1'], data['feature2'], data['feature3']]
            
            # Perform prediction
            try:
                data['flgs'] = le_flgs.transform([data['flgs']])[0]
                data['proto'] = le_proto.transform([data['proto']])[0]

                features = [
                    data['flgs'], data['proto'], data['pkts'],
                    data['bytes'], data['dur'], data['mean'],
                    data['stddev'], data['sum'], data['min'],
                    data['max'], data['rate']
                ] # Replace with actual features required
                features_df = pd.DataFrame([features], columns=[
                    'flgs', 'proto', 'pkts', 'bytes', 'dur', 'mean',
                    'stddev', 'sum', 'min', 'max', 'rate'
                ])
                #features_array = features_df.values
                #features_df = features_df.values.reshape(1, -1)
                
                prediction = model.predict(features_df)[0]
            except KeyError as e:
                logging.error(f"Missing expected feature in data: {e}")
                continue
            except Exception as e:
                logging.error(f"Error during prediction: {e}")
                continue

          
            result = {**data, 'prediction': 'Attack' if prediction == 1 else 'Normal'}
            
            results.append(result)

            if len(results) >= batch_size:
                try:
                    # Convert results to DataFrame
                    df = pd.DataFrame(results)

                    # Generate unique filenames using timestamp
                    timestamp = time.strftime('%Y%m%d_%H%M%S')
                    temp_file_path = f'temp_results_{timestamp}.csv'
                    hdfs_file_path = f'{hdfs_dir}/anomaly_results_{timestamp}.csv'

                    # Save DataFrame to a temporary CSV
                    df.to_csv(temp_file_path, index=False)

                    # Upload to HDFS
                    with open(temp_file_path, 'rb') as f:
                        hdfs_client.write(hdfs_file_path, f, overwrite=True)
                    logging.info(f"Data stored in HDFS at {hdfs_file_path}")

                    # Commit offsets after successful upload
                    consumer.commit()
                    logging.info("Offsets committed.")

                    # Clear results and remove temporary file
                    results.clear()
                    #os.remove(temp_file_path)
                    #logging.info("Temporary file removed.")

                except Exception as e:
                    logging.error(f"Error uploading to HDFS or committing offsets: {e}")
                    results.clear()
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                    continue

except KeyboardInterrupt:
    logging.info("Shutdown requested...exiting")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")
finally:
    consumer.close()
    logging.info("Kafka consumer closed.")