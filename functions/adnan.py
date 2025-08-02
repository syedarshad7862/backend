import pdb
import re
import pypdfium2 as pdfium
import pytesseract
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
from datetime import datetime
from dateutil.parser import parse
import pdb

# Define key mappings for extracting variations of fields
KEY_MAPPINGS = {
    "full_name": ["Full Name","Name"],
    "gender": ["gender", "sex"],
    "marital_status": [ "marital status", "relationship status"],
    "age": ["age",  "years old"],
    "dob": ["date of birth", "DOB", "birthdate"],
    "height": ["Height & weight","height"],
    "complexion": ["complexion", "skin_tone", "skin tone"],
    "education": ["education", "qualification", "degree", "Educational Background"],
    "occupation": ["profession", "job", "profession Details", "Work", "current job", "occupation", "current position"],
    "father_name": ["father's name & occupation", "father", "dad's name", "family details", "Father's Name"],
    "father_occupation": [ "father's job", "father profession","Father's Name"],
    "mother_name": [ "mother name", "mom's name", "mother", "Mother's Name & Profession","Mother's Name"],
    "siblings": ["Sister's","siblings", "brothers and sisters", "family members","sister's"],
    "residence": ["residence",  "current address", "living place", "current location"],
    "native_place": ["Current Location", "hometown", "birthplace", "nationality"],
    "mother_tongue": ["mother tongue", "first_language", "native language"],
    "visits_dargah": ["visits dargah", "dargah visits", "visits shrines"],
    "sect": ["sect", "religious sect", "community", "religion", "caste"],
    "preferences": ["partner preferences", "personality", "other traits", "religious expectation", "age range", "age preference", "education preference", "profession preference", "location preference", "religious & cultural values", "religious values", "height preferences","Expectations"],
    "contact_no": ["Contact No's", "phone number", "mobile number", "Phone", "email", "Address", "email ID"]
}


def convert_pdf_to_images(file_path, scale=300/72):
    pdf_file = pdfium.PdfDocument(file_path)
    page_indices = [i for i in range(len(pdf_file))]
    
    renderer = pdf_file.render(
        pdfium.PdfBitmap.to_pil,
        page_indices=page_indices,
        scale=scale,
    )
    
    list_final_images = []
    
    for i, image in zip(page_indices, renderer):
        image_byte_array = BytesIO()
        image.save(image_byte_array, format='jpeg', optimize=True)
        image_byte_array = image_byte_array.getvalue()
        list_final_images.append({i: image_byte_array})
    
    return list_final_images

def display_images(list_dict_final_images):
    all_images = [list(data.values())[0] for data in list_dict_final_images]
    
    for index, image_bytes in enumerate(all_images):
        image = Image.open(BytesIO(image_bytes))
        plt.figure(figsize=(image.width / 100, image.height / 100))
        plt.title(f"----- Page Number {index+1} -----")
        plt.imshow(image)
        plt.axis("off")
        plt.show()

def extract_text_with_pytesseract(list_dict_final_images):
    image_list = [list(data.values())[0] for data in list_dict_final_images]
    image_content = []
    
    for image_bytes in image_list:
        image = Image.open(BytesIO(image_bytes))
        raw_text = str(pytesseract.image_to_string(image))
        image_content.append(raw_text)
    
    return "\n".join(image_content)

