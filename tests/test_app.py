import base64
import io
import unittest

from PIL import Image

import new_main


class PixelfyRouteTests(unittest.TestCase):
    def setUp(self):
        new_main.previous_image_data = None
        self.client = new_main.app.test_client()
        self.settings = {
            "brightness": "1",
            "steps": "8",
            "contrast": "1",
            "dither": "0.25",
            "grayscale": "grayscale",
            "pixel_size": "30",
        }

    def make_png(self):
        image = io.BytesIO()
        Image.new("RGB", (32, 24), "red").save(image, format="PNG")
        image.seek(0)
        return image

    def test_home_page_renders_default_pixel_width(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'value="300"', response.data)

    def test_valid_image_returns_decodable_jpeg(self):
        response = self.client.post(
            "/pixelfy",
            data={**self.settings, "file": (self.make_png(), "sample.png")},
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        image_bytes = base64.b64decode(response.json["image_data"])
        with Image.open(io.BytesIO(image_bytes)) as result:
            self.assertEqual(result.format, "JPEG")

    def test_missing_image_returns_client_error(self):
        response = self.client.post("/pixelfy", data=self.settings)

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_unsupported_image_extension_returns_client_error(self):
        response = self.client.post(
            "/pixelfy",
            data={**self.settings, "file": (io.BytesIO(b"data"), "sample.gif")},
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_unreadable_image_returns_client_error(self):
        response = self.client.post(
            "/pixelfy",
            data={**self.settings, "file": (io.BytesIO(b"not an image"), "sample.png")},
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
