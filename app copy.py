from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
import os
import requests
from PIL import Image, ImageChops, ImageEnhance

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

background_image_path = 'background.jpg'

# Function to blend images
def blend_images(uploaded_image, background_image):
    # Resize the background image to match the dimensions of the uploaded image
    background_image = background_image.resize(uploaded_image.size)

    # Blend the images using the "screen" mode
    blended_image = ImageChops.screen(uploaded_image, background_image)

    # Enhance the contrast of the blended image
    enhancer = ImageEnhance.Contrast(blended_image)
    blended_image = enhancer.enhance(1)  # Adjust the contrast factor as needed

    return blended_image

@app.route('/')
def index():
    # Get a list of available images in the upload folder
    image_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith(('jpg', 'jpeg', 'png', 'gif'))]
    return render_template('index.html', image_files=image_files)

@app.route('/post_endpoint', methods=['POST'])
def handle_post_request():
    if request.method == 'POST':
        # Check if the POST request has a file part
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})

        file = request.files['file']

        # If the user does not select a file, browser also
        # submit an empty file without filename
        if file.filename == '':
            return jsonify({'error': 'No selected file'})

        # Print the file name
        print('Received file:', file.filename)

        process_file_name(file.filename)

        # Save the file to the server
        upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)

        # Open the uploaded image and the background image
        uploaded_image = Image.open(file_path)
        background_image = Image.open(background_image_path)

        # Blend the images
        blended_image = blend_images(uploaded_image, background_image)

        # Save the blended image to the server with the original filename
        blended_image_path = os.path.join(upload_folder, file.filename)
        blended_image.save(blended_image_path)

        # Return the URL and original filename of the blended image
        blended_image_url = url_for('uploaded_file', filename=file.filename)
        response_data = {'message': 'Image blended and received successfully', 'image_url': blended_image_url, 'filename': file.filename}
        return jsonify(response_data)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def process_file_name(original_name):
    if "(2)" in original_name:
        print(f"Skipping file: {original_name}")
        return  # Skip processing files with "(2)" in their names

    print(f"Original Name: {original_name}")

    name_parts = original_name.split('_')

    if len(name_parts) == 2:
        rtc = name_parts[0]
        formatted_rtc = f"'{rtc[2:4]}  {rtc[4:6]}  {rtc[6:]}'"
        original_name = name_parts[1]
        print(f"Formatted RTC: {formatted_rtc}")

        if '-' in original_name:
            image_full_name = original_name[:original_name.rfind('.')]
            hyphen_index = image_full_name.find('-')
            f_type = image_full_name[hyphen_index + 1:]
            image1 = image_full_name[:hyphen_index]
            print(f"Image1: {image1}")
            print(f"F Type: {f_type}")

        elif '(' in original_name:
            parenthesis_index = original_name.find('(')
            image1 = original_name[:parenthesis_index].strip()
            print(f"Extracted text: {image1}")
            image1_num = int(image1) + 1
            print(f'http://192.168.4.1/image?name={rtc}_{image1_num}(2).jpg')
        else:
            image1 = original_name[:original_name.rfind('.')]
            print(f"Image1: {image1}")

    print("\n")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
