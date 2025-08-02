import fitz  # PyMuPDF
import requests
import re
import ast
import json
from PIL import Image # Import Pillow for image manipulation
import pytesseract # Import pytesseract for OCR
import os # Import os for path manipulation


# --- IMPORTANT: Ensure you have PyMuPDF, Pillow, and pytesseract installed:
# pip install PyMuPDF Pillow pytesseract
# Also, Tesseract OCR engine must be installed on your system for pytesseract to work.
# ---

# --- Step 1: Extract text from PDF (now with OCR for images) ---
def extract_text_from_pdf(pdf_path):
    """
    Extracts all text from a given PDF file, including performing OCR on embedded images.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The concatenated text from all pages and images of the PDF.
    """
    doc = fitz.open(pdf_path)
    all_text_parts = []

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)

        # 1. Extract text directly from the page
        # page = cast(fitz.Page, doc.load_page(page_num))
        page_text = page.get_text() # type: ignore
        if page_text:
            all_text_parts.append(page_text)

        # 2. Extract images and perform OCR
        images = page.get_images(full=True) # Get all images on the page
        for img_index, img in enumerate(images):
            xref = img[0] # The XREF of the image
            try:
                # Extract the pixmap (pixel map) of the image
                pix = fitz.Pixmap(doc, xref)

                # Convert pixmap to a PIL Image
                # PyMuPDF pixmaps can have different number of components (n) and alpha channels.
                # We need to handle these conversions carefully for PIL Image.
                if pix.n == 1: # Grayscale
                    mode = "L"
                elif pix.n == 3: # RGB
                    mode = "RGB"
                elif pix.n == 4: # CMYK or RGBA
                    # If it's CMYK, convert to RGB first
                    if pix.colorspace and pix.colorspace.name == "DeviceCMYK":
                        pix = fitz.Pixmap(fitz.csRGB, pix) # Convert CMYK to RGB
                        mode = "RGB"
                    else: # Assume RGBA
                        mode = "RGBA"
                else:
                    # Fallback for other modes, try converting to RGB
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                    mode = "RGB"

                pil_image = Image.frombytes(mode, (pix.width, pix.height), pix.samples)

                # Perform OCR using pytesseract
                # You might need to set the path to the tesseract executable if it's not in your PATH
                # pytesseract.pytesseract.tesseract_cmd = r'<path_to_your_tesseract_executable>'
                ocr_text = pytesseract.image_to_string(pil_image)
                if ocr_text:
                    all_text_parts.append(f"\n--- OCR Text from Image {img_index + 1} on Page {page_num + 1} ---\n")
                    all_text_parts.append(ocr_text)
                    all_text_parts.append("\n---------------------------------------------------\n")

            except Exception as e:
                print(f"Error processing image {img_index} on page {page_num}: {e}")
                # Continue to next image/page even if one image fails

    doc.close() # Close the PDF document
    return "\n".join(all_text_parts)

# --- New function: Extract text from an image file (JPG, PNG, etc.) ---
def extract_text_from_image(image_path):
    """
    Extracts text from an image file using OCR.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The text extracted from the image.
    """
    try:
        img = Image.open(image_path)
        # Perform OCR using pytesseract
        # pytesseract.pytesseract.tesseract_cmd = r'<path_to_your_tesseract_executable>'
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        raise Exception(f"Error processing image file {image_path}: {e}")


# --- Step 2: Send text to LLaMA 3.2 on Groq ---
def send_to_llama(text, api_key):
    """
    Sends the extracted text to the LLaMA 3.2 model on Groq API
    to extract structured biodata information.

    Args:
        text (str): The biodata text extracted from the PDF or image.
        api_key (str): Your Groq API key.

    Returns:
        str: The raw string response from the LLaMA model,
             expected to be a Python dictionary string.

    Raises:
        Exception: If the Groq API returns a non-200 status code.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Define the prompt for the LLM to extract specific biodata fields
    prompt = f"""
You are acting as a responsible Muslim matchmaker whose duty is to extract complete and structured biodata for matrimonial purposes, strictly adhering to Islamic values and cultural sensitivities.
Your task is to carefully extract and return all personal details and match preferences in the form of a valid Python dictionary.
- full_name
- gender
- marital_status
- age
- date_of_birth
- height
- complexion
- education
- occupation
- father_name
- father_occupation
- mother_name
- siblings
- residence
- native_place
- mother_tongue
- go_to_dargah
- sect
- maslak_sect
- preferences
- contact_no
-'pref_age_range'
-'pref_marital_status'
-'pref_height'
-'pref_complexion'
-'pref_education'
-'pref_work_job'
-'pref_father_occupation'
-'pref_no_of_siblings'
-'pref_native_place'
-'pref_mother_tongue'
-'pref_go_to_dargah'

