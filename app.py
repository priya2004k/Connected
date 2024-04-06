from flask import Flask, request, jsonify, render_template, send_from_directory, url_for
from werkzeug.utils import secure_filename
import os
from PIL import Image, ImageOps, ImageEnhance
from typing import List
from flask_cors import CORS
import random

# Flask app setup
app = Flask(__name__, static_folder='static')
CORS(app)

# Directory setup
UPLOAD_FOLDER = 'photos'
COLLAGE_FOLDER = os.path.join(app.static_folder, 'collages')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['COLLAGE_FOLDER'] = COLLAGE_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(COLLAGE_FOLDER):
    os.makedirs(COLLAGE_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # Return a specific success message
        return jsonify({'message': 'Successfully uploaded!'}), 200


def create_collage(listofimages: List[str], n_cols: int = 0, n_rows: int = 0,
                   thumbnail_scale: float = 1.0, thumbnail_width: int = 0, thumbnail_height: int = 0):
    # Validate input columns and rows
    n_cols = max(1, n_cols)
    n_rows = max(1, n_rows)

    # Calculate number of columns and rows if not provided
    if n_cols == 0 and n_rows != 0:
        n_cols = len(listofimages) // n_rows + (len(listofimages) % n_rows > 0)

    if n_rows == 0 and n_cols != 0:
        n_rows = len(listofimages) // n_cols + (len(listofimages) % n_cols > 0)

    if n_rows == 0 and n_cols == 0:
        # Square-like arrangement by default
        n_cols = n_rows = int(len(listofimages) ** 0.5)

    # Calculate thumbnail sizes
    if thumbnail_width == 0:
        thumbnail_width = min([Image.open(p).width for p in listofimages]) // n_cols
    if thumbnail_height == 0:
        thumbnail_height = min([Image.open(p).height for p in listofimages]) // n_rows

    thumbnail_width = int(thumbnail_width * thumbnail_scale)
    thumbnail_height = int(thumbnail_height * thumbnail_scale)

    # Create thumbnails
    all_thumbnails: List[Image.Image] = []
    for p in listofimages:
        img = Image.open(p)
        img.thumbnail((thumbnail_width, thumbnail_height), Image.Resampling.LANCZOS)
        all_thumbnails.append(img)

    # Create a new image for the collage
    collage_width = thumbnail_width * n_cols
    collage_height = thumbnail_height * n_rows
    new_im = Image.new('RGB', (collage_width, collage_height), 'white')

    # Paste thumbnails into collage
    i = 0
    for col in range(n_cols):
        for row in range(n_rows):
            if i >= len(all_thumbnails):
                break  # No more images to paste
            x = col * thumbnail_width
            y = row * thumbnail_height
            new_im.paste(all_thumbnails[i], (x, y))
            i += 1

    extension = ".jpg"
    collage_filename = 'collage.jpg'  # Keep this filename consistent
    destination_file = os.path.join(COLLAGE_FOLDER, collage_filename)
    new_im.save(destination_file)

@app.route('/create-collage', methods=['GET'])
def generate_collage():
    # Get the list of image paths from the 'photos' directory
    listofimages = [os.path.join(UPLOAD_FOLDER, img) for img in os.listdir(UPLOAD_FOLDER) if img.endswith((".png", ".jpg", ".jpeg"))]

    # Call the create_collage function with the list of image paths
    message = create_collage(listofimages=listofimages, n_cols=3, n_rows=3)  # You can adjust n_cols and n_rows as needed

    return jsonify({'message': message})


@app.route('/collage')
def show_collage():
    collage_filename = 'collage.jpg'  # The filename used in create_collage
    # No need to build the path here, just send the filename to the template
    return render_template('collage.html', collage_url=url_for('static', filename='collages/' + collage_filename))


if __name__ == '__main__':
    app.run(debug=True)
