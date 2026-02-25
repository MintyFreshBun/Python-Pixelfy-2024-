from PIL.Image import Resampling
from flask import Flask, request, redirect, render_template ,jsonify
from werkzeug.utils import secure_filename
from PIL import Image,ImageEnhance
import base64
from io import BytesIO
from blendmodes.blend import blendLayers, BlendType
import json

with open("assets/pallets.JSON") as f:
    PALETTES = json.load(f)

allowed_exts = {'jpg', 'jpeg','png','JPG','JPEG','PNG'}
# For storing any previous image uploaded
previous_image_data = None


app = Flask(__name__)
# File checker
def check_allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts

# Load the pattern image
pattern_image = Image.open("assets/ditter_weak2.png")

## Convert Hex -> RGB for quantizer pallet
def hex_to_rgb(hex_color):
	hex_color = hex_color.lstrip("#")
	return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

## Build a img pallet for quantizer pallet
def build_palette_image(hex_colors):
	palette_img = Image.new("P", (1, 1))
	rgb_palette = []
	for hex_color in hex_colors:
		rgb_palette.extend(hex_to_rgb(hex_color))

	# PIL requires exactly 768 values (256 * 3)
    # So we pad the palette with zeros
	while len(rgb_palette) < 768:
		rgb_palette.extend((0, 0, 0))

	palette_img.putpalette(rgb_palette)
	return palette_img

# Function to apply dither and Quantization
def img_quantization(image,step_value,dither_value,grayscale_value,color_value,bright_value,contrast_value,size_value):
	## Step 1 : prepare the image with the contrasts and scale needed
	 # Resize the image if its width exceeds the value inserted
	max_width = size_value
	if image.width > max_width:
		ratio = max_width / image.width
		new_height = int(image.height * ratio)
		image = image.resize((max_width, new_height))
	
	
	# Apply the contrast and brightness filters
	brightness = ImageEnhance.Brightness(image)
	image = brightness.enhance(bright_value)

	contrast = ImageEnhance.Contrast(image)
	image = contrast.enhance(contrast_value)

	# Apply grayscale conversion if checkbox is checked
	if grayscale_value == "grayscale":				
		enhancer = ImageEnhance.Color(image)
		image = enhancer.enhance(0)


	# Step 2: Get the pattern png
	tiled_image = Image.new('RGBA', (image.width, image.height))
	# Calculate the number of repetitions needed to cover the entire area
	repetitions_x = (image.width + pattern_image.width - 1) // pattern_image.width
	repetitions_y = (image.height + pattern_image.height - 1) // pattern_image.height
	
	# Step 3 :Tile the pattern image across the entire area
	for y in range(repetitions_y):
		for x in range(repetitions_x):
			tiled_image.paste(pattern_image, (x * pattern_image.width, y * pattern_image.height))
   
	dither_image = tiled_image.convert('RGB')
	
	
	# Step 4 :Create a new white image and blend with together with the seemless pattern
	white_bg = Image.new('RGB',(image.width, image.height), color='grey' )
	
	pseduditter = Image.blend(white_bg,dither_image, alpha=1)
	pseduditter = pseduditter.convert('RGB')
	# Step 5: Apply dither effect to the input image using overlay blending
	## because ImageChopss only works with L and RGB , anything with alpha doesnt work, however, if this is overlay, then mid gray will be invisible
	# using blendlayress instead of the one on Pillow sence this those ACTUALLy do what i want
	dittered_img = blendLayers(image,pseduditter,BlendType.OVERLAY,dither_value)
	dittered_img = dittered_img.convert('RGB')
	# Step  6 Apply quantization effect to ge the pixel effect
	pallet_set = None
	if grayscale_value == "grayscale"  or color_value == "Local-Colors":
		pallet_set = None
	else:
		hex_colors = PALETTES.get(color_value)
		## if the pallet isnt found it returns None by default has a failsafe
		if not hex_colors:
			print("No hex color pallet found, pallet set to None")
			pallet_set = None
		else:
			pallet_set = build_palette_image(hex_colors)

	quantized_image = dittered_img.quantize(colors=step_value, method=None, kmeans=0, palette=pallet_set, dither=0)
	
	# Step 6: Return the processed image
	#return processed_image
	return quantized_image


