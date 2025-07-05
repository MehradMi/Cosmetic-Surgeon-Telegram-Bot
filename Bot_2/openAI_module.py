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

def analyze_faces(user_image_path, celebrity_image_path):
  try:
    response = client.chat.completions.create(
      model="gpt-4-turbo",
      messages=[
        {
          "role": "system",
          "content": "You are an expert cosmetic surgeon who analyzes faces and suggests procedures."
        },
        {
          "role": "user",
          "content": [
            {"type": "text", "text": "Suggest cosmetic surgeries that could make the first person look like the second and respond in the Persian Language."},
            {"type": "image_url", "image_url": {"url" : f"data:image/jpeg;base64,{encode_picture(user_image_path)}"}},
            {"type": "image_url", "image_url": {"url" : f"data:image/jpeg;base64,{encode_picture(celebrity_image_path)}"}}
          ]
        }
      ]
    )
    return response.choices[0].message.content.strip()

  except Exception as e:
    return f"Error: {e}"
