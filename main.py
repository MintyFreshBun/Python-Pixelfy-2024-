
from flask import Flask, request, redirect, render_template
from werkzeug.utils import secure_filename
from PIL import Image,ImageOps ,ImageFilter,ImageChops
import base64
from io import BytesIO
import numpy as np


allowed_exts = {'jpg', 'jpeg','png','JPG','JPEG','PNG'}
app = Flask(__name__)

def check_allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts


# Function to create a dither pattern
def create_dither_pattern(image):
    
    size=(image.width, image.height)
    pattern = []
    for y in range(size[1]):
        row = []
        for x in range(size[0]):
            row.append(255 if (x + y) % 2 == 0 else 0)
        pattern.append(row)
    return pattern

# Function to apply dither effect with custom pattern and overlay blending
def apply_dither_effect(image):
    # Step 1: Create a custom dither pattern
    dither_pattern = create_dither_pattern(image)
    
    # Step 2: Create a new image with the dither pattern
    dither_image = Image.new('L', (len(dither_pattern[0]), len(dither_pattern)))
    dither_image.putdata(sum(dither_pattern, []))
    #dither_image = dither_image.resize(image.size, Image.NEAREST)
    print("Dither image mode:", dither_image.mode)
    
    print("Input image mode:", image.mode)
    print("Dither convered image mode:", dither_image.mode)
    
    # Step 4: Apply dither effect to the input image using overlay blending
    #dittered_img = Image.blend(image, dither_image, alpha=0.24)
    dittered_img = ImageChops.overlay(image,dither_image)
    
    # Step  5Apply posterization effect
    #posterized_image = dittered_img
    #posterized_image = dittered_img.filter(ImageFilter.ModeFilter(8))
    posterized_image = ImageOps.posterize(dittered_img,2)
    
    # Step 6: Return the processed image
    #return processed_image
    return posterized_image

@app.route("/",methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		if 'file' not in request.files:
			print('No file attached in request')
			return redirect(request.url)
		
		file = request.files['file']
		
		if file.filename == '':
			print('No file selected')
			return redirect(request.url)
		
		if file and check_allowed_file(file.filename):
			filename = secure_filename(file.filename)
			print('Uploaded file:', filename)
			img = Image.open(file.stream)
			 # print trhough Image pillow, this can give you an idea of how it can work and what information we can use
			print('Image Format:', img.format)
			print('Image Size:',img.size)
			print('Image Mode:',img.mode)
			# Making sure to convert the image to RGB sence jpeg doesnt support RGBA
			## you might want to think better on the whole image.mode https://pillow.readthedocs.io/en/stable/handbook/concepts.html
			# A DUH, if we want to work with RGBA, the we dont need to convert we play with enchances, LIKE SATURATION AND BRIGHTNESS, All while still keeping that
			img = img.convert('RGB')
			
			 # Resize the image if its width exceeds 400px
			max_width = 250
			if img.width > max_width:
				ratio = max_width / img.width
				new_height = int(img.height * ratio)
				img = img.resize((max_width, new_height))
			
            # Convert the image to grayscale
			img = ImageOps.grayscale(img)
			print('greyscale img:',img.mode)
   
			#img = img.convert('1',dither=Image.FLOYDSTEINBERG)  (this turns into 1bit image)
			 # Apply dither effect
            
			processed_image = apply_dither_effect(img)
			
			newSize = (processed_image.width*3,processed_image.height*3)
			processed_image = processed_image.resize(newSize, Image.NEAREST)
   			
      
			with BytesIO() as buf:
				processed_image.save(buf, 'jpeg')
				image_bytes = buf.getvalue()
			encoded_string = base64.b64encode(image_bytes).decode()         
			
            
        

		return render_template('index.html', img_data=encoded_string), 200
	else:
		return render_template('index.html', img_data=""), 200

if __name__ == "__main__":
	app.debug=True
	app.run(host='0.0.0.0')