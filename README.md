# Real-time-anomaly-detection-in-IoT-networks

Problem Statement
The exponential growth of IoT devices necessitates efficient and scalable real-time anomaly detection systems to ensure network security. This project aims to develop such a system using the Hadoop-Kafka framework, capable of flagging anomalous and non-anomalous events in real-time.

Objective
To implement and compare various machine learning models for real-time anomaly detection in IoT networks using the Hadoop-Spark framework. 

Tasks

● Dataset Preparation

○ Dataset: Use the BoT-IoT dataset, which includes various types of normal and attack traffic.
○ Data Exploration: Analyze and preprocess the dataset to understand its structure and features.

● Data Augmentation

○ Class Imbalance Handling: Use Conditional Tabular Generative Adversarial Network (CTGAN) to balance the dataset.

● Model Development

○ Machine Learning Models: Implement and compare multiple machine learning algorithms such as Random Forest, Decision Trees, Naive Bayes, Logistic Regression, SVM with One-vs-Rest, and Gradient Boosted Trees.
○ Evaluation Metrics: Use F1-score and other relevant metrics to assess model performance.

● Big Data Framework

○ Hadoop-Spark Integration: Utilize Hadoop-Kafka for distributed processing and real-time anomaly detection.
○ Pipeline Development: Develop a scalable pipeline for data preprocessing, model training, and real-time anomaly detection.

Deliverables

IoT Anomaly Detection Model:

● A trained and scalable machine learning model based on methods like Random Forest, K-Means Clustering, or Autoencoders that can classify events as anomalous or non-anomalous in real-time.

Real-Time Dashboard for Monitoring:

● A web-based dashboard to display the system’s real-time status, incoming data streams, and flagged anomalous events including Visualizations in form of graphs, tables, and
alert systems for real-time monitoring.

Performance Reports and Documentation:

● A detailed report including the system architecture, data flow, performance metrics (e.g., latency, accuracy, false positive rate), and scalability testing.
● Comprehensive technical documentation for deployment, configuration, and system usage.

Source Code and Scripts:

● A GitHub repository containing all source code, deployment scripts, and instructions for setting up the system.

-------------------------------------------------------------------------------------------------------------------------------------------------------------
Reference paper - https://www.mdpi.com/1424-8220/22/20/7726

Dataset Link - https://www.kaggle.com/datasets/vigneshvenkateswaran/bot-iot
