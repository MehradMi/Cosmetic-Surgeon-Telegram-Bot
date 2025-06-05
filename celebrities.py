import os
# Automatically resolve base path of the project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

MALE_CELEB_IMAGE = os.path.join(BASE_DIR, 'Cosmetic-Surgent-Telegram-Bot', 'Celeb_Images', 'Male')
FEMALE_CELEB_IMAGE = os.path.join(BASE_DIR, 'Cosmetic-Surgent-Telegram-Bot', 'Celeb_Images', 'Female')
# Celebrities
celebrities = {
    "male": [
        {"name": "Brad Pitt", "image_path": f"{MALE_CELEB_IMAGE}/M_Brad_Pitt.jpg"},
        {"name": "Christian Bale", "image_path": f"{MALE_CELEB_IMAGE}/M_Christian_Bale.jpg"},
        {"name": "Jake Gyllenhaal", "image_path": f"{MALE_CELEB_IMAGE}/M_Jake_Gyllenhaal.jpg"},
        {"name": "Leonardo DiCaprio", "image_path": f"{MALE_CELEB_IMAGE}/M_Leonardo_DiCaprio.jpg"},
        {"name": "Matthew McConaughey", "image_path": f"{MALE_CELEB_IMAGE}/M_Matthew_McConaughey.jpg"},
        {"name": "Ryan Gosling", "image_path": f"{MALE_CELEB_IMAGE}/M_Ryan_Gosling.jpg"},
    ],
    "female": [
        {"name": "Ana DE Armas", "image_path": f"{FEMALE_CELEB_IMAGE}/F_Ana_DE_Armas.jpg"},
        {"name": "Angelina Jolie", "image_path": f"{FEMALE_CELEB_IMAGE}/F_Angelina_Jolie.jpg"},
        {"name": "Emma Mackey", "image_path": f"{FEMALE_CELEB_IMAGE}/F_Emma_Mackey.jpg"},
        {"name": "Emma Stone", "image_path": f"{FEMALE_CELEB_IMAGE}/F_Emma_Stone.jpg"},
        {"name": "Emma Watson", "image_path": f"{FEMALE_CELEB_IMAGE}/F_Emma_Watson.jpg"},
        {"name": "Margot Robbie", "image_path": f"{FEMALE_CELEB_IMAGE}/F_Margot_Robbie.jpg"},
        {"name": "Natalie Portman", "image_path": f"{FEMALE_CELEB_IMAGE}/F_Natalie_Portman.jpg"},
        {"name": "Scarlett Johansson", "image_path": f"{FEMALE_CELEB_IMAGE}/F_Scarlett_Johansson.jpg"},
        {"name": "Taylor Swift", "image_path": f"{FEMALE_CELEB_IMAGE}/F_Taylor_Swift.jpg"},
    ]
}