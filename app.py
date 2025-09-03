import cv2
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import uuid4
import os
import threading
import json
import subprocess
import shutil
from collections import defaultdict
import uvicorn
import ssl
from typing import Dict, List, Any, Optional
from utils import compare_all_frames
import glob
import datetime
import boto3
from botocore.exceptions import ClientError

app = FastAPI()

# Security configuration
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable must be set for security. Please set a secure API key.")
API_KEY_HEADER = "X-API-Key"

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security dependency
async def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key is required")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key

# Health endpoint for uptime checks (no authentication required)
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Secure endpoint to get API key (for frontend use)
@app.get("/api-key")
async def get_api_key():
    # This endpoint returns a hashed version of the API key for verification
    import hashlib
    hashed_key = hashlib.sha256(API_KEY.encode()).hexdigest()[:16]
    return {"api_key_hash": hashed_key, "message": "Use this hash to verify your API key"}

"""
S3 configuration
"""
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_PREFIX = os.getenv("S3_PREFIX", "")
AWS_REGION = os.getenv("AWS_REGION")

s3_client = None
if not S3_BUCKET_NAME:
    print("ℹ️ S3 disabled: S3_BUCKET_NAME not set")
if S3_BUCKET_NAME:
    try:
        s3_client = boto3.client("s3", region_name=AWS_REGION) if AWS_REGION else boto3.client("s3")
        # Validate bucket access
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        print(f"✅ Connected to S3 bucket: {S3_BUCKET_NAME}")
    except Exception as e:
        print(f"⚠️ S3 initialization failed: {e}")
        s3_client = None


def s3_enabled() -> bool:
    return s3_client is not None and bool(S3_BUCKET_NAME)


def _s3_key(key: str) -> str:
    key = key.lstrip("/")
    if S3_PREFIX:
        return f"{S3_PREFIX.rstrip('/')}/{key}"
    return key


def upload_file_to_s3(file_path: str, key: str, content_type: Optional[str] = None, metadata: Optional[dict] = None) -> Optional[str]:
    if not s3_enabled() or not os.path.exists(file_path):
        return None
    extra_args: Dict[str, Any] = {}
    if content_type:
        extra_args["ContentType"] = content_type
    if metadata:
        extra_args["Metadata"] = {k: str(v) for k, v in metadata.items() if v is not None}
    try:
        s3_client.upload_file(file_path, S3_BUCKET_NAME, _s3_key(key), ExtraArgs=extra_args)
        print(f"✅ Uploaded to S3: s3://{S3_BUCKET_NAME}/{_s3_key(key)}")
        return key
    except ClientError as e:
        print(f"⚠️ Failed to upload to S3: {e}")
        return None


def upload_bytes_to_s3(content_bytes: bytes, key: str, content_type: Optional[str] = None, metadata: Optional[dict] = None) -> Optional[str]:
    if not s3_enabled():
        return None
    extra_args: Dict[str, Any] = {}
    if content_type:
        extra_args["ContentType"] = content_type
    if metadata:
        extra_args["Metadata"] = {k: str(v) for k, v in metadata.items() if v is not None}
    try:
        s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=_s3_key(key), Body=content_bytes, **extra_args)
        print(f"✅ Uploaded object to S3: s3://{S3_BUCKET_NAME}/{_s3_key(key)}")
        return key
    except ClientError as e:
        print(f"⚠️ Failed to upload object to S3: {e}")
        return None


def save_json_to_s3(obj: dict, key: str) -> Optional[str]:
    try:
        content = json.dumps(obj, indent=4).encode("utf-8")
        return upload_bytes_to_s3(content, key, content_type="application/json")
    except Exception as e:
        print(f"⚠️ Failed to serialize JSON for S3: {e}")
        return None

# Define storage directories
UPLOAD_FOLDER = "data"
CHUNKS_FOLDER = os.path.join(UPLOAD_FOLDER, "chunks")
MP4_FOLDER = os.path.join(UPLOAD_FOLDER, "mp4")
COLOR_DATA_FOLDER = os.path.join(UPLOAD_FOLDER, "color_data")
IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, "images")

