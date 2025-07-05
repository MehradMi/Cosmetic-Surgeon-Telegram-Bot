import os
from dotenv import load_dotenv
import base64
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key = OPENAI_API_KEY)

# Function For Creating Files With The FilesAPI 
def create_file(file_path):
  with open(file_path, "rb") as file_content:
    result = client.files.create(
      file=file_content,
      purpose="vision",
    )
    return result.id
  
# Function For Encoding The Picture
def encode_picture(file_path):
  with open(file_path, "rb") as file_content:
    return base64.b64encode(file_content.read()).decode("utf-8")

def analyze_faces_find_similarities(user_image_path, celeb_list):
    try:
        # Build the prompt content
        content = [
            {"type": "text", "text": "Find the celebrity from the following images that looks most similar to the person in the first image. Then suggest cosmetic surgeries that could help them achieve a similar appearance. Provide only the name of the matching celebrity in the English Language and everything else including the suggestions in the Persian language."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_picture(user_image_path)}"}}
        ]
        for celeb in celeb_list:
            content.append(
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_picture(celeb["image_path"])}"}}
            )

        # Call OpenAI
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": content}]
        )

        reply = response.choices[0].message.content.strip()

        # Extract matching celebrity name
        matched_celeb = None
        for celeb in celeb_list:
            if celeb["name"].lower() in reply.lower():
                matched_celeb = celeb
                break

        # Return both the suggestions and the matched celeb image path
        if matched_celeb:
            return {
                "celebrity_name": matched_celeb["name"],
                "celebrity_image": matched_celeb["image_path"],
                "suggestions": reply
            }
        else:
            return {
                "celebrity_name": None,
                "celebrity_image": None,
                "suggestions": reply
            }

    except Exception as e:
        return {"error": str(e)}