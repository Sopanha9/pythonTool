import customtkinter as ctk
from tkinter import filedialog
from rembg import remove
from PIL import Image, ImageTk
import io
import os

class BackgroundRemover(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Background Remover Pro")
        self.geometry("1000x700")

        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create sidebar frame with widgets
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Sidebar content
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Background\nRemover Pro",
                                     font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Buttons
        self.load_button = ctk.CTkButton(self.sidebar_frame, text="Load Image",
                                       command=self.open_image)
        self.load_button.grid(row=1, column=0, padx=20, pady=10)

        self.process_button = ctk.CTkButton(self.sidebar_frame, text="Remove Background",
                                          command=self.process_image)
        self.process_button.grid(row=2, column=0, padx=20, pady=10)
        self.process_button.configure(state="disabled")

        self.save_button = ctk.CTkButton(self.sidebar_frame, text="Save Image",
                                       command=self.save_image)
        self.save_button.grid(row=3, column=0, padx=20, pady=10)

        # Status label in sidebar
        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="Ready",
                                       font=ctk.CTkFont(size=12))
        self.status_label.grid(row=5, column=0, padx=20, pady=(10, 20))

        # Create main frame for image display
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Create frames for original and processed images
        self.original_frame = ctk.CTkFrame(self.main_frame)
        self.original_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.processed_frame = ctk.CTkFrame(self.main_frame)
        self.processed_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Labels for images
        self.original_label = ctk.CTkLabel(self.original_frame, text="Original Image")
        self.original_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.input_preview = ctk.CTkLabel(self.original_frame, text="No image loaded")
        self.input_preview.grid(row=1, column=0, padx=10, pady=5)

        self.processed_label = ctk.CTkLabel(self.processed_frame, text="Processed Image")
        self.processed_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.output_preview = ctk.CTkLabel(self.processed_frame, text="No image processed")
        self.output_preview.grid(row=1, column=0, padx=10, pady=5)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        self.progress_bar.set(0)

        # Initialize variables
        self.input_image = None
        self.output_image = None

    def update_preview(self, image, preview_label):
        # Resize image while maintaining aspect ratio
        display_size = (400, 400)
        image_copy = image.copy()
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.LANCZOS
        image_copy.thumbnail(display_size, resample)
        photo = ImageTk.PhotoImage(image_copy)
        preview_label.configure(image=photo, text="")
        preview_label.image = photo

    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.webp *.bmp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            try:
                self.input_image = Image.open(file_path)
                self.update_preview(self.input_image, self.input_preview)
                self.process_button.configure(state="normal")
                self.status_label.configure(text="Image loaded")
                self.progress_bar.set(0)
            except Exception as e:
                self.show_error("Failed to load image", str(e))

    def process_image(self):
        if not self.input_image:
            return

        self.process_button.configure(state="disabled")
        self.progress_bar.set(0.25)
        self.status_label.configure(text="Processing...")

        try:
            # Ensure a consistent format (PNG) and proper mode
            img = self.input_image.convert("RGBA")
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format="PNG")
            input_bytes = img_byte_arr.getvalue()

            # Remove background
            output = remove(input_bytes)

            # rembg may return bytes or a PIL Image; handle both
            if isinstance(output, bytes):
                self.output_image = Image.open(io.BytesIO(output)).convert("RGBA")
            elif isinstance(output, Image.Image):
                self.output_image = output.convert("RGBA")
            else:
                # try to interpret as bytes fallback
                self.output_image = Image.open(io.BytesIO(bytes(output))).convert("RGBA")

            # Update preview
            self.update_preview(self.output_image, self.output_preview)
            self.status_label.configure(text="Background removed")

        except Exception as e:
            self.show_error("Processing failed", str(e))
            self.status_label.configure(text="Error processing")
        finally:
            self.progress_bar.set(1.0)
            self.process_button.configure(state="normal")

    def save_image(self):
        if not self.output_image:
            self.show_error("No image to save", "Please process an image first")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ],
            title="Save the output image"
        )

        if file_path:
            try:
                self.output_image.save(file_path, "PNG")
                self.status_label.configure(text="Image saved")
                self.show_success("Success", f"Image saved to:\n{file_path}")
            except Exception as e:
                self.show_error("Failed to save", str(e))

    def show_error(self, title, message):
        error_window = ctk.CTkToplevel(self)
        error_window.title(title)
        error_window.geometry("300x150")
        error_window.transient(self)
        error_window.grab_set()
        
        ctk.CTkLabel(error_window, text=message, wraplength=250).pack(pady=20)
        ctk.CTkButton(error_window, text="OK", command=error_window.destroy).pack(pady=10)

    def show_success(self, title, message):
        success_window = ctk.CTkToplevel(self)
        success_window.title(title)
        success_window.geometry("300x150")
        success_window.transient(self)
        success_window.grab_set()
        
        ctk.CTkLabel(success_window, text=message, wraplength=250).pack(pady=20)
        ctk.CTkButton(success_window, text="OK", command=success_window.destroy).pack(pady=10)

def main():
    app = BackgroundRemover()
    app.mainloop()

if __name__ == "__main__":
   main()

