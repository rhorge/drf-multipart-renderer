import os
import tempfile

from django.test import TestCase
from src.drf_multipart_renderer import MultipartRenderer
from src.drf_multipart_renderer.multipart_renderer import to_bytes


class TestMultiPartRenderer(TestCase):
    def setUp(self):
        self.renderer = MultipartRenderer()
        self.media_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        self.boundary = to_bytes(f'--{self.renderer.boundary}')
        self.end_boundary = to_bytes(f'--{self.renderer.boundary}--')

    def test_render_fields(self):

        """Verify basic key-value pairs are rendered correctly."""
        data = {
            'title': [
                'Test Item',
                {
                    'a': 3, 'b': 2
                }
            ],
            'description': 'A simple test',
            'number': 33
        }

        expected_result = b'\r\n'.join((
            self.boundary,
            b'Content-Disposition: form-data; name="title"',
            b'',
            b'Test Item',
            self.boundary,
            b'Content-Disposition: form-data; name="title"',
            b'Content-Type: application/json',
            b'',
            b'{"a":3,"b":2}',
            self.boundary,
            b'Content-Disposition: form-data; name="description"',
            b'',
            b'A simple test',
            self.boundary,
            b'Content-Disposition: form-data; name="number"',
            b'Content-Type: application/json',
            b'',
            b'33',
            self.end_boundary,
            b''
        ))

        rendered = self.renderer.render(data, self.media_type, {'response': {'Content-Type': 'multipart/form-data'}})

        self.assertEqual(rendered, expected_result)

    def test_render_file(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg", prefix="test_image_") as tmp:
            tmp.write(b"test image data")
            tmp.seek(0)  # Go back to the start of the file

            # Get the actual filename assigned by the OS
            filename = os.path.basename(tmp.name)
            data = {
                'info': 'test info',
                'file': tmp
            }

            expected_result = b'\r\n'.join((
                self.boundary,
                b'Content-Disposition: form-data; name="info"',
                b'',
                b'test info',
                self.boundary,
                b'Content-Disposition: form-data; name="file"; filename="' + bytes(filename, 'utf-8') + b'"',
                b'Content-Type: image/jpeg',
                b'',
                b'test image data',
                self.end_boundary,
                b''
            ))

            rendered = self.renderer.render(data, self.media_type,
                                            {'response': {'Content-Type': 'multipart/form-data'}})

            self.assertEqual(rendered, expected_result)
