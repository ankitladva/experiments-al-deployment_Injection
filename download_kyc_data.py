#!/usr/bin/env python3
"""
KYC Data Downloader from MongoDB GridFS
Downloads videos, images, and color data in organized folder structure
"""

from pymongo import MongoClient
import  gridfs
import os
import json
from datetime import datetime

def connect_to_mongodb(uri):
    """Connect to MongoDB Atlas"""
    try:
        client = MongoClient(uri)
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        return client
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None

def download_user_data(client, user_id, download_dir="download_data"):
    """Download all data for a specific user"""
    db = client.kyc
    fs = gridfs.GridFS(db)
    
    # Create organized directory structure
    user_dir = os.path.join(download_dir, user_id)
    images_dir = os.path.join(user_dir, "images")
    videos_dir = os.path.join(user_dir, "videos")
    color_data_dir = os.path.join(user_dir, "color_data")
    
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)
    os.makedirs(color_data_dir, exist_ok=True)
    
    print(f"📁 Created directories for user: {user_id}")
    
    # Download MP4 video
    video_filename = f"{user_id}/final_video.mp4"
    try:
        video_file = fs.get_last_version(filename=video_filename)
        video_path = os.path.join(videos_dir, f"{user_id}.mp4")
        with open(video_path, "wb") as f:
            f.write(video_file.read())
        print(f"🎥 Downloaded video: {video_path}")
    except Exception as e:
        print(f"⚠️ Failed to download video: {e}")
    
    # Download PNG images
    image_files = fs.find({"metadata.user_id": user_id, "filename": {"$regex": r"\.png$"}})
    for img_file in image_files:
        try:
            filename = img_file.filename.split('/')[-1]  # Get just the filename part
            img_path = os.path.join(images_dir, filename)
            with open(img_path, "wb") as f:
                f.write(img_file.read())
            print(f"🖼️ Downloaded image: {filename}")
        except Exception as e:
            print(f"⚠️ Failed to download image {img_file.filename}: {e}")
    
    # Download color data JSON
    try:
        color_data = list(db.color_changes.find({"user_id": user_id}).sort("created_at", 1))
        if color_data:
            # Convert datetime objects to strings for JSON serialization
            for entry in color_data:
                if "created_at" in entry:
                    entry["created_at"] = entry["created_at"].isoformat()
            
            color_file_path = os.path.join(color_data_dir, f"{user_id}.json")
            with open(color_file_path, "w") as f:
                json.dump(color_data, f, indent=2)
            print(f"📊 Downloaded color data: {color_file_path}")
        else:
            print(f"⚠️ No color data found for user: {user_id}")
    except Exception as e:
        print(f"⚠️ Failed to download color data: {e}")
    
    print(f"✅ Completed download for user: {user_id}")

def download_all_users(client, download_dir="download_data"):
    """Download data for all users in the database"""
    db = client.kyc
    
    # Get unique user IDs from color_changes collection
    user_ids = db.color_changes.distinct("user_id")
    
    if not user_ids:
        print("⚠️ No users found in the database")
        return
    
    print(f"👥 Found {len(user_ids)} users: {user_ids}")
    
    for user_id in user_ids:
        print(f"\n🔄 Processing user: {user_id}")
        download_user_data(client, user_id, download_dir)
    
    print(f"\n🎉 All downloads completed! Check the '{download_dir}' folder")

def main():
    # MongoDB connection string
    MONGODB_URI = "mongodb+srv://ankitladva:tBdJcS7jscL0d6xs@injectiondetection.mxl8gdd.mongodb.net/?retryWrites=true&w=majority&appName=Injectiondetection"
    
    # Connect to MongoDB
    client = connect_to_mongodb(MONGODB_URI)
    if not client:
        return
    
    try:
        # Ask user what to download
        print("\n📥 KYC Data Downloader")
        print("1. Download specific user")
        print("2. Download all users")
        
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == "1":
            user_id = input("Enter user ID: ").strip()
            if user_id:
                download_user_data(client, user_id)
            else:
                print("❌ Invalid user ID")
        elif choice == "2":
            download_all_users(client)
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Download cancelled by user")
    except Exception as e:
        print(f"❌ Error during download: {e}")
    finally:
        client.close()
        print("🔌 MongoDB connection closed")

if __name__ == "__main__":
    main()
