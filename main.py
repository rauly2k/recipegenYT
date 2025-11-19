"""
YouTube Recipe Generator - Main Application
Desktop GUI application for extracting recipes from YouTube videos
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import threading
import json
from datetime import datetime
from pathlib import Path

from config import (
    GUI_TEXT,
    AVAILABLE_TAGS,
    OUTPUT_DIR,
    load_api_key,
    save_api_key as save_api_key_to_file
)
from gemini_service import call_gemini_api, is_valid_youtube_url
from recipe_validator import validate_recipe

class YouTubeRecipeGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(GUI_TEXT["window_title"])
        self.root.geometry("800x900")
        self.root.resizable(True, True)

        self.recipes = []
        self.processing = False

        self.setup_ui()
        self.load_saved_api_key()

    def setup_ui(self):
        """Create all GUI components"""

        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        current_row = 0

        # === API Key Section ===
        ttk.Label(main_frame, text=GUI_TEXT["api_key_label"], font=("Arial", 10, "bold")).grid(
            row=current_row, column=0, sticky=tk.W, pady=(0, 5)
        )
        current_row += 1

        api_frame = ttk.Frame(main_frame)
        api_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        api_frame.columnconfigure(0, weight=1)

        self.api_key_entry = ttk.Entry(api_frame, show="*", font=("Arial", 10))
        self.api_key_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        self.save_api_button = ttk.Button(api_frame, text=GUI_TEXT["api_key_save"], command=self.save_api_key)
        self.save_api_button.grid(row=0, column=1)

        current_row += 1

        # === Tags Section ===
        ttk.Label(main_frame, text=GUI_TEXT["tags_label"], font=("Arial", 10, "bold")).grid(
            row=current_row, column=0, sticky=tk.W, pady=(0, 5)
        )
        current_row += 1

        self.tags_text = scrolledtext.ScrolledText(main_frame, height=4, font=("Arial", 9), wrap=tk.WORD)
        self.tags_text.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.tags_text.insert("1.0", ", ".join(AVAILABLE_TAGS))

        current_row += 1

        # === URLs Section ===
        ttk.Label(main_frame, text=GUI_TEXT["urls_label"], font=("Arial", 10, "bold")).grid(
            row=current_row, column=0, sticky=tk.W, pady=(0, 5)
        )
        current_row += 1

        self.urls_text = scrolledtext.ScrolledText(main_frame, height=10, font=("Arial", 10), wrap=tk.WORD)
        self.urls_text.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.urls_text.insert("1.0", GUI_TEXT["urls_placeholder"])
        self.urls_text.bind("<FocusIn>", self.clear_placeholder)

        current_row += 1

        # === Generate Button ===
        self.generate_button = ttk.Button(
            main_frame,
            text=GUI_TEXT["generate_button"],
            command=self.generate_recipes
        )
        self.generate_button.grid(row=current_row, column=0, pady=(0, 15))

        current_row += 1

        # === Progress Section ===
        ttk.Label(main_frame, text=GUI_TEXT["progress_label"], font=("Arial", 10, "bold")).grid(
            row=current_row, column=0, sticky=tk.W, pady=(0, 5)
        )
        current_row += 1

        self.progress_text = scrolledtext.ScrolledText(main_frame, height=8, font=("Consolas", 9),
                                                       wrap=tk.WORD, state=tk.DISABLED)
        self.progress_text.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Configure tags for colored output
        self.progress_text.tag_config("success", foreground="green")
        self.progress_text.tag_config("error", foreground="red")
        self.progress_text.tag_config("warning", foreground="orange")

        current_row += 1

        # === Action Buttons ===
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=current_row, column=0, pady=(0, 10))

        self.preview_button = ttk.Button(button_frame, text=GUI_TEXT["preview_button"],
                                        command=self.preview_recipes, state=tk.DISABLED)
        self.preview_button.grid(row=0, column=0, padx=(0, 10))

        self.export_button = ttk.Button(button_frame, text=GUI_TEXT["export_button"],
                                       command=self.export_recipes, state=tk.DISABLED)
        self.export_button.grid(row=0, column=1)

        # Configure row weights for resizing
        for i in range(current_row + 1):
            if i in [4, 7]:  # URLs and Progress areas
                main_frame.rowconfigure(i, weight=1)

    def clear_placeholder(self, event):
        """Clear placeholder text on focus"""
        if self.urls_text.get("1.0", tk.END).strip() == GUI_TEXT["urls_placeholder"].strip():
            self.urls_text.delete("1.0", tk.END)

    def load_saved_api_key(self):
        """Load previously saved API key"""
        api_key = load_api_key()
        if api_key:
            self.api_key_entry.insert(0, api_key)

    def save_api_key(self):
        """Save API key to config file"""
        api_key = self.api_key_entry.get().strip()
        if api_key:
            save_api_key_to_file(api_key)
            self.log_progress("✓ Cheie API salvată", "success")
        else:
            messagebox.showwarning("Atenție", "Vă rugăm să introduceți o cheie API validă.")

    def log_progress(self, message: str, tag: str = ""):
        """Add message to progress log"""
        self.progress_text.config(state=tk.NORMAL)
        if tag:
            self.progress_text.insert(tk.END, message + "\n", tag)
        else:
            self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.see(tk.END)
        self.progress_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def validate_inputs(self):
        """Validate user inputs"""
        # Check API key
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            return False, GUI_TEXT["error_no_api_key"], []

        # Get and validate URLs
        urls_text = self.urls_text.get("1.0", tk.END).strip()
        if not urls_text or urls_text == GUI_TEXT["urls_placeholder"].strip():
            return False, GUI_TEXT["error_no_urls"], []

        urls = [line.strip() for line in urls_text.split("\n") if line.strip()]

        # Validate YouTube URLs
        valid_urls = []
        for url in urls:
            if is_valid_youtube_url(url):
                valid_urls.append(url)
            else:
                self.log_progress(GUI_TEXT["error_invalid_url"].format(url=url), "error")

        if not valid_urls:
            return False, "Nu s-au găsit URL-uri YouTube valide.", []

        return True, api_key, valid_urls

    def generate_recipes(self):
        """Start recipe generation process"""
        if self.processing:
            return

        # Validate inputs
        is_valid, result, urls = self.validate_inputs()
        if not is_valid:
            messagebox.showerror("Eroare", result)
            return

        api_key = result

        # Get tags
        tags_text = self.tags_text.get("1.0", tk.END).strip()
        available_tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

        # Clear previous results
        self.recipes = []
        self.progress_text.config(state=tk.NORMAL)
        self.progress_text.delete("1.0", tk.END)
        self.progress_text.config(state=tk.DISABLED)

        # Start processing in background thread
        self.processing = True
        self.generate_button.config(state=tk.DISABLED)

        thread = threading.Thread(
            target=self.process_urls,
            args=(urls, api_key, available_tags),
            daemon=True
        )
        thread.start()

    def process_urls(self, urls: list, api_key: str, available_tags: list):
        """Process YouTube URLs (runs in background thread)"""
        try:
            self.log_progress("Se inițializează Gemini API...")

            for i, url in enumerate(urls, 1):
                self.log_progress(f"\nSe procesează video {i}/{len(urls)}: {url}")

                try:
                    # Call Gemini API
                    recipe_json = call_gemini_api(url, available_tags, api_key)

                    # Validate recipe
                    is_valid, error_msg = validate_recipe(recipe_json, available_tags)

                    if not is_valid:
                        self.log_progress(f"✗ Validare eșuată: {error_msg}", "error")
                        continue

                    # Check if confirmation needed
                    if recipe_json.get('no_transcript_warning', False):
                        # Schedule confirmation dialog on main thread
                        result = {"accepted": False, "processed": False}
                        self.root.after(0, lambda r=recipe_json, res=result: self.show_confirmation_dialog(r, res))

                        # Wait for dialog to be processed
                        import time
                        while not result["processed"]:
                            time.sleep(0.1)

                        if result["accepted"]:
                            self.recipes.append(recipe_json)
                            self.log_progress(f"✓ Rețetă acceptată: {recipe_json['title']}", "success")
                        else:
                            self.log_progress(f"✗ Rețetă respinsă de utilizator", "warning")
                    else:
                        self.recipes.append(recipe_json)
                        self.log_progress(f"✓ Rețetă generată: {recipe_json['title']}", "success")

                except Exception as e:
                    self.log_progress(GUI_TEXT["error_processing"].format(error=str(e)), "error")
                    continue

            # Finished
            self.log_progress(f"\n{GUI_TEXT['success_message'].format(count=len(self.recipes))}", "success")

            # Enable export buttons
            if self.recipes:
                self.root.after(0, self.enable_export_buttons)

        finally:
            self.processing = False
            self.root.after(0, lambda: self.generate_button.config(state=tk.NORMAL))

    def show_confirmation_dialog(self, recipe_json: dict, result: dict):
        """Show confirmation dialog for recipes without transcript"""
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title(GUI_TEXT["confirmation_title"])
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()

        # Warning message
        warning_label = ttk.Label(dialog, text=GUI_TEXT["confirmation_warning"],
                                 font=("Arial", 10), foreground="orange")
        warning_label.pack(pady=10)

        # Recipe preview
        preview_frame = ttk.Frame(dialog)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        preview_text = scrolledtext.ScrolledText(preview_frame, wrap=tk.WORD, font=("Arial", 9))
        preview_text.pack(fill=tk.BOTH, expand=True)

        # Format recipe preview
        preview_content = f"""
