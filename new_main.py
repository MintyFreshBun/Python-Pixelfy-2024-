
from flask import Flask, request, redirect, render_template
from werkzeug.utils import secure_filename
from PIL import Image,ImageEnhance
import base64
from io import BytesIO

from blendmodes.blend import blendLayers, BlendType


allowed_exts = {'jpg', 'jpeg','png','JPG','JPEG','PNG'}
# List of the color pallet file names , got them from Lospec
color_list ={"local-colors","aap-64-32x","blessing-8x","blk-neo-32x","blk-nx64-32x","bubblegum-16-8x","endesga-32-32x","gated-8x",
"island-joy-16-8x","late-night-sunrise-8x","mulfok32-32x","na16-8x","oil-6-8x","resurrect-64-32x","twilight-5-8x",
"vanilla-milkshake-8x"}

previous_image_data = None


app = Flask(__name__)
# File checker
def check_allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts

# Load the pattern image
pattern_image = Image.open("assets/ditter_weak2.png")


# Function to apply dither and Quantization
def img_quantization(image,step_value,dither_value,grayscale_value,color_value,bright_value,contrast_value,size_value):
    ## Step 1 : prepare the image with the contrasts and scale needed
     # Resize the image if its width exceeds the value inserted
	max_width = size_value
	if image.width > max_width:
		ratio = max_width / image.width
		new_height = int(image.height * ratio)
		image = image.resize((max_width, new_height))
	
	
	# Apply the contrest and brightness filters
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
	if grayscale_value == "grayscale"  or color_value == "local-colors":
		pallet_set = None
	else:		
		pallet_set = Image.open("assets/" + color_value + ".png")

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
        
        while (scaling_factor*processed_image.width >900):
            scaling_factor= scaling_factor -1
            print("Scaling factor reduced:",scaling_factor)
    
    newSize = (processed_image.width*scaling_factor,processed_image.height*scaling_factor)
    final_image = processed_image.resize(newSize, Image.NEAREST)
    return final_image
    


@app.route("/",methods=['GET', 'POST'])
def index():
	global previous_image_data
	
	if request.method == 'POST':
		
		
		#get the values needed
		bright_value = float(request.form['brightness'])
		step_value = int(request.form['steps'])
		contrast_value = float(request.form['contrast'] )
		dither_value = float(request.form['dither_op'])        
		grayscale_value =  str(request.form.get('grayscale'))
		color_value =  str(request.form.get('colors'))
		size_value = int((request.form['pixel_size']))
		## printing to check on console to see if everything all good
		print('Brightness:',bright_value)
		print('Contrast:',contrast_value)
		print('Color Count Steps:',step_value)
		print('Dither Opacity:',dither_value)
		print('Grayscale Set:',grayscale_value)
		print('Color pallet name:',color_value)
		print('Pixel Width size:',size_value)
  
		
		if 'file' not in request.files:
			if previous_image_data == None:
				print('No file attached in request')
				return redirect(request.url)
			print('No file attached in request , Reusing previous picture')
			img = previous_image_data.convert('RGB')
			
			
			processed_image = img_quantization(img,step_value,dither_value,grayscale_value,color_value,bright_value,contrast_value,size_value)
			print('Processed image beofre:',processed_image.mode)
			processed_image = processed_image.convert('RGB')
			print('prossed image after:',processed_image.mode)

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
			
			processed_image = img_quantization(img,step_value,dither_value,grayscale_value,color_value,bright_value,contrast_value,size_value)
			print('Processed image beofre:',processed_image.mode)
			processed_image = processed_image.convert('RGB')
			print('prossed image after:',processed_image.mode)

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
			
			processed_image = img_quantization(img,step_value,dither_value,grayscale_value,color_value,bright_value,contrast_value,size_value)
			print('Processed image beofre:',processed_image.mode)
			processed_image = processed_image.convert('RGB')
			print('prossed image after:',processed_image.mode)

			## upscale the image to show on the page 
			final_image = image_resize(processed_image)
	  
			with BytesIO() as buf:
				final_image.save(buf, 'jpeg')
				image_bytes = buf.getvalue()
			encoded_string = base64.b64encode(image_bytes).decode()  
				   
		return render_template('index.html', img_data=encoded_string , bright_value=bright_value ,step_value=step_value,contrast_value=contrast_value,dither_value=dither_value, grayscale_value=grayscale_value,color_list=color_list,color_value=color_value,size_value=size_value), 200
		
		
	else:
		return render_template('index.html', img_data="", bright_value=1 ,step_value=8,contrast_value=1,dither_value=0.25, grayscale_value="grayscale",color_list=color_list,color_value="local-colors",size_value=300 ), 200

if __name__ == "__main__":
	app.debug=True
	app.run(host='0.0.0.0')