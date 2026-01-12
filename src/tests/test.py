import tempfile

from django.test import TestCase
from src.drf_multipart_renderer import MultipartRenderer


class TestMultiPartRenderer(TestCase):
    def setUp(self):
        self.renderer = MultipartRenderer()
        self.media_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'

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
        rendered = self.renderer.render(data, self.media_type)

        expected_result = b'\r\n'.join((
            b'--BoUnDaRyStRiNgetpvelarptriznzsespgfmagoxpjpjluxkwqroqgsilzbdfsfgffddg',
            b'Content-Disposition: form-data; name="title"',
            b'',
            b'Test Item',
            b'--BoUnDaRyStRiNgetpvelarptriznzsespgfmagoxpjpjluxkwqroqgsilzbdfsfgffddg',
            b'Content-Disposition: form-data; name="title"',
            b'Content-Type: application/json',
            b'',
            b'{"a":3,"b":2}',
            b'--BoUnDaRyStRiNgetpvelarptriznzsespgfmagoxpjpjluxkwqroqgsilzbdfsfgffddg',
            b'Content-Disposition: form-data; name="description"',
            b'',
            b'A simple test',
            b'--BoUnDaRyStRiNgetpvelarptriznzsespgfmagoxpjpjluxkwqroqgsilzbdfsfgffddg',
            b'Content-Disposition: form-data; name="number"',
            b'Content-Type: application/json',
            b'',
            b'33',
            b'--BoUnDaRyStRiNgetpvelarptriznzsespgfmagoxpjpjluxkwqroqgsilzbdfsfgffddg--',
            b''
        ))

        self.assertEqual(rendered, expected_result)

    def test_render_file(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg", prefix="test_image_") as tmp:
            tmp.write(b"test image data")
            tmp.seek(0)  # Go back to the start of the file

            # Get the actual filename assigned by the OS
            filename = tmp.name.split('/')[2]
            data = {
                'info': 'test info',
                'file': tmp
            }

            expected_result = b'\r\n'.join((
                b'--BoUnDaRyStRiNgetpvelarptriznzsespgfmagoxpjpjluxkwqroqgsilzbdfsfgffddg',
                b'Content-Disposition: form-data; name="info"',
                b'',
                b'test info',
                b'--BoUnDaRyStRiNgetpvelarptriznzsespgfmagoxpjpjluxkwqroqgsilzbdfsfgffddg',
                b'Content-Disposition: form-data; name="file"; filename="' + bytes(filename, 'utf-8') + b'"',
                b'Content-Type: image/jpeg',
                b'',
                b'test image data',
                b'--BoUnDaRyStRiNgetpvelarptriznzsespgfmagoxpjpjluxkwqroqgsilzbdfsfgffddg--',
                b''
            ))

            rendered = self.renderer.render(data, self.media_type)
            self.assertEqual(rendered, expected_result)