Format your output exactly like this (as Python dictionary):
{{
  'full_name': 'John Doe',
  'gender': 'Male',
  'marital_status': 'Single',
  'age': 28,
  'date_of_birth': '1995-05-15',
  'height': '5\'10"',
  'complexion': 'Fair',
  'education': 'Bachelor\'s Degree',
  'occupation': 'Software Engineer',
  'father_name': 'Robert Doe',
  'father_occupation': 'Businessman',
  'mother_name': 'Mary Doe',
  'siblings': 2,
  'residence': 'New York',
  'native_place': 'Chicago',
  'mother_tongue': 'English',
  'go_to_dargah': None,
  'sect': None,
  'preferences': 'Non-smoker, vegetarian',
  'contact_no': '+1 123-456-7890'
  'pref_age_range': '22-26',
  'pref_marital_status': 'Unmarried',
  'pref_height': "5'2\",
  'pref_complexion': 'Wheatish',
  'pref_education': 'POSTGRADUATE',
  'pref_work_job': 'Teacher',
  'pref_father_occupation': 'Businessman',
  'pref_no_of_siblings': '3',
  'pref_native_place': 'Hyderabad',
  'pref_mother_tongue': 'Urdu',
  'pref_go_to_dargah': 'Yes',
  'pref_maslak_sect': 'Sunni',
  'pref_deendari': 'Religious'
}}

