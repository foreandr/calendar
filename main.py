import json
from calendar import monthrange, month_name, day_name
from PIL import Image, ImageDraw, ImageFont
import os
from data import ASPECT_RATIOS
from datetime import datetime


def load_all_events(json_file):
    """Load all events from a JSON file."""
    with open(json_file, "r") as f:
        data = json.load(f)
    return data["events"]


def filter_events_for_month(events, year, month):
    """Filter events for the specified year and month using the timestamp."""
    return [
        event for event in events
        if datetime.strptime(event["timestamp"], "%Y-%m-%d %H:%M:%S").year == year and
           datetime.strptime(event["timestamp"], "%Y-%m-%d %H:%M:%S").month == month
    ]


def prepare_event_map(events):
    """Convert a list of events into a dictionary for quick lookup."""
    event_map = {}
    for event in events:
        # Extract day, month, and year from the timestamp
        event_date = datetime.strptime(event["timestamp"], "%Y-%m-%d %H:%M:%S")
        date_key = (event_date.day, event_date.month, event_date.year)
        if date_key not in event_map:
            event_map[date_key] = []
        # Add only the event title
        event_map[date_key].append(event["event"])
    return event_map


def create_output_folders(base_folder, width, height):
    """Create a folder for the specified aspect ratio."""
    ratio_folder = os.path.join(base_folder, f"{width}x{height}")
    os.makedirs(ratio_folder, exist_ok=True)
    return ratio_folder


def wrap_text(text, font, max_width):
    """Wrap text into multiple lines to fit within the specified width."""
    words = text.split()
    lines = []
    current_line = words[0]

    for word in words[1:]:
        test_line = f"{current_line} {word}"
        width = font.getbbox(test_line)[2]  # Use getbbox for width measurement
        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

def draw_calendar_image(draw, width, height, year, month, event_map):
    """
    Draw the calendar on the given image with highlighting for the current day.
    """
    font = ImageFont.truetype("arial.ttf", 20)
    title_font = ImageFont.truetype("arial.ttf", 28)
    event_font = ImageFont.truetype("arial.ttf", 16)

    # Get the current date
    current_date = datetime.now()
    current_date = datetime(2025, 1, 17)  # Hardcoded for testing
    current_day = current_date.day if current_date.year == year and current_date.month == month else None

    # Draw title (Month and Year)
    title_text = f"{month_name[month]} {year}"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_width) / 2, 20), title_text, fill="black", font=title_font)

    # Draw days of the week header
    days = [day_name[i][:3] for i in range(7)]
    cell_width = width // 7
    for i, day in enumerate(days):
        day_bbox = draw.textbbox((0, 0), day, font=font)
        day_width = day_bbox[2] - day_bbox[0]
        x = i * cell_width + (cell_width - day_width) / 2
        draw.text((x, 80), day, fill="black", font=font)

    # Get days in the month
    _, num_days = monthrange(year, month)
    first_day_of_month = monthrange(year, month)[0]  # 0 = Monday, 6 = Sunday

    # Define the highlight color and text color
    highlight_color = (220, 220, 220)  # Light gray for highlighting
    text_color = "red"  # Red text for the current day

    # Draw grid and add events
    y_offset = 120
    cell_height = (height - y_offset) // 6
    day = 1
    for row in range(6):  # Max 6 rows in a calendar
        for col in range(7):
            if row == 0 and col < first_day_of_month:
                continue
            if day > num_days:
                break

            x = col * cell_width
            y = y_offset + row * cell_height

            # Highlight the current day box
            if day == current_day:
                draw.rectangle(
                    [(x, y), (x + cell_width, y + cell_height)],
                    fill=highlight_color
                )
                day_text_color = text_color
            else:
                day_text_color = "black"

            # Draw the day number
            draw.text((x + 10, y + 5), str(day), fill=day_text_color, font=font)

            # Check for events in the event map
            if (day, month, year) in event_map:
                event_list = event_map[(day, month, year)]
                for i, event_text in enumerate(event_list):
                    wrapped_lines = wrap_text(event_text, event_font, cell_width - 20)
                    for j, line in enumerate(wrapped_lines):
                        text_color = "red" if day == current_day else "blue"
                        draw.text((x + 10, y + 25 + (i * 25) + (j * 20)), line, fill=text_color, font=event_font)

            day += 1

            
def generate_calendar_image_with_events(year, month, json_file, output_folder="calendars"):
    """Generate calendar images for specified aspect ratios."""
    # Load all events from JSON and filter for the month
    all_events = load_all_events(json_file)
    events = filter_events_for_month(all_events, year, month)
    event_map = prepare_event_map(events)

    for width, height in ASPECT_RATIOS:
        # Create output folder for this aspect ratio
        ratio_folder = create_output_folders(output_folder, width, height)

        # Create a new image
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        # Draw the calendar
        draw_calendar_image(draw, width, height, year, month, event_map)

        # Save the image
        output_file = os.path.join(ratio_folder, f"{month_name[month].lower()}_{year}_calendar.png")
        image.save(output_file)
        print(f"Calendar saved as {output_file}")


if __name__ == "__main__":
    # Path to the JSON file containing all events
    json_file = "events.json"

    # Generate calendar for February 2025
    generate_calendar_image_with_events(2025, 1, json_file)
