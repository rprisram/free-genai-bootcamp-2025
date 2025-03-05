from youtube_transcript_api import YouTubeTranscriptApi
from typing import Optional, List, Dict
import os


class YouTubeTranscriptDownloader:
    def __init__(self, languages: List[str] = ["ja", "en"]):
        self.languages = languages

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL
        
        Args:
            url (str): YouTube URL
            
        Returns:
            Optional[str]: Video ID if found, None otherwise
        """
        if "v=" in url:
            return url.split("v=")[1][:11]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1][:11]
        return None

    def get_transcript(self, video_id: str) -> Optional[List[Dict]]:
        """
        Download YouTube Transcript
        
        Args:
            video_id (str): YouTube video ID or URL
            
        Returns:
            Optional[List[Dict]]: Transcript if successful, None otherwise
        """
        # Extract video ID if full URL is provided
        if "youtube.com" in video_id or "youtu.be" in video_id:
            video_id = self.extract_video_id(video_id)
            
        if not video_id:
            print("Invalid video ID or URL")
            return None

        print(f"Downloading transcript for video ID: {video_id}")
        
        try:
            return YouTubeTranscriptApi.get_transcript(video_id, languages=self.languages)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

    def save_transcript(self, transcript: List[Dict], filename: str) -> bool:
        """
        Save transcript to file
        
        Args:
            transcript (List[Dict]): Transcript data
            filename (str): Output filename or URL
            
        Returns:
            bool: True if successful, False otherwise
        """
        # If transcript is None, return False
        if not transcript:
            return False
            
        # Extract video ID if URL is provided
        if "youtube.com" in filename or "youtu.be" in filename:
            filename = self.extract_video_id(filename)
            
        if not filename:
            print("Invalid filename or URL")
            return False
            
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Path to transcripts directory (in the same directory as this script)
        transcripts_dir = os.path.join(script_dir, "transcripts")
        
        # Ensure transcripts directory exists
        os.makedirs(transcripts_dir, exist_ok=True)
        
        # Full path to the output file
        filepath = os.path.join(transcripts_dir, f"{filename}.txt")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for entry in transcript:
                    f.write(f"{entry['text']}\n")
            print(f"Transcript saved successfully to {filepath}")
            return True
        except Exception as e:
            print(f"Error saving transcript: {str(e)}")
            return False

def main(video_url, print_transcript=False):
    # Initialize downloader
    downloader = YouTubeTranscriptDownloader()
    
    # Get transcript
    transcript = downloader.get_transcript(video_url)
    
    if transcript:
        # Save transcript
        video_id = downloader.extract_video_id(video_url)
        if downloader.save_transcript(transcript, video_id):
            #Print transcript if True
            if print_transcript:
                # Print transcript
                for entry in transcript:
                    print(f"{entry['text']}")
            return transcript
        else:
            print("Failed to save transcript")
            return None
    else:
        print("Failed to get transcript")
        return None

if __name__ == "__main__":
    video_id = "https://www.youtube.com/watch?v=sY7L5cfCWno&list=PLkGU7DnOLgRMl-h4NxxrGbK-UdZHIXzKQ"  # Extract from URL: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    transcript = main(video_id, print_transcript=True)