# data_loader.py
import pandas as pd
import os

def load_data():
    """
    Loads the e-commerce dataset from the provided CSV files.
    
    It assumes the CSV files are in a 'data' folder inside 'backend'.
    """
    data_path = os.path.join(os.path.dirname(__file__), 'data')
    
    try:
        # Load all the csv files from the provided dataset
        files = [
            "products", 
            "orders", 
            "order_items", 
            "inventory_items", 
            "users", 
            "distribution_centers"
        ]
        
        data_frames = {f: pd.read_csv(os.path.join(data_path, f"{f}.csv")) for f in files}

        print("✅ All datasets loaded successfully!")
        return data_frames

    except FileNotFoundError as e:
        print(f"❌ Error loading data: {e}")
        print("Please ensure all dataset CSV files are in the 'backend/data/' directory.")
        return None

