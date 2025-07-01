import os
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

# --- Function: Check Whether It's URL or File Path -- #
def url_or_path(celebrity_image_url_or_path):
    if "http" in celebrity_image_url_or_path:
         return celebrity_image_url_or_path
    return f"data:image/jpeg;base64,{encode_image(celebrity_image_url_or_path)}" 
# ===============================

# --- Functions: Give Surgery Suggestions Based On User Image and Choice --- #
def surgery_suggestions(user_image_path, celebrity_image_url_or_path):
   celebrity_image_url_or_path = url_or_path(celebrity_image_url_or_path) 
   response = client.responses.create(
       model="gpt-4.1",
       input=[
           {
               "role": "user",
               "content": [
                   {
                       "type": "input_text",
                       "text": """
                                    You are a highly experienced and world-renowned facial aesthetics and cosmetic surgery expert.
                                    You will be given two face images:
                                    - First image : the user's face
                                    - Second image B: the face of a celebrity the user wants to resemble

                                    Your task:
                                    - Carefully analyze and compare the facial features in both images, including:
                                    - Nose shape and structure
                                    - Jawline and chin definition
                                    - Lip size and contour
                                    - Eye shape, distance, and eyelids
                                    - Forehead and brow area
                                    - Cheekbones and facial volume
                                    - Symmetry and proportions

                                    Then:
                                    - Suggest **specific, medically accurate cosmetic surgeries or non-invasive procedures** that can help the person in Image A look more like the person in Image B
                                    - Give **clear, respectful, and professional explanations** of what each procedure does and **why it would help bridge the visual gap**
                                    - Be realistic: avoid suggesting extreme or unsafe transformations

                                    Instructions:
                                    - Use professional terminology (e.g., rhinoplasty, genioplasty, buccal fat removal, blepharoplasty, etc.)
                                    - Write the analysis as a **well-structured paragraph or report**
                                    - Include **multiple procedures**, only if necessary
                                    - Explain the reasoning behind each recommendation in a **natural, informative tone**
                                    - Write the explanation in **Persian (Farsi)** for better localization
                                    - Do not include any other information, disclaimers, or markdown formatting — just the full, clean explanation

                                    Images:
                                    - First image  is the user’s face
                                    - Second image is the celebrity’s face they want to resemble
                       """
                   },
                   {
                       "type": "input_image",
                       "image_url": f"data:image/jpeg;base64,{encode_image(user_image_path)}", 
                   },
                   {
                       "type": "input_image",
                       "image_url": celebrity_image_url_or_path,
                   }
               ]
           } 
       ]
   ) 
   #print(response.output[0].content[0].text.strip())
   return response.output[0].content[0].text.strip() 

# ===============================