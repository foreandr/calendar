import os
import ctypes
from datetime import datetime
from PIL import Image
from main import generate_calendar_image_with_events  # Import the function from main.py


def convert_to_bmp(png_path, bmp_path):
    """
    Convert a PNG image to BMP format.
    
    Args:
        png_path (str): Path to the PNG image.
        bmp_path (str): Path to save the BMP image.
    """
    try:
        with Image.open(png_path) as img:
            img = img.convert("RGB")  # Ensure compatibility
            img.save(bmp_path, "BMP")
        print(f"[DEBUG] Converted PNG to BMP: {bmp_path}")
    except Exception as e:
        print(f"[ERROR] Failed to convert PNG to BMP. Error: {e}")
        raise


def set_desktop_background(image_path):
    """
    Set the desktop background to the specified image.
    
    Args:
        image_path (str): Full path to the image file.
    """
    # Ensure the path exists and is absolute
    image_path = os.path.abspath(image_path)

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"The image file '{image_path}' does not exist.")
    
    # Use ctypes to change the desktop wallpaper (Windows only)
    try:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
        print(f"[DEBUG] Desktop background successfully updated to: {image_path}")
    except Exception as e:
        print(f"[ERROR] Failed to set desktop background. Error: {e}")


if __name__ == "__main__":
    # Get the current date, month, and year
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month  # Month as a number
    current_month_name = current_date.strftime("%B").lower()  # Month name for the file

    # Define the calendar folder and image filenames
    calendar_folder = os.path.abspath("calendars/1920x1080")  # Ensure absolute path
    png_image = f"{current_month_name}_{current_year}_calendar.png"
    bmp_image = f"{current_month_name}_{current_year}_calendar.bmp"
    png_path = os.path.join(calendar_folder, png_image)
    bmp_path = os.path.join(calendar_folder, bmp_image)

    # Debug current state
    print(f"[DEBUG] Current date: {current_date}")
    print(f"[DEBUG] Current year: {current_year}, Current month: {current_month} ({current_month_name})")
    print(f"[DEBUG] Preparing to regenerate calendar image at: {png_path}")

    # Regenerate the calendar image
    try:
        json_file = os.path.abspath("events.json")  # Ensure absolute path
        print(f"[DEBUG] Using JSON file at: {json_file}")
        generate_calendar_image_with_events(current_year, current_month, json_file, "calendars")
        print(f"[DEBUG] Calendar image generated successfully at: {png_path}")
    except Exception as e:
        print(f"[ERROR] Failed to generate calendar image. Error: {e}")
        exit(1)

    # Convert the PNG to BMP
    try:
        convert_to_bmp(png_path, bmp_path)
    except Exception as e:
        print(f"[ERROR] Failed to convert PNG to BMP. Error: {e}")
        exit(1)

    # Set the desktop background
    try:
        set_desktop_background(bmp_path)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
