# db_operations.py
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

# Constants
DB = "autohalle"
CARS_COLL = "cars"
FEATURES_COLL = "features"

def connect_to_mongodb(conn_str):
    """Connect to MongoDB Atlas"""
    try:
        client = MongoClient(conn_str)
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB Atlas: {e}")
        return None

def save_features(conn_str, car_id, raw_text, categorized_features, all_features, ai_model):
    """
    Save extracted features to MongoDB.
    
    Args:
        conn_str (str): MongoDB connection string
        car_id (str or ObjectId): ID of the car document
        raw_text (str): Original text
        categorized_features (dict): Categorized features
        all_features (list): All features in alphabetical order
        ai_model (str): LLM model used for extraction
        
    Returns:
        str: ID of the inserted document
    """
    client = connect_to_mongodb(conn_str)
    
    if client:
        db = client[DB]
        features_collection = db[FEATURES_COLL]
        
        # Convert string ID to ObjectId if needed
        if isinstance(car_id, str):
            car_id = ObjectId(car_id)
        
        features_doc = {
            "car_id": car_id,
            "raw_text": raw_text,
            "extraction_date": datetime.now().strftime('%d-%m-%Y'),
            "extraction_time": datetime.now().strftime('%H:%M:%S'),
            "ai_model": ai_model,
            "categorized_features": categorized_features,
            "all_features": all_features
        }
        
        result = features_collection.insert_one(features_doc)
        
        # Update car document with reference to features
        cars_collection = db[CARS_COLL]
        cars_collection.update_one(
            {"_id": car_id},
            {"$set": {"features_id": result.inserted_id}}
        )
        
        return str(result.inserted_id)
    
    return None

def get_features_by_car_id(conn_str, car_id):
    """
    Get features for a specific car.
    
    Args:
        conn_str (str): MongoDB connection string
        car_id (str or ObjectId): ID of the car document
        
    Returns:
        dict: Features document
    """
    client = connect_to_mongodb(conn_str)
    
    if client:
        db = client[DB]
        features_collection = db[FEATURES_COLL]
        
        # Convert string ID to ObjectId if needed
        if isinstance(car_id, str):
            car_id = ObjectId(car_id)
        
        features = features_collection.find_one({"car_id": car_id})
        return features
    
    return None

def get_all_features(conn_str, limit=10):
    """
    Get all feature documents.
    
    Args:
        conn_str (str): MongoDB connection string
        limit (int): Maximum number of documents to return
        
    Returns:
        list: List of feature documents
    """
    client = connect_to_mongodb(conn_str)
    
    if client:
        db = client[DB]
        features_collection = db[FEATURES_COLL]
        
        features = list(features_collection.find().sort("extraction_date", -1).limit(limit))
        return features
    
    return []