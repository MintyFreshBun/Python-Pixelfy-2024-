
from flask import Flask, request, redirect, render_template
from werkzeug.utils import secure_filename
from PIL import Image,ImageOps ,ImageFilter,ImageChops ,ImageDraw,ImageEnhance
import base64
from io import BytesIO
import numpy as np


allowed_exts = {'jpg', 'jpeg','png','JPG','JPEG','PNG'}

# Define the dither matrix for 4x4 ordered dithering
#dither_matrix = np.array([[0, 8, 2, 10],[12, 4, 14, 6],[3, 11, 1, 9],[15, 7, 13, 5]])
dither_matrix = np.array([[0,2],[3,1]])


app = Flask(__name__)

def check_allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts


# Function to create a dither pattern
def create_dither_pattern(image):
    
    #dither_image = Image.new('L', (width, height))
    #for y in range(height):
        #for x in range(width):
            #threshold = dither_matrix[y % 4][x % 4]
            #pixel_value = threshold * 16
            #dither_image.putpixel((x, y), pixel_value)
    ## So i THeory it works, but how ever it takes a while to calculate and and setup the values,
    ##So we might have scrap the calculate and instead try with a ditter patern image instead, we can create a few of our own and well try that
    
    
    ## So the data pattern we have to check our ditter file and figure how we are going to do the rows fomular acording to the color of the alpha
    size=(image.width, image.height)
    pattern = []
    for y in range(size[1]):
        row = []
        for x in range(size[0]):
            #row.append(255 if (x + y) % 2 == 0 else 0)
            threshold = dither_matrix[y % 2][x % 2]
            
            print('treshhold value:',threshold ,end="\r")
            row.append(threshold * 4)
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
    dither_image = dither_image.convert('RGB')
    print("Dither convered image mode:", dither_image.mode)
    
    # Create a new white image
    white_bg = Image.new('RGB',(image.width, image.height), color='white' )
	
    pseduditter = Image.blend(white_bg,dither_image, alpha=1)
    pseduditter = pseduditter.convert('RGB')
    # Step 4: Apply dither effect to the input image using overlay blending
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