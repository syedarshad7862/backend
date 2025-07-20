import pypdfium2 as pdfium
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import math
from concurrent.futures import ThreadPoolExecutor

# --- Page Rendering Function ---
def render_page(file_path, page_number, scale):
    pdf = pdfium.PdfDocument(file_path)
    page = pdf[page_number]
    image = page.render(scale=scale).to_pil()

    image_byte_array = BytesIO()
    image.save(image_byte_array, format='jpeg')  # Faster: skip optimize=True
    return {page_number: image_byte_array.getvalue()}

# --- Convert PDF to JPEG Images in Memory ---
def convert_pdf_to_images(file_path, scale=150/72, max_pages=None):
    pdf = pdfium.PdfDocument(file_path)
    total_pages = len(pdf)
    del pdf  # Avoid memory leak due to multithreaded re-load

    page_indices = list(range(total_pages))
    if max_pages:
        page_indices = page_indices[:max_pages]

    # Run rendering in parallel
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(render_page, file_path, i, scale)
            for i in page_indices
        ]

    results = [future.result() for future in futures]
    return results

# --- Display All Images in Grid ---
def display_images_grid(list_dict_final_images):
    all_images = [
        Image.open(BytesIO(list(data.values())[0]))
        for data in list_dict_final_images
    ]

    cols = 2
    rows = math.ceil(len(all_images) / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(10, rows * 5))
    axes = axes.flatten()

    for i, image in enumerate(all_images):
        axes[i].imshow(image)
        axes[i].set_title(f"Page {i+1}")
        axes[i].axis('off')

    for j in range(i + 1, len(axes)):
        axes[j].axis('off')

    plt.tight_layout()
    plt.show()



file_path = r"c:\Users\ThinkPad\Desktop\python projects\pdfs\00000072-MATRIMONIAL BIO DATA-2.pdf"  # Replace with actual path

# Step 1: Convert PDF to JPEGs in memory
images_data = convert_pdf_to_images(file_path, scale=150/72, max_pages=4)

# Step 2: Show all images in one grid
display_images_grid(images_data)

print(images_data)
