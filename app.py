# app.py

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
import sys
import string
import os
import threading
import numpy as np
# NEW: Import the theming library
import sv_ttk

# Import our logic modules from the 'core' folder
from logic import gather_file_contents
from enhanced_audio import EnhancedAudioProcessor


# Ensure console encoding supports emojis on Windows PowerShell
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass





class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("AI Context Builder")
        self.geometry("1000x700")
        
        # A variable to "remember" the last saved file path
        self.saved_filepath = None
        
        self.audio_processor = EnhancedAudioProcessor()
        threading.Thread(target=self.audio_processor.load_model, daemon=True).start()

        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=1)
        
        self.tree = ttk.Treeview(left_frame) 
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewOpen>>', self.on_tree_open)
        self.tree.bind("<Button-1>", self.toggle_selection)
        
        self.setup_initial_tree()
        
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=3)

        prompt_label = ttk.Label(right_frame, text="Your Prompt:")
        prompt_label.pack(pady=(5, 2), padx=10, anchor="w")

        self.prompt_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, height=10)
        self.prompt_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        self.prompt_text.config(background="#282828", foreground="#ffffff", insertbackground="white")

        button_frame = ttk.Frame(right_frame)
        button_frame.pack(pady=10, padx=10, fill=tk.X)

        self.status_label = ttk.Label(button_frame, text="Ready.")
        self.status_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.record_btn = ttk.Button(button_frame, text="🎤 Start Recording", command=self.toggle_recording)
        self.record_btn.pack(side=tk.LEFT)

        self.save_btn = ttk.Button(button_frame, text="💾 Save to File...", command=self.save_preview_to_file)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.generate_btn = ttk.Button(button_frame, text="✨ Generate", command=self.generate_and_copy)
        self.generate_btn.pack(side=tk.RIGHT)

    def save_preview_to_file(self):
        """
        Saves the content of the preview area. Asks for a path the first time,
        then remembers and uses that path for subsequent saves.
        """
        content_to_save = self.prompt_text.get("1.0", tk.END).strip()
        if not content_to_save:
            messagebox.showwarning("Empty Preview", "There is no content in the preview box to save.")
            return

        # Check if we need to ask for the path (first time saving)
        if self.saved_filepath is None:
            path_to_save = filedialog.asksaveasfilename(
                title="Choose Save Location for AI Context",
                initialfile="ai_context.txt",
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            # If the user cancels the dialog, stop here.
            if not path_to_save:
                return
            # Remember the chosen path for the next time.
            self.saved_filepath = path_to_save
        else:
            # If we've saved before, just use the remembered path.
            path_to_save = self.saved_filepath

        # Now, write the content to the determined path.
        try:
            with open(path_to_save, "w", encoding="utf-8") as f:
                f.write(content_to_save)
            messagebox.showinfo("Success", f"File saved successfully to:\n{path_to_save}")
        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred while saving the file:\n{e}")

    def toggle_selection(self, event):
        """Allow clicking on label (text/image) to toggle selection and open/close directories."""
        item_id = self.tree.identify_row(event.y)
        element = self.tree.identify_element(event.x, event.y)
        if not item_id:
            return

        # Only intercept clicks on the label area; let indicator clicks behave normally
        if element in ('text', 'image'):
            # Toggle selection
            if item_id in self.tree.selection():
                self.tree.selection_remove(item_id)
            else:
                self.tree.selection_add(item_id)

            # Determine if the clicked item represents a directory
            values = self.tree.item(item_id, "values")
            is_directory = False
            if values:
                try:
                    is_directory = Path(values[0]).is_dir()
                except Exception:
                    is_directory = False

            if is_directory:
                # Toggle open/close state
                currently_open = self.tree.item(item_id, "open")
                self.tree.item(item_id, open=not currently_open)

                # If opening, populate children when a dummy is present
                if not currently_open:
                    # Ensure focus so on_tree_open operates on this node
                    self.tree.focus(item_id)
                    children = self.tree.get_children(item_id)
                    if children and self.tree.item(children[0], "text") == "dummy":
                        self.on_tree_open(None)

            return "break"

    def setup_initial_tree(self):
        if sys.platform == "win32":
            for drive in string.ascii_uppercase:
                path = Path(f"{drive}:\\")
                if path.exists(): self.add_node(parent="", path=path)
        else:
            self.add_node(parent="", path=Path.home())
            self.add_node(parent="", path=Path('/'))
    
    def add_node(self, parent, path):
        try:
            node_id = self.tree.insert(parent, "end", text=path.name or str(path), values=[str(path)])
            if path.is_dir(): self.tree.insert(node_id, "end", text="dummy")
        except PermissionError: pass
            
    def on_tree_open(self, event):
        item_id = self.tree.focus()
        children = self.tree.get_children(item_id)
        if not children or self.tree.item(children[0], "text") != "dummy": return
        self.tree.delete(children[0])
        parent_path = Path(self.tree.item(item_id, "values")[0])
        try:
            for path in sorted(parent_path.iterdir()): self.add_node(parent=item_id, path=path)
        except PermissionError: self.tree.insert(item_id, "end", text="[Access Denied]")
            
    def generate_and_copy(self):
        """Generates a full preview and copies to clipboard. Prompt is optional."""
        user_prompt = self.prompt_text.get("1.0", tk.END).strip()
        selected_items = self.tree.selection()
        if not user_prompt and not selected_items:
            messagebox.showwarning("Warning", "Please provide a prompt or select at least one file.")
            return
        file_paths = [Path(self.tree.item(i, "values")[0]) for i in selected_items if self.tree.item(i, "values") and Path(self.tree.item(i, "values")[0]).is_file()]
        output_parts = []
        if user_prompt:
            output_parts.append(f"--- USER PROMPT ---\n\n{user_prompt}\n\n")
        if file_paths:
            root_path = Path(os.path.commonpath([str(p) for p in file_paths]))
            if root_path.is_file(): root_path = root_path.parent
            file_context = gather_file_contents(file_paths, root_path)
            output_parts.append(f"--- CONTEXT FILES ---\n\n{file_context}")
        final_output = "".join(output_parts)
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", final_output)
        messagebox.showinfo("Success", "Full context has been generated.")

    def toggle_recording(self):
        if self.audio_processor.is_recording.is_set():
            self.record_btn.config(state="disabled", text="Processing...")
            self.status_label.config(text="Recording stopped. Transcribing...")
            audio_data = self.audio_processor.stop_ptt_recording()
            if audio_data is not None:
                threading.Thread(target=self.process_recorded_audio, args=(audio_data,), daemon=True).start()
            else:
                self.record_btn.config(state="normal", text="🎤 Start Recording")
                self.status_label.config(text="Ready.")
        else:
            self.audio_processor.start_ptt_recording()
            self.record_btn.config(text="⏹️ Stop Recording")
            self.status_label.config(text="🔴 Recording...")

    def process_recorded_audio(self, audio_data: np.ndarray):
        try:
            transcribed_text = self.audio_processor.transcribe_audio(audio_data)
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", transcribed_text)
        except Exception as e:
            messagebox.showerror("Transcription Error", f"Could not process audio: {e}")
        finally:
            self.record_btn.config(state="normal", text="🎤 Start Recording")
            self.status_label.config(text="Ready.")

if __name__ == "__main__":
    app = App()
    sv_ttk.set_theme("dark")
    app.mainloop()