Titlu: {recipe_json['title']}
Descriere: {recipe_json['description']}

Ingrediente: {len(recipe_json['ingredients'])}
Pași: {len(recipe_json['instructions'])}
Timp total: {recipe_json['totalTime']} minute
Dificultate: {recipe_json['difficulty']}
Etichete: {', '.join(recipe_json['tags'])}

Ingrediente detaliate:
"""
        for ing in recipe_json['ingredients']:
            preview_content += f"  - {ing['name']}: {ing['quantity']} {ing['unit']}\n"

        preview_content += "\nInstrucțiuni:\n"
        for i, step in enumerate(recipe_json['instructions'], 1):
            preview_content += f"  {i}. {step}\n"

        preview_text.insert("1.0", preview_content)
        preview_text.config(state=tk.DISABLED)

        # Action buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        def accept():
            result["accepted"] = True
            result["processed"] = True
            dialog.destroy()

        def reject():
            result["accepted"] = False
            result["processed"] = True
            dialog.destroy()

        ttk.Button(button_frame, text=GUI_TEXT["confirmation_accept"],
                  command=accept).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=GUI_TEXT["confirmation_reject"],
                  command=reject).pack(side=tk.LEFT, padx=5)

        # Handle window close
        def on_closing():
            result["accepted"] = False
            result["processed"] = True
            dialog.destroy()

        dialog.protocol("WM_DELETE_WINDOW", on_closing)

    def enable_export_buttons(self):
        """Enable preview and export buttons"""
        self.preview_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.NORMAL)

    def preview_recipes(self):
        """Show preview of generated recipes"""
        if not self.recipes:
            messagebox.showinfo("Info", "Nu există rețete de previzualizat.")
            return

        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Previzualizare Rețete")
        preview_window.geometry("700x600")

        preview_text = scrolledtext.ScrolledText(preview_window, wrap=tk.WORD, font=("Arial", 9))
        preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Format all recipes
        preview_content = f"Total rețete: {len(self.recipes)}\n\n"
        preview_content += "=" * 70 + "\n\n"

        for i, recipe in enumerate(self.recipes, 1):
            preview_content += f"REȚETA #{i}\n"
            preview_content += f"Titlu: {recipe['title']}\n"
            preview_content += f"Categorie: {recipe['category']} | Bucătărie: {recipe['cuisine']}\n"
            preview_content += f"Timp: {recipe['totalTime']} min | Porții: {recipe['servings']}\n"
            preview_content += f"Dificultate: {recipe['difficulty']}\n"
            preview_content += f"Etichete: {', '.join(recipe['tags'])}\n"
            preview_content += "\n" + "=" * 70 + "\n\n"

        preview_text.insert("1.0", preview_content)
        preview_text.config(state=tk.DISABLED)

    def export_recipes(self):
        """Export recipes to JSON file"""
        if not self.recipes:
            messagebox.showinfo("Info", "Nu există rețete de exportat.")
            return

        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=OUTPUT_DIR,
            initialfile=f"recipes_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        if not file_path:
            return

        # Create export structure
        export_data = {
            "metadata": {
                "exportDate": datetime.utcnow().isoformat() + "Z",
                "totalRecipes": len(self.recipes),
                "source": "youtube_recipe_generator_v1.0",
                "targetApp": "mealee"
            },
            "recipes": self.recipes
        }

        # Write to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            self.log_progress(GUI_TEXT["export_success"].format(path=file_path), "success")
            messagebox.showinfo("Succes", f"Rețete exportate cu succes!\n\nFișier: {file_path}")

        except Exception as e:
            self.log_progress(f"✗ Eroare la export: {str(e)}", "error")
            messagebox.showerror("Eroare", f"Eroare la exportul fișierului:\n{str(e)}")

def main():
    root = tk.Tk()
    app = YouTubeRecipeGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
