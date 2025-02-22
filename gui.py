import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
from datetime import datetime


### EVENT MANAGER ###
class EventManager:
    def __init__(self, json_file):
        self.json_file = json_file
        self.load_events()

    def load_events(self):
        """Load events from the JSON file."""
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, "r") as f:
                    data = json.load(f)
                    self.events = data.get("events", [])
            except json.JSONDecodeError:
                print(f"[WARNING] {self.json_file} was corrupted. Resetting file.")
                self.events = []
                self.save_events()
        else:
            self.events = []
            self.save_events()

    def save_events(self):
        """Save events to the JSON file."""
        with open(self.json_file, "w") as f:
            json.dump({"events": self.events}, f, indent=4)

    def add_event(self, timestamp, event_text):
        """Add a new event."""
        if not event_text.strip():
            raise ValueError("Event text cannot be empty!")
        new_event = {"timestamp": timestamp, "event": event_text}
        self.events.append(new_event)
        self.save_events()

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


### NOTES MANAGER ###
class NotesManager:
    def __init__(self, json_file):
        self.json_file = json_file
        self.load_notes()

    def load_notes(self):
        """Load notes from the JSON file, handling empty or corrupted files."""
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, "r") as f:
                    data = json.load(f)
                    self.notes = data.get("notes", [])
            except (json.JSONDecodeError, ValueError):
                print(f"[WARNING] {self.json_file} is empty or corrupted. Resetting file.")
                self.notes = []
                self.save_notes()
        else:
            self.notes = []
            self.save_notes()

    def save_notes(self):
        """Save notes to the JSON file."""
        with open(self.json_file, "w") as f:
            json.dump({"notes": self.notes}, f, indent=4)

    def add_note(self, note_text):
        """Add a new note."""
        if not note_text.strip():
            raise ValueError("Note cannot be empty!")
        self.notes.append(note_text)
        self.save_notes()

    def search_notes(self, search_string=None):
        """Search for notes containing a keyword."""
        return [
            note for note in self.notes
            if search_string is None or search_string.lower() in note.lower()
        ]

    def delete_note(self, note_to_delete):
        """Delete a note."""
        self.notes = [note for note in self.notes if note != note_to_delete]
        self.save_notes()


### GUI CLASS ###
class EventGUI:
    def __init__(self, root, event_manager, notes_manager):
        self.event_manager = event_manager
        self.notes_manager = notes_manager

        root.title("Event & Notes Manager")
        root.state("zoomed")  # Fullscreen mode

        ### EVENT SECTION ###
        self.add_event_frame = tk.LabelFrame(root, text="Add Event", padx=10, pady=10)
        self.add_event_frame.pack(fill="both", padx=10, pady=5)

        self.date_label = tk.Label(self.add_event_frame, text="Date:")
        self.date_label.grid(row=0, column=0, sticky="w")
        self.date_picker = DateEntry(self.add_event_frame, width=12)
        self.date_picker.grid(row=0, column=1, sticky="w")

        self.event_label = tk.Label(self.add_event_frame, text="Event Title:")
        self.event_label.grid(row=1, column=0, sticky="w")
        self.event_entry = tk.Entry(self.add_event_frame, width=40)
        self.event_entry.grid(row=1, column=1, columnspan=5, sticky="w")

        self.add_event_button = tk.Button(self.add_event_frame, text="Add Event", command=self.add_event)
        self.add_event_button.grid(row=2, column=0, columnspan=6, pady=5)

        self.event_listbox = tk.Listbox(root, width=80, height=10)
        self.event_listbox.pack(padx=10, pady=5)
        self.event_listbox.bind("<Delete>", self.delete_event)

        self.delete_event_button = tk.Button(root, text="Delete Selected Event", command=self.delete_event)
        self.delete_event_button.pack(pady=5)

        ### NOTES SECTION ###
        self.notes_frame = tk.LabelFrame(root, text="Manage Notes", padx=10, pady=10)
        self.notes_frame.pack(fill="both", padx=10, pady=5)

        self.note_entry = tk.Entry(self.notes_frame, width=50)
        self.note_entry.grid(row=0, column=0, padx=10)

        self.add_note_button = tk.Button(self.notes_frame, text="Add Note", command=self.add_note)
        self.add_note_button.grid(row=0, column=1)

        self.search_notes_entry = tk.Entry(self.notes_frame, width=30)
        self.search_notes_entry.grid(row=1, column=0, padx=10)

        self.search_notes_button = tk.Button(self.notes_frame, text="Search Notes", command=self.search_notes)
        self.search_notes_button.grid(row=1, column=1)

        self.notes_listbox = tk.Listbox(self.notes_frame, width=80, height=10)
        self.notes_listbox.grid(row=2, column=0, columnspan=2, pady=5)
        self.notes_listbox.bind("<Delete>", self.delete_note)

        self.delete_note_button = tk.Button(self.notes_frame, text="Delete Selected Note", command=self.delete_note)
        self.delete_note_button.grid(row=3, column=0, columnspan=2, pady=5)

    def add_event(self):
        """Add an event."""
        selected_date = self.date_picker.get_date().strftime("%Y-%m-%d")
        event_text = self.event_entry.get()

        if not event_text:
            messagebox.showerror("Error", "Event title cannot be empty.")
            return

        self.event_manager.add_event(selected_date, event_text)
        self.event_listbox.insert(tk.END, f"{selected_date} - {event_text}")

    def delete_event(self, event=None):
        """Delete selected event."""
        selection = self.event_listbox.curselection()
        if selection:
            event_text = self.event_listbox.get(selection[0])
            self.event_manager.delete_event(event_text)
            self.event_listbox.delete(selection[0])

    def add_note(self):
        """Add a note."""
        note_text = self.note_entry.get()
        if not note_text.strip():
            messagebox.showerror("Error", "Note cannot be empty.")
            return

        self.notes_manager.add_note(note_text)
        self.notes_listbox.insert(tk.END, note_text)
        self.note_entry.delete(0, tk.END)

    def search_notes(self):
        """Search for notes."""
        search_text = self.search_notes_entry.get()
        results = self.notes_manager.search_notes(search_text)
        self.notes_listbox.delete(0, tk.END)
        for note in results:
            self.notes_listbox.insert(tk.END, note)

    def delete_note(self, event=None):
        """Delete selected note."""
        selection = self.notes_listbox.curselection()
        if selection:
            note_text = self.notes_listbox.get(selection[0])
            self.notes_manager.delete_note(note_text)
            self.notes_listbox.delete(selection[0])


if __name__ == "__main__":
    root = tk.Tk()
    app = EventGUI(root, EventManager("events.json"), NotesManager("notes.json"))
    root.mainloop()
