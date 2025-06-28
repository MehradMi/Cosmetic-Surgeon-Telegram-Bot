import base64
from openai import OpenAI
from dotenv import load_dotenv

# Load OpenAI API Key Here
load_dotenv()
OPENAI_API_KEY - os.getenv("OPENAI_API_KEY")
# =========================

client = OpenAI(api_key=OPENAI_API_KEY)

# Function For Encoding The User's Image
def encode_image(image_path):
    with open(image_path, "rb") as image:
        return base64.b64encode(image.read()).decode()

def verify_user_image(user_image_path):
    response = client.responses.create(
        model="gpt-4.1",
        input=[
           {
               "role" : "user",
               "content" : [
                   {
                    "type": "input_text", 
                    "text": """ You are an expert in computer vision and face detection. You have been given an uploaded image and must analyze it to determine if it is suitable for further celebrity resemblance and cosmetic analysis. 
                                Instructions:

                                Analyze the image to detect if it contains a human face.

                                Confirm if:

                                    1. There is exactly one clearly visible face.

                                    2. The face is of adequate quality for further analysis (well-lit, not heavily obscured or blurred).

                                If any of these conditions are NOT met, respond the error message string: "NOT OK".

                                If the image is acceptable, respond with a single word: "OK".

                            Do NOT provide any additional commentary, reasoning, or extraneous text beyond the error message or "OK".
                    """
                    },
                   {
                      "type": "input_image",
                      "image_url": f"data:image/jpeg;base64,{encode_image(user_image_path)}",
                   },
               ],
           } 
        ],
    )