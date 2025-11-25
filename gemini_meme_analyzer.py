import os
import io
import pandas as pd
import time
import random # For jitter in exponential backoff
from PIL import Image

# Gemini API imports
import google.generativeai as genai
from google.api_core import exceptions # To catch specific API errors

# --- Configuration ---
# Path to your local folder containing the meme images
LOCAL_IMAGES_FOLDER = "/Users/mihaelacoste/Downloads/ro_memes/memes" # <-- IMPORTANT: Update this path!

# Gemini API Key (set as environment variable for security)
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") 

if not GEMINI_API_KEY:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    print("Please set it before running the script: export GOOGLE_API_KEY='YOUR_API_KEY'")
    exit()

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash" # Or "gemini-1.5-pro" for potentially better results but higher cost

# --- Rate Limiting Parameters ---
MAX_RETRIES = 3    # Enough to catch network hiccups
INITIAL_DELAY_SECONDS = 0.5 # Start retries quickly
MAX_DELAY_SECONDS = 5   # Maximum time to wait
JITTER_FACTOR = 0.1     # Keep jitter

# --- Main script logic ---
def analyze_local_memes():
    model = genai.GenerativeModel(MODEL_NAME)
    results = []

    if not os.path.isdir(LOCAL_IMAGES_FOLDER):
        print(f"Error: The specified local images folder does not exist: {LOCAL_IMAGES_FOLDER}")
        return

    print(f"Scanning for images in local folder: {LOCAL_IMAGES_FOLDER}")
    
    # List all files in the directory and filter for common image extensions
    image_files = [f for f in os.listdir(LOCAL_IMAGES_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

    if not image_files:
        print("No image files found in the specified local folder.")
        return

    print(f"Found {len(image_files)} images. Starting analysis...")

    for i, file_name in enumerate(image_files):
        file_path = os.path.join(LOCAL_IMAGES_FOLDER, file_name)

        print(f"\nProcessing {i+1}/{len(image_files)}: {file_name}")

        try:
            with open(file_path, 'rb') as f:
                image_bytes = f.read()

            mime_type = "image/jpeg"
            if file_name.lower().endswith('.png'):
                mime_type = "image/png"
            elif file_name.lower().endswith('.webp'):
                mime_type = "image/webp"

            image_part = {
                'mime_type': mime_type,
                'data': image_bytes
            }

            # --- Define questions and their corresponding CSV column names ---
            # This is the key change for robust mapping!
            question_mappings = [
                {
                    "question_text": "List all prominent individuals or political figures explicitly depicted or strongly implied in this image, separated by commas. Pay special attention to recognizing Romanian politicians like Nicușor Dan, George Simion, Elena Lasconi, Traian Basescu, Marcel Ciolacu, Calin Georgescu. If no specific individual is identifiable, state 'Unknown'.",
                    "csv_column": "who_is_in_images"
                },
                {
                    "question_text": "What is the core political message or theme of this meme? Be concise, using keywords or a short phrase.",
                    "csv_column": "overall_sentiment" # Keep this name as it's useful for sentiment analysis
                },
                {
                    "question_text": "List any specific Romanian political parties, symbols, or major events referenced in this meme, separated by commas. If none, state 'None'.",
                    "csv_column": "romanian_references"
                },
                {
                    "question_text": "Transcribe any visible text in the image. If no text, state 'No text'.",
                    "csv_column": "text_content"
                },
                {
                    "question_text": "Describe the overall tone or sentiment of this meme using single words (e.g., 'satirical', 'critical', 'humorous', 'supportive', 'neutral'), separated by commas.",
                    "csv_column": "visual_sentiment"
                },
                {
                    "question_text": "Describe the key visual characteristics and style of this image using keywords (e.g., 'photograph', 'cartoon', 'drawing', 'collage', 'screenshot', 'hand-drawn', 'digital art', 'monochromatic', 'vibrant', 'simple', 'complex'), separated by commas.",
                    "csv_column": "visual_characteristics"
                }
            ]
            # Extract just the questions for the model prompt
            questions_for_model = [mapping["question_text"] for mapping in question_mappings]

            meme_data = {
                'file_name': file_name,
                'who_is_in_images': '',
                'overall_sentiment': '',
                'romanian_references': '',
                'text_content': '',
                'visual_sentiment': '',
                'visual_characteristics': ''
            }

            for mapping in question_mappings:
                question = mapping["question_text"]
                csv_column = mapping["csv_column"]

                retries = 0
                answer = "Error: Could not retrieve answer." # Initialize answer before the loop
                while retries < MAX_RETRIES:
                    try:
                        full_prompt = [image_part, question]
                        response = model.generate_content(full_prompt)
                        
                        if response.candidates and response.candidates[0].content.parts:
                            answer = response.candidates[0].content.parts[0].text
                        else:
                            answer = "No clear answer or content received."
                        break
                    
                    except exceptions.ResourceExhausted as e:
                        retries += 1
                        delay = min(
                            INITIAL_DELAY_SECONDS * (2 ** (retries - 1)),
                            MAX_DELAY_SECONDS
                        )
                        delay += random.uniform(-delay * JITTER_FACTOR, delay * JITTER_FACTOR)
                        delay = max(1, delay)

                        print(f"  Rate limit exceeded (429). Retrying in {delay:.2f} seconds... (Attempt {retries}/{MAX_RETRIES})")
                        print(f"  Original error: {e}")
                        time.sleep(delay)
                        
                        if retries == MAX_RETRIES:
                            print(f"  Max retries ({MAX_RETRIES}) reached for {file_name} - {question}. Skipping this question.")
                            answer = "Failed to get answer due to repeated rate limits."
                    
                    except Exception as e:
                        print(f"  An unexpected error occurred for {file_name} - {question}: {e}")
                        answer = f"Error: {e}"
                        break
                
                # Assign answer to the dynamically chosen CSV column
                meme_data[csv_column] = answer
                
                print(f"  Q: {question[:50]}...")
                print(f"  A: {answer[:100]}...")

            results.append(meme_data)

        except Exception as e:
            print(f"Error reading or processing {file_name}: {e}")
            continue

    if results:
        df = pd.DataFrame(results)
        output_csv_path = "romanian_meme_analysis_results_local.csv"
        df.to_csv(output_csv_path, index=False, encoding='utf-8')
        print(f"\nAnalysis complete! Results saved to {output_csv_path}")
    else:
        print("\nNo results to save.")

if __name__ == "__main__":
    analyze_local_memes()