def image_resize(processed_image):
	#Calculation for the factor acording to the width acording to the pattern formula

	scaling_factor = 0;
	if processed_image.width <= 38:
		scaling_factor = 14
		print("Scaling factor:",scaling_factor)
	elif processed_image.width >= 350:
		scaling_factor = 2
		print("Scaling factor:",scaling_factor)
		 

	else:
		# Define the slope (m) and y-intercept (c)
		m = -3 / 80
		c = 115 / 8
		
		# Calculate the scaling factor using the linear equation

		scaling_factor = m * processed_image.width + c
		print("Scaling factor:",scaling_factor)
		scaling_factor = round(scaling_factor)
		print("Scaling factor rounded:",scaling_factor)

		while scaling_factor*processed_image.width >900:
			scaling_factor= scaling_factor -1
			print("Scaling factor reduced:",scaling_factor)

	new_size = (processed_image.width*scaling_factor,processed_image.height*scaling_factor)
	final_image = processed_image.resize(new_size, Resampling.NEAREST)
	return final_image



@app.route("/",methods=['GET', 'POST'])
def index():
	global previous_image_data
	return render_template('index.html', img_data="", bright_value=1 ,step_value=8,contrast_value=1,dither_value=0.25, grayscale_value="grayscale",color_list=PALETTES.keys(),color_value="local-colors",size_value=300 ), 200

@app.route("/pixelfy", methods=["POST"])
def pixelfy():
	global previous_image_data


	if request.method == 'POST':

		print("incoming request:", request.form)
		print("Incoming FILES DATA:", request.files)
		# get the values needed
		bright_value = float(request.form['brightness'])
		step_value = int(request.form['steps'])
		contrast_value = float(request.form['contrast'])
		dither_value = float(request.form['dither'])
		grayscale_value = str(request.form.get('grayscale'))
		color_value = str(request.form.get('colors'))
		size_value = int((request.form['pixel_size']))
		## printing to check on console to see if everything all good
		print('Brightness:', bright_value)
		print('Contrast:', contrast_value)
		print('Color Count Steps:', step_value)
		print('Dither Opacity:', dither_value)
		print('Grayscale Set:', grayscale_value)
		print('Color pallet name:', color_value)
		print('Pixel Width size:', size_value)

		if 'file' not in request.files:
			if previous_image_data == None:
				print('No file attached in request')
				return redirect(request.url)
			print('No file attached in request , Reusing previous picture')
			img = previous_image_data.convert('RGB')

			processed_image = img_quantization(img, step_value, dither_value, grayscale_value, color_value,
											   bright_value, contrast_value, size_value)
			print('Processed image beofre:', processed_image.mode)
			processed_image = processed_image.convert('RGB')
			print('prossed image after:', processed_image.mode)

			## upscale the image to show on the page
			final_image = image_resize(processed_image)

			with BytesIO() as buf:
				final_image.save(buf, 'jpeg')
				image_bytes = buf.getvalue()
			encoded_string = base64.b64encode(image_bytes).decode()

		file = request.files['file']

		if file.filename == '':
			if previous_image_data == None:
				print('No file selected')
				return redirect(request.url)

			print('No file selected , Reusing previous picture')
			img = previous_image_data.convert('RGB')

			processed_image = img_quantization(img, step_value, dither_value, grayscale_value, color_value,
											   bright_value, contrast_value, size_value)
			print('Processed image beofre:', processed_image.mode)
			processed_image = processed_image.convert('RGB')
			print('prossed image after:', processed_image.mode)

			## upscale the image to show on the page
			final_image = image_resize(processed_image)

			with BytesIO() as buf:
				final_image.save(buf, 'jpeg')
				image_bytes = buf.getvalue()
			encoded_string = base64.b64encode(image_bytes).decode()

		if file and check_allowed_file(file.filename):
			filename = secure_filename(file.filename)
			print('Uploaded file:', filename)
			img = Image.open(file.stream)

			# Store a copy of the original image data
			previous_image_data = img

			img = img.convert('RGB')

			processed_image = img_quantization(img, step_value, dither_value, grayscale_value, color_value, bright_value, contrast_value, size_value)
			print('Processed image before:', processed_image.mode)
			processed_image = processed_image.convert('RGB')
			print('processed image after:', processed_image.mode)

			## upscale the image to show on the page
			final_image = image_resize(processed_image)

			with BytesIO() as buf:
				final_image.save(buf, 'jpeg')
				image_bytes = buf.getvalue()
			encoded_string = base64.b64encode(image_bytes).decode()

			return jsonify({
					"image_data": encoded_string
				})

if __name__ == "__main__":
	app.debug=True
	app.run(host='0.0.0.0')