# Color mapping from hex to name
COLOR_MAP = {
    "#00000000": "transparent",
    "#000000": "black",
    "#0000FF": "blue",
    "#FFFF00": "yellow",
    "#00FF00": "green",
    "#FF0000": "red",
    "#00FFFF": "cyan",
    "#FFFFFF": "white"
}

# Ensure all directories exist
os.makedirs(CHUNKS_FOLDER, exist_ok=True)
os.makedirs(MP4_FOLDER, exist_ok=True)
os.makedirs(COLOR_DATA_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Thread-safe storage for user data
user_data = defaultdict(lambda: {"video_chunks": [], "converted_mp4s": [], "color_changes": []})
user_locks = defaultdict(threading.Lock)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Check for API key in query parameters for WebSocket
    api_key = websocket.query_params.get("api_key")
    if not api_key or api_key != API_KEY:
        await websocket.close(code=4001, reason="Invalid API key")
        return
    
    user_id = str(uuid4())
    await manager.connect(websocket, user_id)
    
    # Send user_id to client
    await websocket.send_json({"event": "user_id", "data": {"user_id": user_id}})
    print(f"✅ User connected: {user_id}")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            event = data.get("event")
            
            if event == "video_start":
                handle_video_start(data.get("data", {}))
            
            elif event == "color_change":
                handle_color_change(data.get("data", {}), user_id)
            
            elif event == "video_chunk":
                # For binary data, we need to receive bytes
                binary_data = await websocket.receive_bytes()
                handle_video_chunk(data.get("data", {}), binary_data, user_id)
            
            elif event == "video_end":
                handle_video_end(data.get("data", {}), user_id)
                # Send response back to client
                await manager.send_personal_message(
                    {"event": "video_processed", "data": {"message": "Video processing complete"}},
                    user_id
                )
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        print(f"❌ User disconnected: {user_id}")

def handle_video_start(data):
    user_id = data.get("user_id")
    start_time = data.get("timestamp")
    print(f"✅ start time: {start_time}")

def handle_color_change(data, user_id):
    """Stores color change events in a JSON file per user and mirrors to S3."""
    previous_color = data.get("previousColor")
    new_color = data.get("newColor")
    timestamp = data.get("timestamp")
    video_start_time = data.get("video_start_time")

    if not user_id:
        return

    # Convert hex colors to names
    previous_color_name = COLOR_MAP.get(previous_color, previous_color)
    new_color_name = COLOR_MAP.get(new_color, new_color)

    user_color_file = os.path.join(COLOR_DATA_FOLDER, f"{user_id}.json")

    with user_locks[user_id]:
        color_data = []
        if os.path.exists(user_color_file):
            with open(user_color_file, "r") as f:
                color_data = json.load(f)

        entry = {
            "previous_color": previous_color_name,
            "new_color": new_color_name,
            "timestamp": timestamp,
            "video_start_time": video_start_time
        }
        color_data.append(entry)

        with open(user_color_file, "w") as f:
            json.dump(color_data, f, indent=4)

    # Also mirror the aggregated color data file to S3 to match download_data structure
    if s3_enabled():
        try:
            s3_key = f"download_data/{user_id}/color_data/{user_id}.json"
            upload_file_to_s3(user_color_file, key=s3_key, content_type="application/json")
        except Exception as e:
            print(f"⚠️ Failed to upload color data JSON to S3: {e}")

    print(f"🎨 Color Change Logged: {previous_color_name} → {new_color_name} at {timestamp} for {user_id}")

def _ext_from_mime(mime: Optional[str]) -> str:
    if not mime:
        return ".webm"
    mime = mime.lower()
    if "mp4" in mime:
        return ".mp4"
    if "webm" in mime:
        return ".webm"
    return ".webm"


def handle_video_chunk(data, binary_data, user_id):
    """Handles video chunk received from the client."""
    start_time = data.get("startTime")
    end_time = data.get("endTime")
    mime_type = data.get("mimeType")
    sequence = data.get("sequence")

    if not user_id or binary_data is None:
        return

    # Save the binary chunk
    with user_locks[user_id]:
        ext = _ext_from_mime(mime_type)
        safe_seq = f"_{int(sequence):06d}" if sequence is not None else ""
        chunk_filename = f"{user_id}_{start_time}_{end_time}{safe_seq}{ext}"
        chunk_path = os.path.join(CHUNKS_FOLDER, chunk_filename)
        with open(chunk_path, "wb") as f:
            f.write(binary_data)

        user_data[user_id]["video_chunks"].append(chunk_path)
        print(f"Chunk saved for user {user_id}: {chunk_path}, {start_time} {end_time} mime={mime_type}")

def handle_video_end(data, user_id):
    """Handles video end event and merges chunks for a specific user."""
    if not user_id:
        return

    with user_locks[user_id]:
        chunk_paths = list(user_data[user_id]["video_chunks"])
        if not chunk_paths:
            print(f"⚠️ No chunks found for user {user_id} on video_end")
            return

        # Ensure chunks are ordered by the sequence number if present, else by start time
        def _parse_seq(path: str) -> int:
            base = os.path.basename(path)
            parts = base.split("_")
            try:
                # last token might contain sequence like 000001.ext
                seq_part = parts[-1]
                seq_num = int(seq_part.split(".")[0])
                return seq_num
            except Exception:
                return 0

        def _parse_start(path: str) -> int:
            base = os.path.basename(path)
            parts = base.split("_")
            try:
                return int(parts[1])
            except Exception:
                return 0

        # Sort by sequence first if any sequence exists, else by start time
        if any(path.rsplit("_", 1)[-1].split(".")[0].isdigit() for path in chunk_paths):
            chunk_paths.sort(key=_parse_seq)
        else:
            chunk_paths.sort(key=_parse_start)

        num_chunks = len(chunk_paths)

        # If chunks are MP4, concatenate via ffmpeg; if WebM, first convert to MP4
        mp4_chunks: List[str] = []
        temp_dir = os.path.join(MP4_FOLDER, user_id)
        os.makedirs(temp_dir, exist_ok=True)

        for idx, path in enumerate(chunk_paths):
            ext = os.path.splitext(path)[1].lower()
            if ext == ".mp4":
                mp4_chunks.append(path)
            else:
                mp4_path = os.path.join(temp_dir, f"chunk_{idx:06d}.mp4")
                if convert_webm_to_mp4(path, mp4_path):
                    mp4_chunks.append(mp4_path)
                else:
                    print(f"⚠️ Skipping chunk that failed to convert: {path}")

        output_video_path = os.path.join(MP4_FOLDER, f"{user_id}_final_video.mp4")

        if len(mp4_chunks) == 1:
            # Single chunk, copy to final
            shutil.copyfile(mp4_chunks[0], output_video_path)
        elif len(mp4_chunks) > 1:
            if not merge_mp4_chunks(mp4_chunks, output_video_path):
                print(f"❌ Failed to merge MP4 chunks for user {user_id}")
                return
        else:
            print(f"❌ No usable MP4 chunks for user {user_id}")
            return

        # Clear user data
        user_data[user_id]["video_chunks"].clear()

        print(f"✅ Video created for user {user_id}: {output_video_path}")
        # Upload merged MP4 to S3 in desired folder structure
        upload_file_to_s3(
            output_video_path,
            key=f"download_data/{user_id}/videos/{user_id}.mp4",
            content_type="video/mp4",
            metadata={
                "user_id": user_id,
                "created_at": datetime.datetime.utcnow().isoformat(),
                "num_chunks": num_chunks
            }
        )
        extract_frames(user_id, output_video_path)
        # res=analyze_video(user_id)
        cleanup_user_files(user_id)

def convert_webm_to_mp4(webm_path, mp4_path):
    """Converts WebM to MP4 using ffmpeg."""
    try:
        command = [
            "ffmpeg",
            "-y", "-i", webm_path,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-strict", "experimental",
            mp4_path
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error: {e.stderr.decode('utf-8')}")
        return False

def merge_mp4_chunks(mp4_chunks, output_path):
    """Merges MP4 chunks into a single video file using FFmpeg."""
    concat_file = os.path.join(os.path.dirname(output_path), "concat.txt")

    try:
        # Step 1: Create concat.txt for the MP4 chunks
        with open(concat_file, "w") as f:
            for chunk in mp4_chunks:
                f.write(f"file '{os.path.abspath(chunk)}'\n")

        # Step 2: Concatenate MP4 files into the final MP4
        command = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            output_path
        ]
        print(f"🔄 Merging MP4 chunks: {' '.join(command)}")
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Cleanup the concat.txt file
        os.remove(concat_file)
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg failed: {e.stderr.decode('utf-8')}")
        return False

def cleanup_user_files(user_id):
    """Deletes all temporary files for the user after processing."""
    user_chunk_folder = os.path.join(CHUNKS_FOLDER, user_id)
    user_mp4_folder = os.path.join(MP4_FOLDER, user_id)

    # Delete chunks and MP4 files
    if os.path.exists(user_chunk_folder):
        shutil.rmtree(user_chunk_folder)
    if os.path.exists(user_mp4_folder):
        shutil.rmtree(user_mp4_folder)

    print(f"🗑️ Deleted all temporary files for user {user_id}")

def extract_frames(user_id, video_path):
    """Extracts frames from the final video at specified timestamps."""
    user_color_file = os.path.join(COLOR_DATA_FOLDER, f"{user_id}.json")
    user_image_folder = os.path.join(IMAGE_FOLDER, user_id)
    os.makedirs(user_image_folder, exist_ok=True)

    if not os.path.exists(user_color_file):
        print(f"⚠️ No color data found for user {user_id}")
        return

    with open(user_color_file, "r") as f:
        color_data = json.load(f)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ OpenCV Error: Unable to open {video_path}")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video FPS: {fps}, Total frames: {total_frames}")

    for entry in color_data:
        timestamp = entry["timestamp"]
        video_start = entry["video_start_time"]
        previous_color = entry["new_color"]
        
        # Calculate relative time from video start in milliseconds
        relative_time_ms = timestamp - video_start
        target_frame = int((relative_time_ms / 1000) * fps)
        print(f"Looking for frame at timestamp: {timestamp}ms, relative time: {relative_time_ms}ms, target frame: {target_frame}")
        frame_number = 0
        cap = cv2.VideoCapture(video_path)
        while True:
            # Read next frame
            success, frame = cap.read()
            
            # Break the loop if we've reached the end of the video
            if not success:
                break
            
            # Save the frame as an image
            if target_frame==frame_number:
                frame_filename = f"{timestamp}_{previous_color}.png"
                frame_path = os.path.join(user_image_folder, frame_filename)
                cv2.imwrite(frame_path, frame)
                print(f"🖼️ Frame with text saved: {frame_path}")
                # Upload this saved frame to S3 in desired folder structure
                upload_file_to_s3(
                    frame_path,
                    key=f"download_data/{user_id}/images/{frame_filename}",
                    content_type="image/png",
                    metadata={
                        "user_id": user_id,
                        "timestamp": int(timestamp),
                        "relative_time_ms": int(relative_time_ms),
                        "color": previous_color
                    }
                )
            # Increment frame number
            frame_number += 1

    cap.release()

