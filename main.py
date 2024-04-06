import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk

# Create a photos directory if it doesn't exist
if not os.path.exists('photos'):
    os.makedirs('photos')

# Create a collages directory if it doesn't exist
if not os.path.exists('static/collages'):
    os.makedirs('static/collages')

def upload_picture():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if file_path:
        # Save the picture to the photos directory
        try:
            with Image.open(file_path) as img:
                img.save(os.path.join('photos', os.path.basename(file_path)))
            messagebox.showinfo("Success", "Picture uploaded successfully")
        except IOError:
            messagebox.showerror("Error", "Failed to save the picture")

def create_collage():
    # Combine all images in the photos directory into a collage
    try:
        images = [Image.open(os.path.join('photos', file)) for file in os.listdir('photos')]
        if not images:
            messagebox.showerror("Error", "No images to create a collage")
            return

        widths, heights = zip(*(i.size for i in images))
        total_width = sum(widths)
        max_height = max(heights)
        collage = Image.new('RGB', (total_width, max_height))

        x_offset = 0
        for im in images:
            collage.paste(im, (x_offset,0))
            x_offset += im.size[0]

        collage_path = os.path.join('static/collages', 'collage.jpg')
        collage.save(collage_path)
        messagebox.showinfo("Success", f"Collage created successfully\n{collage_path}")
    except IOError:
        messagebox.showerror("Error", "Failed to create a collage")

# Tkinter GUI
root = tk.Tk()
root.title("Connected")

# Daily Prompt
prompt_label = tk.Label(root, text="Daily Prompt", font=('Helvetica', 16))
prompt_label.pack()
prompt_text = tk.Text(root, height=4, width=50)
prompt_text.insert(tk.END, "Your daily prompt goes here...")
prompt_text.pack()

# Upload Picture Button
upload_button = tk.Button(root, text="Upload Picture", command=upload_picture)
upload_button.pack()

# Create Collage Button
collage_button = tk.Button(root, text="Create Collage", command=create_collage)
collage_button.pack()

# Start the GUI loop
root.mainloop()