Here is the biodata text:
{text}
"""

    payload = {
        "model": "llama3-70b-8192",  # Using the 70B model as specified
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 800  # Limiting the response token count
    }

    response = requests.post(url, headers=headers, json=payload)

    # Check for successful API response
    if response.status_code != 200:
        raise Exception(f"Groq API Error {response.status_code}: {response.json()}")

    return response.json()['choices'][0]['message']['content']

# --- Step 3: Safely parse model output into a Python dictionary ---
def safe_parse_dict(text):
    """
    Safely parses a string containing a Python dictionary into a dictionary object.
    Handles potential markdown code blocks, common quote issues, and JSON null/true/false.

    Args:
        text (str): The string output from the LLM.

    Returns:
        dict: The parsed Python dictionary.

    Raises:
        ValueError: If no dictionary structure is found or parsing fails.
    """
    print(f"\n--- Raw Model Response for Parsing ---\n{text}\n--------------------------------------\n") # Added for debugging

    try:
        # Remove markdown code blocks (e.g., python ... , json ... , )
        cleaned = re.sub(r"(?:python|json)?\s*\n", "", text, flags=re.DOTALL).strip("`").strip()
        # Replace smart quotes with standard quotes for proper parsing
        cleaned = cleaned.replace("“", "\"").replace("”", "\"")
        cleaned = cleaned.replace("‘", "'").replace("’", "'")

        # Replace JSON 'null' with Python 'None'
        cleaned = cleaned.replace("null", "None")
        # Replace JSON 'true'/'false' with Python 'True'/'False'
        cleaned = cleaned.replace("true", "True").replace("false", "False")

        # Use regex to find the dictionary structure. This regex is more robust
        # to leading/trailing text outside the dictionary.
        match = re.search(r"\{[\s\S]*?\}", cleaned)
        if not match:
            raise ValueError("No dictionary structure found in model output.")

        dict_string = match.group(0)
        print(f"\n--- Cleaned Dictionary String for ast.literal_eval ---\n{dict_string}\n----------------------------------------------------\n") # Added for debugging

        # Safely evaluate the string as a Python literal (dictionary)
        return ast.literal_eval(dict_string)

    except (ValueError, SyntaxError) as e:
        raise ValueError(f"Failed to parse dictionary from model response: {e}. Raw text was: '{text}'")
    except Exception as e:
        raise ValueError(f"An unexpected error occurred during parsing: {e}. Raw text was: '{text}'")


# --- Step 4: Save dictionary to file (JSON or raw text) ---
def save_to_file(data, filename="output.json", as_json=True):
    """
    Saves the extracted data dictionary to a file.

    Args:
        data (dict): The dictionary to save.
        filename (str): The name of the file to save to.
        as_json (bool): If True, saves as JSON; otherwise, saves as raw string.
    """
    with open(filename, "w", encoding="utf-8") as f:
        if as_json:
            json.dump(data, f, indent=2) # Save as pretty-printed JSON
        else:
            f.write(str(data)) # Save as raw string representation of the dictionary
    print(f"\n✅ Output saved to {filename}")

# --- Step 5: New function to save dictionary to a Python file ---
def save_dict_to_file(data, filename="profile_data.py"):
    """
    Saves the extracted data dictionary to a Python file in a specific format
    as a variable assignment.

    Args:
        data (dict): The dictionary to save.
        filename (str): The name of the Python file to save to.
    """
    with open(filename, "w", encoding="utf-8") as file:
        file.write("profile_data = {\n")
        for key, value in data.items():
            # Handle string values by enclosing them in quotes
            # Handle None values as 'None' in Python
            # Handle integer values directly
            if isinstance(value, str):
                file.write(f'    "{key}": "{value}",\n')
            elif value is None:
                file.write(f'    "{key}": None,\n')
            elif isinstance(value, (int, float, bool)): # Handle numbers and booleans directly
                file.write(f'    "{key}": {value},\n')
            else: # For lists, dicts, etc., use repr for safe string representation
                file.write(f'    "{key}": {repr(value)},\n')
        file.write("}\n")
    print(f"\n✅ Output saved to {filename}")


# --- Step 6: Run the full pipeline ---
# Define the path to your input file (can be PDF or image)
# Example for PDF:
input_path = r"c:\Users\ThinkPad\Desktop\python projects\pdfs\00000439-PHOTO-2025-05-05-19-21-50.jpg"
# Example for JPG:
# input_path = "/content/sample_biodata.jpg" # <--- Uncomment and change to your JPG path

# Define your Groq API key
api_key = "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"

# try:
#     extracted_text = ""
#     file_extension = os.path.splitext(input_path)[1].lower()

#     if file_extension == '.pdf':
#         print("Extracting text from PDF (including OCR for images)...")
#         extracted_text = extract_text_from_pdf(input_path)
#     elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
#         print(f"Extracting text from image file ({file_extension.upper()})...")
#         extracted_text = extract_text_from_image(input_path)
#     else:
#         raise ValueError("Unsupported file type. Please provide a PDF or an image file (JPG, PNG, etc.).")

#     print("\n--- Extracted Text (including OCR) ---")
#     # Print only the first 1000 characters to avoid overwhelming the console
#     print(extracted_text[:1000] + ("..." if len(extracted_text) > 1000 else ""))

#     print("\nSending text to LLaMA 3.2 for extraction...")
#     response_text = send_to_llama(extracted_text, api_key)

#     print("Parsing output into dictionary...")
#     extracted_data = safe_parse_dict(response_text)

#     print("\n--- Final Extracted Dictionary ---")
#     print(extracted_data)

#     # --- Save to file options ---
#     # Option 1: Save as JSON format
#     save_to_file(extracted_data, "output.json", as_json=True)

#     # Option 2: Save as raw dictionary string in a text file
#     # save_to_file(extracted_data, "output.txt", as_json=False)

#     # Option 3: Save as a Python file with a variable assignment
#     save_dict_to_file(extracted_data, "profile_data.py")

# except Exception as e:
#     print("\n--- Error ---")
#     print(str(e))
    



# @router.post("/upload-biodata")
# async def upload_biodata(request: Request, file: UploadFile = File(...), user_db=Depends(get_authenticated_agent_db)):
#     user, db = user_db
#     result = None

#     try:
#         # Save uploaded file temporarily
#         suffix = os.path.splitext(file.filename)[1]
#         with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
#             tmp.write(await file.read())
#             tmp_path = tmp.name

#         # Determine if it's image or PDF
#         if suffix.lower() == ".pdf":
#             extracted_text = extract_text_from_pdf(tmp_path)
#         else:
#             extracted_text = extract_text_from_image(tmp_path)

#         # Extract structured data from LLaMA via Groq API
#         response_text = send_to_llama(extracted_text, api_key="your_groq_api_key_here")
#         profile_data = safe_parse_dict(response_text)
#         profile_data["row_text"] = extracted_text

#         # Insert into DB
#         result = await db["user_profiles"].insert_one(profile_data)
#         profile_id = str(result.inserted_id)[-6:].lower()
#         await db["user_profiles"].update_one(
#             {"_id": result.inserted_id},
#             {"$set": {"profile_id": profile_id}}
#         )

#         return JSONResponse(status_code=200, content={
#             "message": "Upload successful.",
#             "profile_id": profile_id,
#             "_id": str(result.inserted_id)
#         })

#     except DuplicateKeyError:
#         if result:
#             await db["user_profiles"].delete_one({"_id": result.inserted_id})
#         raise HTTPException(status_code=409, detail="Duplicate profile ID.")
#     except Exception as e:
#         if result:
#             await db["user_profiles"].delete_one({"_id": result.inserted_id})
#         raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
#     finally:
#         # Clean up the temp file
#         if os.path.exists(tmp_path):
#             os.remove(tmp_path)