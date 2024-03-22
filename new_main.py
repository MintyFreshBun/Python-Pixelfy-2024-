
from flask import Flask, request, redirect, render_template
from werkzeug.utils import secure_filename
from PIL import Image,ImageOps ,ImageFilter,ImageChops ,ImageDraw,ImageEnhance
import base64
from io import BytesIO
import numpy as np
from blendmodes.blend import blendLayers, BlendType


allowed_exts = {'jpg', 'jpeg','png','JPG','JPEG','PNG'}

previous_image_data = None


##To do List

## - change from a PNG premate , make the base template in code with diferent matrixes to select. x2 x4 x16 , ordered ditter, scaline ditter etc (search on that)



app = Flask(__name__)
# File checker
def check_allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts

# Load the pattern image
pattern_image = Image.open("assets/ditter_weak2.png")
# Pallet image test
pallet_img = Image.open("assets/mulfok32-32x.png")

# Function to apply dither and Quantization
def img_quantization(image,step_value,dither_value):
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
	white_bg = Image.new('RGB',(image.width, image.height), color='grey' )
	
	pseduditter = Image.blend(white_bg,dither_image, alpha=1)
	pseduditter = pseduditter.convert('RGB')
	# Step 4: Apply dither effect to the input image using overlay blending
	## because ImageChopss only works with L and RGB , anything with alpha doesnt work, however, if this is overlay, then mid gray will be invisible
	# using blendlayress instead of the one on Pillow sence this those ACTUALLy do what i want
	dittered_img = blendLayers(image,pseduditter,BlendType.OVERLAY,dither_value)
	dittered_img = dittered_img.convert('RGB')
	# Step  5Apply posterization effect
	## ok palette may not be that great sence it ignores colors and with that we might need to rely on something else
	## solution to that might be here : https://stackoverflow.com/questions/71581267/apply-a-color-map-gradient-map-to-an-image-using-python
	quantized_image = dittered_img.quantize(colors=step_value, method=None, kmeans=0, palette=None, dither=0)
	
	# Step 6: Return the processed image
	#return processed_image
	return quantized_image




