# Merchant Agent

## Project Description
The **Merchant Agent** is an intelligent, AI-powered system designed to assist merchants in optimizing their business operations through advanced demand forecasting and product management. Leveraging machine learning, this project analyzes historical sales data to predict future demand, helping businesses make informed decisions regarding inventory, pricing, and overall strategy.

It features a robust client-server architecture for scalable operations, a data simulation module for testing and scenario analysis, and an interactive web application built with Streamlit for intuitive visualization of insights and user interaction.

## Features
-   **AI-Powered Demand Forecasting:** Utilizes machine learning models to predict future product demand based on historical sales data.
-   **Product Management Optimization:** Assists in managing product inventory and mapping for efficient operations.
-   **Client-Server Architecture:** Provides a scalable and modular foundation for handling data and model serving.
-   **Data Simulation:** Generates synthetic sales data for model training, testing, and scenario analysis.
-   **Interactive Web UI (Streamlit):** A user-friendly interface for visualizing forecasts, managing products, and interacting with the system.
-   **Model Training Pipeline:** Includes scripts for training and persisting demand forecasting models.

## Technologies Used
-   Python
-   Scikit-learn (or similar ML library for demand_model.pkl)
-   Streamlit
-   Flask (likely for server.py)
-   Pandas, NumPy (for data handling)
-   Docker (for development container)

## Setup and Installation

### Prerequisites
-   Python 3.8+
-   Docker (recommended for consistent development environment)

### Option 1: Using Dev Containers (Recommended)
If you have Docker installed and the VS Code "Dev Containers" extension:
1.  Clone the repository:
    ```bash
    git clone https://github.com/MohammadNoman/Merchant-Agent.git
    cd Merchant-Agent
    ```
2.  Open the project in VS Code.
3.  When prompted, click "Reopen in Container" to launch a pre-configured development environment. All dependencies will be automatically installed.

### Option 2: Local Setup
1.  Clone the repository:
    ```bash
    git clone https://github.com/MohammadNoman/Merchant-Agent.git
    cd Merchant-Agent
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```
3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Train the Demand Model
First, train the machine learning model using your historical sales data.
```bash
python train_model.py
```
This will generate `demand_model.pkl` and `product_map.pkl`.

### 2. Simulate Data (Optional)
You can simulate additional data if needed for testing or extending your dataset.
```bash
python data_sim.py
```

### 3. Run the Server
Start the backend server, which might serve the model or handle client requests.
```bash
python server.py
```

### 4. Launch the Streamlit Web Application
Access the interactive UI to visualize forecasts and interact with the system.
```bash
streamlit run streamlit_app.py
```
Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

### 5. Run the Client (if applicable)
If there's a separate client application, you can run it as follows:
```bash
python client.py
```

## Project Structure
```
.
├── client.py             # Client-side application logic
├── data_sim.py           # Script for simulating sales data
├── demand_model.pkl      # Trained demand forecasting model
├── product_map.pkl       # Mapping for product information
├── requirements.txt      # Python dependencies
├── sales_history.csv     # Historical sales data
├── server.py             # Backend server for model serving/API
├── streamlit_app.py      # Interactive Streamlit web application
├── train_model.py        # Script for training the ML model
├── .devcontainer/        # Development Container configuration
│   └── devcontainer.json
└── .gitignore            # Specifies intentionally untracked files to ignore
```

## Author
**Mohammad Noman**

## License
This project is open-sourced under the [MIT License](LICENSE). (Assuming MIT, can be changed if user specifies)
