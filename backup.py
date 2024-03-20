from flask import Flask, render_template, request, flash, redirect, url_for, send_file
from PIL import Image
from io import BytesIO
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'

@app.route('/', methods=['GET','POST'])
def index():
    processed_image_url = None
    #return 'Hello, Flask!'
    if request.method == "POST":
        # Check if a file was submitted
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        ##Get the image uploaded file
        file = request.files['image']

         # Check if the file has a valid extension
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        # Process the image file with pillow image
        image = Image.open(file)
        #For now Print the information on the console about the image to confirm everything so far
        print('Uploaded file:', file.filename)
        # print trhough Image pillow, this can give you an idea of how it can work and what information we can use
        print('Image Format:',image.format)
        print('Image Size:',image.size)
        print('Image Mode:',image.mode)

        # Generate a unique filename
        filename = str(uuid.uuid4()) + '.png'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        # Save the uploaded image
        file.save(filepath)
        # Open the image using Pillow
        image = Image.open(filepath)
        # Convert the image to RGB mode
        image = image.convert('RGB')
        # Process the image (e.g., posterization)
        # Save the processed image as a PNG file
        processed_filename = 'processed_' + filename
        processed_filepath = os.path.join(UPLOAD_FOLDER, processed_filename)
        image.save(processed_filepath, format="PNG")
        # Pass the URL of the processed image to the HTML template
        processed_image_url = url_for('processed_image', filename=processed_filename)

    return render_template('index.html',processed_image_url=processed_image_url)

@app.route('/processed_image/<filename>')
def processed_image(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

if __name__ == "__main__":
    app.run(debug=True)