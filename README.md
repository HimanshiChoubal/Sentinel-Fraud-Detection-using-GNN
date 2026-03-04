SENTINEL — Real-Time Fraud Detection System using Graph Neural Networks
Built an end-to-end fraud detection platform leveraging GraphSAGE Graph Neural Networks (GNN) and graph-based ring detection to identify coordinated fraud networks across 50,000 synthetic financial transactions.
Tech Stack: Python · PyTorch · FastAPI · Spring Boot (Java 25) · MySQL (AWS RDS) · Neo4j AuraDB · Streamlit · Docker
Key Contributions & Achievements:

Designed and trained a GraphSAGE GNN model (AUC: 0.83) on a heterogeneous transaction graph with 50,000 nodes and 402,656 edges, incorporating user-merchant-device-IP relationships for fraud classification
Built a Neo4j AuraDB graph database with 13,912 nodes and 4 relationship types (User→Transaction→Merchant/Device/IP), enabling real-time graph traversal queries for fraud ring detection
Engineered 14 domain-specific features including device ring score, IP ring score, and combined ring score to quantify coordinated fraud behavior — identifying device D02987 shared by 81 users with 67.9% fraud rate
Developed a RESTful microservices architecture with Spring Boot (port 8080) handling transaction CRUD operations and FastAPI (port 8000) serving GNN inference, connected via HTTP client integration
Implemented fraud ring detection algorithms using Cypher queries on Neo4j to surface devices and IPs shared by suspicious user clusters, enabling network-level fraud identification beyond individual transaction analysis
Built an interactive Streamlit dashboard with 6 pages: real-time fraud check on existing transactions, arbitrary transaction prediction bypassing the database entirely, ring detector with drill-down investigation, and statistical analytics with Plotly visualizations
Performed ETL pipeline syncing MySQL relational data to Neo4j graph format, transforming 5,000 transaction records into a connected graph with MADE, AT, USED_DEVICE, and FROM_IP relationships
