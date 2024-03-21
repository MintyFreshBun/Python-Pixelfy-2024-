
from flask import Flask, request, redirect, render_template
from werkzeug.utils import secure_filename
from PIL import Image,ImageOps ,ImageFilter,ImageChops ,ImageDraw,ImageEnhance
import base64
from io import BytesIO
import numpy as np


allowed_exts = {'jpg', 'jpeg','png','JPG','JPEG','PNG'}



app = Flask(__name__)

def check_allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts

# Load the pattern image
pattern_image = Image.open("assets/ditter_weak2.png")

# Function to apply dither effect with custom pattern and overlay blending
def apply_dither_effect(image):
    # Step 1: Get the pattern png
    tiled_image = Image.new('RGBA', (image.width, image.height))
	# Calculate the number of repetitions needed to cover the entire area
    repetitions_x = (image.width + pattern_image.width - 1) // pattern_image.width
    repetitions_y = (image.height + pattern_image.height - 1) // pattern_image.height
    
    # Tile the pattern image across the entire area
    for y in range(repetitions_y):
        for x in range(repetitions_x):
            tiled_image.paste(pattern_image, (x * pattern_image.width, y * pattern_image.height))
   
    #dither_image = dither_image.resize(image.size, Image.NEAREST)
    print("Dither image mode:", tiled_image.mode)
    
    print("Input image mode:", image.mode)
    dither_image = tiled_image.convert('RGB')
    print("Dither convered image mode:", dither_image.mode)
    
    # Create a new white image
    white_bg = Image.new('RGB',(image.width, image.height), color='gray' )
	
    pseduditter = Image.blend(white_bg,dither_image, alpha=0.45)
    pseduditter = pseduditter.convert('RGB')
    # Step 4: Apply dither effect to the input image using overlay blending
    ## because ImageChopss only works with L and RGB , anything with alpha doesnt work, however, if this is overlay, then mid gray will be invisible
    #dittered_img = Image.blend(image, dither_image, alpha=0.24)
    dittered_img = ImageChops.overlay(image,pseduditter)
    dittered_img = dittered_img.convert('RGB')
    # Step  5Apply posterization effect
    #posterized_image = dittered_img
    #posterized_image = dittered_img.filter(ImageFilter.ModeFilter(8))
    posterized_image = ImageOps.posterize(dittered_img,3)
    
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
			# Making sure to convert the image to RGB sence jpeg doesnt support RGBA - imageOps can only handle L and RGB, so the Alpha will have to be converted before colorizing
			## you might want to think better on the whole image.mode https://pillow.readthedocs.io/en/stable/handbook/concepts.html
			# A DUH, if we want to work with RGBA, the we dont need to convert we play with enchances, LIKE SATURATION AND BRIGHTNESS, All while still keeping that
			img = img.convert('RGB')
			
			 # Resize the image if its width exceeds 400px - also look at quantize https://www.geeksforgeeks.org/python-pil-image-quantize-method/?ref=ml_lbp
			max_width = 250
			if img.width > max_width:
				ratio = max_width / img.width
				new_height = int(img.height * ratio)
				img = img.resize((max_width, new_height))
			
            # Convert the image to grayscale
			#img = ImageOps.grayscale(img)
			img_greyscale = ImageEnhance.Color(img)
			img_desaturated = img_greyscale.enhance(0.0)
			print('greyscale img:',img_desaturated.mode)
			
   
			#img = img.convert('1',dither=Image.FLOYDSTEINBERG)  (this turns into 1bit image)
			 # Apply dither effect
            
			processed_image = apply_dither_effect(img_desaturated)
			print('Processed image beofre:',processed_image.mode)
			processed_image = processed_image.convert('L')
			print('prossed image after:',processed_image.mode)


			# Apply gradient map to the posterized image
			
			#final_image = Image.blend(processed_image, gradient_map, alpha=0.5)
			# Define the color for colorizing (light yellow in this example)
			dark = (102, 0, 51)
			middle = (255, 153, 51)
			light = (255, 255, 153)

			# Apply colorizing effect
			final_image = ImageOps.colorize(processed_image, black=dark, white=light, mid=middle, blackpoint=0, whitepoint=255, midpoint=127)
			
			newSize = (final_image.width*3,final_image.height*3)
			final_image = final_image.resize(newSize, Image.NEAREST)
   			
      
			with BytesIO() as buf:
				final_image.save(buf, 'jpeg')
				image_bytes = buf.getvalue()
			encoded_string = base64.b64encode(image_bytes).decode()         
			
            
        

		return render_template('index.html', img_data=encoded_string), 200
	else:
		return render_template('index.html', img_data=""), 200

if __name__ == "__main__":
	app.debug=True
	app.run(host='0.0.0.0')