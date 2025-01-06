from calendar import monthrange, month_name, day_name
from PIL import Image, ImageDraw, ImageFont

def generate_calendar_image(year, month, output_file=None):
    # Set default output file name if not provided
    if output_file is None:
        output_file = f"{month_name[month].lower()}_{year}_calendar.png"

    # Create a new image with a white background
    img_width, img_height = 800, 600
    image = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(image)

    # Load a font
    font = ImageFont.truetype("arial.ttf", 20)  # Replace with a valid font path if needed
    title_font = ImageFont.truetype("arial.ttf", 28)

    # Draw the title (Month and Year)
    title_text = f"{month_name[month]} {year}"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((img_width - title_width) / 2, 20), title_text, fill="black", font=title_font)

    # Draw the days of the week header
    days = [day_name[i][:3] for i in range(7)]  # Short names like Mon, Tue, etc.
    cell_width = img_width // 7
    for i, day in enumerate(days):
        day_bbox = draw.textbbox((0, 0), day, font=font)
        day_width = day_bbox[2] - day_bbox[0]
        x = i * cell_width + (cell_width - day_width) / 2
        draw.text((x, 80), day, fill="black", font=font)

    # Get the days in the month
    _, num_days = monthrange(year, month)
    first_day_of_month = monthrange(year, month)[0]  # 0 = Monday, 6 = Sunday

    # Draw the days grid
    y_offset = 120
    cell_height = 60
    day = 1
    for row in range(6):  # Max 6 rows in a calendar
        for col in range(7):
            if row == 0 and col < first_day_of_month:
                continue
            if day > num_days:
                break
            x = col * cell_width + 10
            y = y_offset + row * cell_height
            draw.text((x, y), str(day), fill="black", font=font)
            day += 1

    # Save the image
    image.save(output_file)
    print(f"Calendar saved as {output_file}")

# Example usage
generate_calendar_image(2025, 1)  # February 2025

