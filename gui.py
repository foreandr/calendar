import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
from datetime import datetime


class EventManager:
    def __init__(self, json_file):
        self.json_file = json_file
        self.load_events()

    def load_events(self):
        """Load events from the JSON file."""
        if os.path.exists(self.json_file):
            with open(self.json_file, "r") as f:
                data = json.load(f)
                self.events = data.get("events", [])
        else:
            self.events = []

    def save_events(self):
        """Save events to the JSON file."""
        with open(self.json_file, "w") as f:
            json.dump({"events": self.events}, f, indent=4)

    def add_event(self, timestamp, event_text):
        """Add a new event."""
        try:
            # Validate timestamp
            datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            new_event = {"timestamp": timestamp, "event": event_text}
            self.events.append(new_event)
            self.save_events()
        except ValueError:
            raise ValueError("Timestamp must be in the format 'YYYY-MM-DD HH:MM:SS'.")

    def search_events(self, event_string=None):
        """Search for events containing the event string."""
        return [
            event for event in self.events
            if event_string is None or event_string.lower() in event["event"].lower()
        ]

    def delete_event(self, event_to_delete):
        """Delete an event."""
        self.events = [event for event in self.events if event != event_to_delete]
        self.save_events()


class EventGUI:
    def __init__(self, root, manager):
        self.manager = manager

        # Main window setup
        root.title("Event Manager")
        root.state("zoomed")  # Open in fullscreen mode

        # Add event section
        self.add_frame = tk.LabelFrame(root, text="Add Event", padx=10, pady=10)
        self.add_frame.pack(fill="both", padx=10, pady=5)

        # Date Picker
        self.date_label = tk.Label(self.add_frame, text="Date:")
        self.date_label.grid(row=0, column=0, sticky="w")
        self.date_picker = DateEntry(self.add_frame, width=12, background="darkblue", foreground="white", borderwidth=2)
        self.date_picker.grid(row=0, column=1, sticky="w")

        # Time Selector
        self.time_label = tk.Label(self.add_frame, text="Time:")
        self.time_label.grid(row=0, column=2, sticky="w")

        self.hour_var = tk.StringVar()
        self.minute_var = tk.StringVar()
        self.second_var = tk.StringVar()

        self.hour_dropdown = ttk.Combobox(self.add_frame, textvariable=self.hour_var, width=5, values=[f"{i:02}" for i in range(24)])
        self.hour_dropdown.grid(row=0, column=3, sticky="w")
        self.hour_dropdown.set("00")

        self.minute_dropdown = ttk.Combobox(self.add_frame, textvariable=self.minute_var, width=5, values=[f"{i:02}" for i in range(60)])
        self.minute_dropdown.grid(row=0, column=4, sticky="w")
        self.minute_dropdown.set("00")

        self.second_dropdown = ttk.Combobox(self.add_frame, textvariable=self.second_var, width=5, values=[f"{i:02}" for i in range(60)])
        self.second_dropdown.grid(row=0, column=5, sticky="w")
        self.second_dropdown.set("00")

        # Event Title Entry
        self.event_label = tk.Label(self.add_frame, text="Event Title:")
        self.event_label.grid(row=1, column=0, sticky="w")
        self.event_entry = tk.Entry(self.add_frame, width=40)
        self.event_entry.grid(row=1, column=1, columnspan=5, sticky="w")

        self.add_button = tk.Button(self.add_frame, text="Add Event", command=self.add_event)
        self.add_button.grid(row=2, column=0, columnspan=6, pady=5)

        # Search event section
        self.search_frame = tk.LabelFrame(root, text="Search Events", padx=10, pady=10)
        self.search_frame.pack(fill="both", padx=10, pady=5)

        self.search_string_label = tk.Label(self.search_frame, text="Search for Event Title:")
        self.search_string_label.grid(row=0, column=0, sticky="w")
        self.search_string_entry = tk.Entry(self.search_frame, width=30)
        self.search_string_entry.grid(row=0, column=1, sticky="w")

        self.search_button = tk.Button(self.search_frame, text="Search Events", command=self.search_events)
        self.search_button.grid(row=0, column=2, padx=10)

        self.result_box = tk.Listbox(self.search_frame, width=80, height=10)
        self.result_box.grid(row=1, column=0, columnspan=3, pady=5)
        self.result_box.bind("<Delete>", self.delete_event)

        self.delete_button = tk.Button(self.search_frame, text="Delete Selected Event", command=self.delete_event)
        self.delete_button.grid(row=2, column=0, columnspan=3, pady=5)

    def add_event(self):
        """Add an event using input from the GUI."""
        try:
            selected_date = self.date_picker.get_date().strftime("%Y-%m-%d")
            selected_time = f"{self.hour_var.get()}:{self.minute_var.get()}:{self.second_var.get()}"
            timestamp = f"{selected_date} {selected_time}"
            event_text = self.event_entry.get()

            if not event_text:
                raise ValueError("Event text cannot be empty!")

            self.manager.add_event(timestamp, event_text)
            messagebox.showinfo("Success", "Event added successfully!")
            self.event_entry.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def search_events(self):
        """Search for events based on input and display them."""
        try:
            event_string = self.search_string_entry.get() if self.search_string_entry.get() else None
            results = self.manager.search_events(event_string)
            self.result_box.delete(0, tk.END)  # Clear previous results

            for event in results:
                self.result_box.insert(tk.END, f"{event['timestamp']} - {event['event']}")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def delete_event(self, event=None):
        """Delete the selected event from the listbox and JSON file."""
        selection = self.result_box.curselection()
        if not selection:
            return  # No popup on failure either

        selected_event = self.result_box.get(selection[0])
        timestamp, event_text = selected_event.split(" - ", 1)

        for event in self.manager.events:
            if event["timestamp"] == timestamp and event["event"] == event_text:
                self.manager.delete_event(event)
                self.result_box.delete(selection[0])  # Just delete it, no confirmation popup
                break


if __name__ == "__main__":
    json_file = "events.json"
    manager = EventManager(json_file)

    root = tk.Tk()
    app = EventGUI(root, manager)
    root.mainloop()