def is_video_injected(user_id):
    """
    Analyze the video frames to determine if the video is likely injected.
    Stores results in a JSON file within the analysis folder.
    """
    try:
        # Get the user's image directory
        user_image_folder = os.path.join(IMAGE_FOLDER, user_id)
        if not os.path.exists(user_image_folder):
            return {
                "status": "error",
                "message": "No images found for this user",
                "is_injected": None
            }

        # Get all PNG files in the user's directory
        images = glob.glob(os.path.join(user_image_folder, "*.png"))
        if len(images) < 2:
            return {
                "status": "error",
                "message": "Not enough images for analysis",
                "is_injected": None
            }

        # Sort images to ensure consistent order
        images.sort()
        print
        # Find transparent image as base frame
        base_frame_path = None
        colored_frame_paths = []
        
        for img_path in images:
            if "transparent" in os.path.basename(img_path).lower():
                if base_frame_path is None:
                    base_frame_path = img_path
                else:
                    colored_frame_paths.append(img_path)
            else:
                colored_frame_paths.append(img_path)

        if not base_frame_path or not colored_frame_paths:
            return {
                "status": "error",
                "message": "Could not find base frame or colored frames",
                "is_injected": None
            }

        # Create analysis directory if it doesn't exist
        analysis_dir = os.path.join("data", "analysis")
        os.makedirs(analysis_dir, exist_ok=True)
        
        # Create visualization directory if it doesn't exist
        visualization_dir = os.path.join("data", "visualization")
        os.makedirs(visualization_dir, exist_ok=True)

        # Create temporary output directory for frame analysis
        temp_dir = os.path.join("temp_analysis", user_id)
        os.makedirs(temp_dir, exist_ok=True)

        print("calling compare all frames:::",)
        # Analyze frames
        results = compare_all_frames(base_frame_path, colored_frame_paths,user_id, 
                                   output_dir=temp_dir, threshold=20)
        # print(" results :::",results)

        if not results:
            return {
                "status": "error",
                "message": "Analysis failed to produce results",
                "is_injected": None
            }

        # Calculate key metrics
        intensities = [r['intensity'] for r in results]
        consistency = 100 * (1 - (max(intensities) - min(intensities)) / max(intensities))

        # Check expected color matches
        expected_matches = {
            'Blue': 'Blue', 'Blue2': 'Blue',
            'Red': 'Red', 
            'Green': 'Green', 'Green2': 'Green',
            'Yellow': 'Red',  # Yellow often appears as high in red channel
            'Cyan': 'Green'   # Cyan often appears as high in green/blue
        }
        
        matches = sum(1 for r in results if r['dominant_channel'] == expected_matches.get(r['color'], ''))
        match_percentage = (matches / len(results)) * 100

        # Determine if video is likely injected
        is_injected = not (matches >= len(results) * 0.5 or consistency > 50)
        if is_injected:
            print("------------>Video is Injected")
        else:
            print("------------>Video is not Injected")
        # Prepare analysis result
        analysis_result = {
            "status": "success",
            "is_injected": is_injected,
            "timestamp": datetime.datetime.now().isoformat(),
            "analysis": {
                "consistency": consistency,
                "match_percentage": match_percentage,
                "total_frames_analyzed": len(results),
                "frames_matching_expected": matches,
                "intensity_range": {
                    "min": min(intensities),
                    "max": max(intensities)
                },
                "frame_details": [
                    {
                        "color": r['color'],
                        "intensity": r['intensity'],
                        "dominant_channel": r['dominant_channel'],
                        "affected_pixels": r['affected_pixels'],
                        "channel_values": r['channel_values']
                    } for r in results
                ]
            }
        }

        # Save analysis result to JSON file
        output_file = os.path.join(analysis_dir, f"{user_id}_response.json")
        with open(output_file, 'w') as f:
            json.dump(analysis_result, f, indent=4)

        # Also mirror analysis to S3 in desired folder structure
        if s3_enabled():
            upload_file_to_s3(output_file, key=f"download_data/{user_id}/analysis/{user_id}_response.json", content_type="application/json")

        # Clean up temporary directory
        shutil.rmtree(temp_dir)

        return analysis_result

    except Exception as e:
        error_result = {
            "status": "error",
            "message": str(e),
            "is_injected": None,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Save error result to JSON file
        output_file = os.path.join(analysis_dir, f"{user_id}_response.json")
        with open(output_file, 'w') as f:
            json.dump(error_result, f, indent=4)
        
        # Mirror error result to S3 as well in desired folder structure
        if s3_enabled():
            upload_file_to_s3(output_file, key=f"download_data/{user_id}/analysis/{user_id}_response.json", content_type="application/json")
            
        return error_result

# @app.get("/analyze/{user_id}")
def analyze_video(user_id: str):
    """
    Endpoint to analyze if a video is injected based on color reflection analysis.
    Results are stored in analysis/{user_id}_response.json
    """
    result = is_video_injected(user_id)
    return result

if __name__ == "__main__":
    print("🚀 Starting FastAPI with HTTPS and WebSockets on port 8000...")
    
    # Create SSL context
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    
    # Run the server with HTTPS
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8000, 
        ssl_certfile="cert.pem", 
        ssl_keyfile="key.pem",
        reload=True
    )
