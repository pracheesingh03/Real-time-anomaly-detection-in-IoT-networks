import os
import json
import pandas as pd
from kafka import KafkaProducer
from kafka.errors import KafkaError
import gc

def create_producer():
    try:
        # Initialize Kafka Producer
        producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            retries=5,
            acks='all'
        )
        print("Kafka Producer initialized successfully.")
        return producer
    except KafkaError as e:
        print(f"Error initializing Kafka Producer: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def send_data(producer, topic, data):
    try:
        for record in data:
            future = producer.send(topic, value=record)
            result = future.get(timeout=10)  # Block until the message is sent
            print(f"Successfully sent: {record}")
        producer.flush()  # Ensure all data is sent
    except Exception as e:
        print(f"Failed to send data: {e}")

def process_csv_files(folder_path):
    """Read CSV files, filter required columns, and convert to a list of dictionaries."""
    selected_columns = ["flgs", "proto", "pkts", "bytes", "dur", "mean", 
                        "stddev", "sum", "min", "max", "rate"]
    
    data_list = []
    chunk_size = 100  # Adjust chunk size as needed

    filenames_to_process = [f"data_{i}.csv" for i in range(1, 2)]  

    processed_files = set()

    for filename in filenames_to_process:
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename not in processed_files:
            processed_files.add(filename)
            print(f"Processing file: {file_path}")
            
            try:
                # Read CSV in chunks and process
                for chunk in pd.read_csv(file_path, usecols=selected_columns, chunksize=chunk_size, engine='python'):
                    for column in ["dur", "mean", "stddev", "min", "max", "rate"]:
                        chunk[column] = pd.to_numeric(chunk[column], errors='coerce')
                    
                    records = chunk.to_dict(orient='records')
                    data_list.extend(records)
                
                # Clear memory after processing each file
                del chunk
                gc.collect()

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
    
    return data_list

if __name__ == "__main__":
    # Path to your CSV files
    folder_path = r"E:\BdaPROJECT\Bot_Iot_dataSet"
    
    # Create Kafka Producer
    producer = create_producer()
    
    if producer:
        # Process CSV files and get data
        data_to_send = process_csv_files(folder_path)
        
        # Send data to Kafka topic
        send_data(producer, 'iot-stream', data_to_send)
        
        # Cleanup
        producer.flush()
        producer.close()
        print("Data sent successfully.")
    else:
        print("Producer creation failed.")