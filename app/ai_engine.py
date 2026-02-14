import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure the API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_video(video_path):
    """
    Uploads a video to Gemini, waits for processing, and generates a forensic report.
    """
    try:
        print(f"--- AI ENGINE: Uploading {video_path} ---")
        
        # 1. Upload the video file to Google's temporary storage
        video_file = genai.upload_file(path=video_path)
        print(f"--- AI ENGINE: Uploaded. State: {video_file.state.name} ---")

        # 2. Wait for the video to be processed (Active State)
        while video_file.state.name == "PROCESSING":
            print("--- AI ENGINE: Processing video... ---")
            time.sleep(2)
            video_file = genai.get_file(video_file.name)

        if video_file.state.name == "FAILED":
            raise ValueError("Video processing failed by Google AI.")

        # 3. Generate the Forensic Report
        print("--- AI ENGINE: Generating Report... ---")
        model = genai.GenerativeModel(model_name="gemini-2.5-flash")
        
        prompt = """
        You are an expert AI Forensic Analyst. Analyze this video footage carefully.
        Provide a structured report containing:
        1. A brief summary of the event.
        2. Key timestamps of critical actions (e.g., '00:12 - Vehicle enters frame').
        3. A detailed description of objects, people, and actions visible.
        4. Any potential anomalies or safety concerns.
        
        Format the output clearly in plain text.
        """
        
        response = model.generate_content([video_file, prompt])
        
        # Clean up: Delete file from Google Cloud (save space)
        genai.delete_file(video_file.name)
        
        return response.text

    except Exception as e:
        print(f"--- AI ERROR: {e} ---")
        return f"Analysis Failed: {str(e)}"