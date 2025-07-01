import os
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv

# Load OpenAI API Key Here
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# ===============================  

# Initialize OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)
# ===============================

# --- Function: Encoding User's Image ---# 
def encode_image(image_path):
    with open(image_path, "rb") as image:
        return base64.b64encode(image.read()).decode()
# ===============================

# --- Functions: Find Similar Celebrities --- #
def find_similar_celebrities(user_image_path, user_gender):
    response = client.responses.create(
       model="gpt-4.1",
       input=[
           {
               "role": "user",
               "content" : [
                   {
                       "type": "input_text",
                       "text": """ You are a professional facial aesthetics analyst with expertise in recognizing celebrity lookalikes.
                                    You will be given:
                                    - A clear image of a human face
                                    - The user's gender

                                    Your job is to analyze the face and return exactly 4 celebrities the person resembles:
                                    - 2 must be **Iranian/Persian**
                                    - 2 must be **foreign (non-Iranian)**

                                    For each celebrity:
                                    - Provide the **Iranian/Persian** celebrity names in **Persian**
                                    - Provide the **foreign (non-Iranian)** celebrity names in **English**
                                    - Provide exactly **3 reasons** for all celebrities in **Persian** (even for the **foreign (non_Iranian)** celebrities) that explain why the user resembles them along with an estimate percentage of similarity
                                    - The reasons should focus on facial structure, symmetry, features like eyes, jawline, lips, etc.
                                    - The reasons must be realistic, well-written, and based on visual traits

                                    ⚠️ Output Format (required):
                                    Return only a **Python list of dictionaries**, structured like this:
                                    ```python
                                    [
                                    {
                                        "name": "Celebrity Name 1",
                                        "reasons": [
                                        "دلیل اول به فارسی",
                                        "دلیل دوم به فارسی",
                                        "دلیل سوم به فارسی"
                                        ]
                                    },
                                    ...
                                    {
                                        "name": "Celebrity Name 4",
                                        "reasons": [
                                        "دلیل اول به فارسی",
                                        "دلیل دوم به فارسی",
                                        "دلیل سوم به فارسی"
                                        ]
                                    }
                                    ] 
                                    ```
                                    """
                   },
                   {
                       "type": "input_text",
                       "text": f"user's gender is: {user_gender}"   
                   },
                   {
                       "type": "input_image",
                       "image_url": f"data:image/jpeg;base64,{encode_image(user_image_path)}",
                   }
               ]
           }
       ] 
    )
    
    found_celebrities = response.output[0].content[0].text.strip() 
    
    if "```python" in found_celebrities:
        found_celebrities = found_celebrities.replace("```python", "")
    if "```" in found_celebrities:
        found_celebrities = found_celebrities.replace("```", "")
        
    try:
        found_celebrities = json.loads(found_celebrities)
        #print(type(found_celebrities))
        #print(found_celebrities)
    except json.JSONDecodeError as e:
        #print("🚫 JSON parsing error:", e)
        #print("🔎 Raw input:", found_celebrities)
        return "NOT FOUND"
    
        
    return found_celebrities
# ===============================