@app.route("/",methods=['GET', 'POST'])
def index():
	global previous_image_data
	
	if request.method == 'POST':
     
		bright_value = float(request.form['brightness'])
		step_value = int(request.form['steps'])
		contrast_value = float(request.form['contrast'] )
		dither_value = float(request.form['dither_op'])        
		grayscale_value =  bool(request.form.get('grayscale'))
  
		print('Brightness:',bright_value)
		print('Contrast:',contrast_value)
		print('Color Count Steps:',step_value)
		print('Dither Opacity:',dither_value)
		print('Grayscale Set:',grayscale_value)
		
		if 'file' not in request.files:
			if previous_image_data == None:
				print('No file attached in request')
				return redirect(request.url)
			print('No file attached in request , Reusing previous picture')
			img = previous_image_data.convert('RGB')
			
			 # Resize the image if its width exceeds 400px
			max_width = 250
			if img.width > max_width:
				ratio = max_width / img.width
				new_height = int(img.height * ratio)
				img = img.resize((max_width, new_height))
			
			
			# Apply the contrest and brightness filters
			brightness = ImageEnhance.Brightness(img)
			img = brightness.enhance(bright_value)
	  
			contrast = ImageEnhance.Contrast(img)
			img = contrast.enhance(contrast_value)

			# Apply grayscale conversion if checkbox is checked
			if grayscale_value:				
				enhancer = ImageEnhance.Color(img)
				img = enhancer.enhance(0)
	
			processed_image = img_quantization(img,step_value,dither_value)
			print('Processed image beofre:',processed_image.mode)
			processed_image = processed_image.convert('RGB')
			print('prossed image after:',processed_image.mode)

			
			newSize = (processed_image.width*3,processed_image.height*3)
			final_image = processed_image.resize(newSize, Image.NEAREST)
   			
	  
			with BytesIO() as buf:
				final_image.save(buf, 'jpeg')
				image_bytes = buf.getvalue()
			encoded_string = base64.b64encode(image_bytes).decode()  
		
		file = request.files['file']
		
		
		if file.filename == '':
			if previous_image_data == None:
				print('No file selected')
				return redirect(request.url)
			img = previous_image_data.convert('RGB')
			print('No file selected , Reusing previous picture')
			 # Resize the image if its width exceeds 400px
			max_width = 250
			if img.width > max_width:
				ratio = max_width / img.width
				new_height = int(img.height * ratio)
				img = img.resize((max_width, new_height))
			
			
			# Apply the contrest and brightness filters
			brightness = ImageEnhance.Brightness(img)
			img = brightness.enhance(bright_value)
	  
			contrast = ImageEnhance.Contrast(img)
			img = contrast.enhance(contrast_value)

			# Apply grayscale conversion if checkbox is checked
			if grayscale_value:				
				enhancer = ImageEnhance.Color(img)
				img = enhancer.enhance(0)
	
			
			processed_image = img_quantization(img,step_value,dither_value)
			print('Processed image beofre:',processed_image.mode)
			processed_image = processed_image.convert('RGB')
			print('prossed image after:',processed_image.mode)

			
			newSize = (processed_image.width*3,processed_image.height*3)
			final_image = processed_image.resize(newSize, Image.NEAREST)
   			
	  
			with BytesIO() as buf:
				final_image.save(buf, 'jpeg')
				image_bytes = buf.getvalue()
			encoded_string = base64.b64encode(image_bytes).decode()  
		
		if file and check_allowed_file(file.filename):
			filename = secure_filename(file.filename)
			print('Uploaded file:', filename)
			img = Image.open(file.stream)
			 # print trhough Image pillow, this can give you an idea of how it can work and what information we can use
			print('Image Format:', img.format)
			print('Image Size:',img.size)
			print('Image Mode:',img.mode)

			# Store a copy of the original image data
			previous_image_data = img
   
			# Making sure to convert the image to RGB sence jpeg doesnt support RGBA - imageOps can only handle L and RGB, so the Alpha will have to be converted before colorizing
			## you might want to think better on the whole image.mode https://pillow.readthedocs.io/en/stable/handbook/concepts.html
			# A DUH, if we want to work with RGBA, the we dont need to convert we play with enchances, LIKE SATURATION AND BRIGHTNESS, All while still keeping that
			img = img.convert('RGB')
			
			 # Resize the image if its width exceeds 400px
			 # Try to have the option to choose a size of pixels and then calculate the resize after 
			max_width = 250
			if img.width > max_width:
				ratio = max_width / img.width
				new_height = int(img.height * ratio)
				img = img.resize((max_width, new_height))
			
		
			#img = img.convert('1',dither=Image.FLOYDSTEINBERG)  (this turns into 1bit image)
			 # Apply dither effect
			# Apply the contrest and brightness filters
			brightness = ImageEnhance.Brightness(img)
			img = brightness.enhance(bright_value)
	  
			contrast = ImageEnhance.Contrast(img)
			img = contrast.enhance(contrast_value)

			# Apply grayscale conversion if checkbox is checked
			if grayscale_value:				
				enhancer = ImageEnhance.Color(img)
				img = enhancer.enhance(0)
	
			
			processed_image = img_quantization(img,step_value,dither_value)
			print('Processed image beofre:',processed_image.mode)
			processed_image = processed_image.convert('RGB')
			print('prossed image after:',processed_image.mode)


			# Try to have the option to choose a size of pixels and then calculate the resize after 
			newSize = (processed_image.width*3,processed_image.height*3)
			final_image = processed_image.resize(newSize, Image.NEAREST)
   			
	  
			with BytesIO() as buf:
				final_image.save(buf, 'jpeg')
				image_bytes = buf.getvalue()
			encoded_string = base64.b64encode(image_bytes).decode()  
				   
		return render_template('index.html', img_data=encoded_string , bright_value=bright_value ,step_value=step_value,contrast_value=contrast_value,dither_value=dither_value, grayscale_value=grayscale_value), 200
		
		
	else:
		return render_template('index.html', img_data="", bright_value=1 ,step_value=16,contrast_value=1,dither_value=0.25, grayscale_value=False ), 200

if __name__ == "__main__":
	app.debug=True
	app.run(host='0.0.0.0')