def extract_birth_year(text):
    """
    Extract birth year from text using multiple patterns
    Returns the 4-digit year if found, otherwise None
    """
    patterns = [
        r"(?P<dob>\d{1,2}[/-]\d{1,2}[/-](?P<year>\d{2,4}))",  # DD/MM/YYYY or MM/DD/YYYY
        r"(?P<dob>(?P<year>\d{4})[/-]\d{1,2}[/-]\d{1,2})",    # YYYY/MM/DD
        r"(?P<dob>\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(?P<year>\d{4}))",
        r"(?P<dob>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]\s+\d{1,2}\s,?\s+(?P<year>\d{4}))",
        r"\b(19[0-9]{2}|20[0-2][0-9])\b"  # Standalone year
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            year = match.group("year") if "year" in match.groupdict() else match.group(1)
            if len(year) == 2:  # Handle 2-digit years (assuming 19XX or 20XX)
                year = f"19{year}" if int(year) > 30 else f"20{year}"
            return int(year)
    
    return None

def calculate_age_from_text(text):
    """
    Calculate age from text containing date of birth
    Returns age if successful, otherwise None
    """
    current_year = datetime.now().year
    
    # First try explicit DOB fields
    dob_keys = ["dob", "date of birth", "birthdate", "Date of Birth"]
    for dob_key in dob_keys:
        pattern = rf"{re.escape(dob_key)}\s*[:;_–-]+\s*(?P<date>.+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            birth_year = extract_birth_year(match.group("date"))
            if birth_year:
                return current_year - birth_year
    
    # Search entire text for date patterns if no explicit DOB field found
    birth_year = extract_birth_year(text)
    if birth_year:
        return current_year - birth_year
    
    return None

def extract_profile_data(text):
    profile_data= {key: "" for key in KEY_MAPPINGS}
    
    # Extract regular profile fields
    for key, variations in KEY_MAPPINGS.items():
        for variation in variations:
            pattern = rf"{re.escape(variation)}\s*[:;_–-]+\s*(.+)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_value = match.group(1).strip()
                if profile_data[key]:
                    profile_data[key] += "; " + extracted_value
                else:
                    profile_data[key] = extracted_value
    
    # Enhanced age calculation
    calculated_age = calculate_age_from_text(text)
    if calculated_age:
        # Only update age if not found or if calculated age seems more reliable
        if not profile_data["age"] or (isinstance(profile_data["age"], str) and not profile_data["age"].isdigit()):
            profile_data["age"] = str(calculated_age)
        elif profile_data["age"] and profile_data["age"].isdigit():
            # If both exist, keep the one that's more recent (smaller age)
            existing_age = int(profile_data["age"])
            profile_data["age"] = str(min(existing_age, calculated_age))
    
    return profile_data

def save_text_to_file(text, filename="extracted_text.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)

def save_dict_to_file(data, filename="profile_data.py"):
    with open(filename, "w", encoding="utf-8") as file:
        file.write("profile_data = {\n")
        for key, value in data.items():
            file.write(f'    "{key}": "{value if value is not None else ""}",\n')
        file.write("}\n")

# Main Execution Flow
# if __name__ == "__main__":
#     pdf_images = convert_pdf_to_images(r"c:\Users\ThinkPad\Desktop\python projects\pdfs\00000072-MATRIMONIAL BIO DATA-2.pdf")
#     # pdb.set_trace()
#     display_images(pdf_images)
#     extracted_text = extract_text_with_pytesseract(pdf_images)
#     print(extracted_text)
#     save_text_to_file(extracted_text, "extracted_text.txt")
#     print("Extracted text saved to extracted_text.txt")

#     profile = extract_profile_data(extracted_text)
#     print(profile)
#     save_dict_to_file(profile, "profile_data.py")
#     print("Profile data saved to profile_data.py")  #very good
    

# pdf_images = convert_pdf_to_images(r"c:\Users\ThinkPad\Desktop\python projects\pdfs\00000072-MATRIMONIAL BIO DATA-2.pdf")
#     # pdb.set_trace()
#     display_images(pdf_images)
#     extracted_text = extract_text_with_pytesseract(pdf_images)
#     save_text_to_file(extracted_text, "extracted_text.txt")
#     print("Extracted text saved to extracted_text.txt")

#     profile = extract_profile_data(extracted_text)
#     save_dict_to_file(profile, "profile_data.py")
#     print("Profile data saved to profile_data.py") 





import pdb
import re
import pypdfium2 as pdfium
import pytesseract
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
from datetime import datetime
from dateutil.parser import parse
import pdb
from concurrent.futures import ThreadPoolExecutor

# Define key mappings for extracting variations of fields
KEY_MAPPINGS = {
    "full_name": ["Full Name","Name"],
    "gender": ["gender", "sex"],
    "marital_status": [ "marital status", "relationship status"],
    "age": ["age",  "years old"],
    "dob": ["date of birth", "DOB", "birthdate"],
    "height": ["Height & weight","height"],
    "complexion": ["complexion", "skin_tone", "skin tone"],
    "education": ["education", "qualification", "degree", "Educational Background"],
    "occupation": ["profession", "job", "profession Details", "Work", "current job", "occupation", "current position"],
    "father_name": ["father's name & occupation","Father’s Name", "father", "dad's name", "family details", "Father's Name"],
    "father_occupation": [ "father's job", "father profession","Father's Name"],
    "mother_name": [ "mother name", "mom's name", "mother", "Mother's Name & Profession","Mother's Name"],
    "siblings": ["Sister's","siblings", "brothers and sisters", "family members","sister's"],
    "residence": ["residence",  "current address", "living place", "current location", "Area"],
    "native_place": ["Current Location", "hometown", "birthplace", "nationality"],
    "mother_tongue": ["mother tongue", "first_language", "native language"],
    "visits_dargah": ["visits dargah", "dargah visits", "visits shrines"],
    "religion": ["Religion"],
    "sect": ["sect", "religious sect", "community", "Maslak", "Maslak Sect", "caste"],
    "preferences": ["partner preferences", "personality", "other traits", "religious expectation", "age range", "age preference", "education preference", "profession preference", "location preference", "religious & cultural values", "religious values", "height preferences","Expectations"],
    "contact_no": ["Contact No's","Contact", "phone number", "mobile number", "Phone", "email", "Address", "email ID"]
}


def convert_pdf_to_images(file_path, scale=300/72):
    pdf_file = pdfium.PdfDocument(file_path)
    page_indices = [i for i in range(len(pdf_file))]
    
    renderer = pdf_file.render(
        pdfium.PdfBitmap.to_pil,
        page_indices=page_indices,
        scale=scale,
    )
    
    list_final_images = []
    
    for i, image in zip(page_indices, renderer):
        image_byte_array = BytesIO()
        image.save(image_byte_array, format='jpeg', optimize=True)
        image_byte_array = image_byte_array.getvalue()
        list_final_images.append({i: image_byte_array})
    
    return list_final_images

def display_images(list_dict_final_images):
    all_images = [list(data.values())[0] for data in list_dict_final_images]
    
    for index, image_bytes in enumerate(all_images):
        image = Image.open(BytesIO(image_bytes))
        plt.figure(figsize=(image.width / 100, image.height / 100))
        plt.title(f"----- Page Number {index+1} -----")
        plt.imshow(image)
        plt.axis("off")
        plt.show()

def ocr_image(image_bytes):
    image = Image.open(BytesIO(image_bytes)).convert("L")
    return pytesseract.image_to_string(image, lang="eng")

def extract_text_with_pytesseract(list_dict_final_images):
    image_list = [list(data.values())[0] for data in list_dict_final_images]

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(ocr_image, image_list))

    return "\n".join(results)

def extract_birth_year(text):
    """
    Extract birth year from text using multiple patterns
    Returns the 4-digit year if found, otherwise None
    """
    patterns = [
        r"(?P<dob>\d{1,2}[/-]\d{1,2}[/-](?P<year>\d{2,4}))",  # DD/MM/YYYY or MM/DD/YYYY
        r"(?P<dob>(?P<year>\d{4})[/-]\d{1,2}[/-]\d{1,2})",    # YYYY/MM/DD
        r"(?P<dob>\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(?P<year>\d{4}))",
        r"(?P<dob>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]\s+\d{1,2}\s,?\s+(?P<year>\d{4}))",
        r"\b(19[0-9]{2}|20[0-2][0-9])\b"  # Standalone year
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            year = match.group("year") if "year" in match.groupdict() else match.group(1)
            if len(year) == 2:  # Handle 2-digit years (assuming 19XX or 20XX)
                year = f"19{year}" if int(year) > 30 else f"20{year}"
            return int(year)
    
    return None

def calculate_age_from_text(text):
    """
    Calculate age from text containing date of birth
    Returns age if successful, otherwise None
    """
    current_year = datetime.now().year
    
    # First try explicit DOB fields
    dob_keys = ["dob", "date of birth", "birthdate", "Date of Birth"]
    for dob_key in dob_keys:
        pattern = rf"{re.escape(dob_key)}\s*[:;_–-]+\s*(?P<date>.+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            birth_year = extract_birth_year(match.group("date"))
            if birth_year:
                return current_year - birth_year
    
    # Search entire text for date patterns if no explicit DOB field found
    birth_year = extract_birth_year(text)
    if birth_year:
        return current_year - birth_year
    
    return None

def extract_profile_data(text):
    profile_data= {key: "" for key in KEY_MAPPINGS}
    
    # Extract regular profile fields
    for key, variations in KEY_MAPPINGS.items():
        for variation in variations:
            pattern = rf"{re.escape(variation)}\s*[:;_–-]+\s*(.+)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_value = match.group(1).strip()
                if profile_data[key]:
                    profile_data[key] += "; " + extracted_value
                else:
                    profile_data[key] = extracted_value
    
    # Enhanced age calculation
    calculated_age = calculate_age_from_text(text)
    if calculated_age:
        # Only update age if not found or if calculated age seems more reliable
        if not profile_data["age"] or (isinstance(profile_data["age"], str) and not profile_data["age"].isdigit()):
            profile_data["age"] = str(calculated_age)
        elif profile_data["age"] and profile_data["age"].isdigit():
            # If both exist, keep the one that's more recent (smaller age)
            existing_age = int(profile_data["age"])
            profile_data["age"] = str(min(existing_age, calculated_age))
    
    return profile_data

def save_text_to_file(text, filename="extracted_text.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)

def save_dict_to_file(data, filename="profile_data.py"):
    with open(filename, "w", encoding="utf-8") as file:
        file.write("profile_data = {\n")
        for key, value in data.items():
            file.write(f'    "{key}": "{value if value is not None else ""}",\n')
        file.write("}\n")

# Main Execution Flow
# if __name__ == "__main__":
#     pdf_images = convert_pdf_to_images(r"c:\Users\ThinkPad\Desktop\python projects\pdfs\00000072-MATRIMONIAL BIO DATA-2.pdf")
#     # pdb.set_trace()
#     display_images(pdf_images)
#     extracted_text = extract_text_with_pytesseract(pdf_images)
#     print(extracted_text)
#     save_text_to_file(extracted_text, "extracted_text.txt")
#     print("Extracted text saved to extracted_text.txt")

#     profile = extract_profile_data(extracted_text)
#     print(profile)
#     save_dict_to_file(profile, "profile_data.py")
#     print("Profile data saved to profile_data.py")  #very good
    

# @router.post("/upload-pdf")
# async def upload_pdf_db(request: Request ,file: UploadFile = File(...), user_db=Depends(get_authenticated_agent_db)):
#     try:    
#         file_contants = await file.read() 
#         user, db = user_db
#         try:
#             images_data = convert_pdf_to_images(file_contants,scale=300/72)
#         except Exception as e:
#             print(f"error logs {e}")
#             return JSONResponse(status_code=500, content={"error": f"PDF rendering failed: {str(e)}"})
        
#         try:
#             extracted_text = extract_text_with_pytesseract(images_data)
#             print(extracted_text)
#         except Exception as e:
#             return JSONResponse(status_code=500, content={"error": f"OCR failed: {str(e)}"})
        
#         result = None
#         try:
#             # await db["user_profiles"].create_index("profile_id", unique=True)
#             profile_data = extract_profile_data(extracted_text)
#             profile_data["row_text"] = extracted_text
#             print(profile_data)
#             result = await db["user_profiles"].insert_one(profile_data)
#             print(result)
#             profile_id = str(result.inserted_id)[-6:].lower()
#             # chars = string.ascii_lowercase + string.digits
#             # unique_id = f"USR-{''.join(random.choices(chars, k=6))}"
#             # print(f" u id : {unique_id}")
#             await db["user_profiles"].update_one(
#                 {"_id": result.inserted_id},
#                 {"$set": {"profile_id": profile_id}}
#             )
            
#             return JSONResponse(status_code=200, content={"message": "PDF Upload Successfully.", "profile_id": profile_id, "_id":result.inserted_id})
#         except DuplicateKeyError:
#             if result:
#                 await db["user_profiles"].delete_one({"_id": result.inserted_id})
#             raise HTTPException(status_code=409, detail="Profile ID conflict. Try again.")
#     except Exception as e:
#         if result:
#             await db["user_profiles"].delete_one({"_id": result.inserted_id})
#         logger.error(f"Create profile failed: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error.")