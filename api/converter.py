import base64
from io import BytesIO
from PIL import Image

class Base64ImageConverter:
    def __init__(self):
        pass

    def convert_base64_to_image(self, base64_string):
        try:
            # Remove the data URL prefix and decode the base64 string
            image_data = base64.b64decode(base64_string)

            # Create a BytesIO object to handle the image data
            image_stream = BytesIO(image_data)

            # Open the image using PIL
            image = Image.open(image_stream)

            return image

        except Exception as e:
            print("Error converting base64 to image:", e)
            return None

    def save_image(self, image, output_path):
        if image is not None:
            try:
                image.save(output_path)
                print("Image saved successfully to", output_path)
            except Exception as e:
                print("Error saving image:", e)

# # Example usage
# base64_string = ""
# converter = Base64ImageConverter()
# image = converter.convert_base64_to_image(base64_string)
# converter.save_image(image, "output.png")
