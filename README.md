# Django Rest Framework multipart renderer
A high-performance multipart (multipart/form-data) renderer for Django Rest Framework.
This package allows you to return complex, nested data structures and binary files in a single multipart response.

## Highlights
- **Response renderer**: Suitable as a DRF Response renderer
- **Smart Type Mapping**: Automatically determines Content-Type for different Python objects.
- **File Support**: Handles file streams and automatically selects MIME types.
- **JSON Integration**: Serializes primitives and dictionaries as `application/json` parts.
- **List Flattening**: Supports multiple values for a single key (e.g., multiple tags or images).

## Install

```sh
pip install drf-multipart-renderer
```

## Usage
To use this renderer, add it to your `renderer_classes` in a DRF View or ViewSet.

### Basic Example

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_multipart_renderer import MultipartRenderer

class MyView(APIView):
    renderer_classes = [MultipartRenderer]

    def get(self, request):
        data = {
            "title": "Project Alpha",
            "metadata": {"version": 1.0, "active": True},
            "file": open("report.pdf", "rb"),
            "tags": ["python", "django"],
            "number": 33
        }
        
        return Response(data)
```

### Data Type Mapping Logic
The `MultipartRenderer` automatically determines the `Content-Type` of each part in the response based on the Python type of the dictionary value.

| Python Type                               | Target Content-Type  | Handling Behavior                                                                                                       |
|:------------------------------------------|:---------------------|:------------------------------------------------------------------------------------------------------------------------|
| **String** (`str`)                        | `text/plain`         | Encoded as standard UTF-8 text.                                                                                         |
| **Primitives** (`int`, `float`, `bool`)   | `application/json`   | Serialized as a JSON value.                                                                                             |
| **Dictionary** (`dict`)                   | `application/json`   | Serialized as a JSON object.                                                                                            |
| **File** (`io.IOBase`)                    | `guessed/type`       | Uses the file object's content_type if exists, else guesses type from filename; defaults to `application/octet-stream`. |
| **Iterables** (`list`, `tuple`)           | *Per-element type*   | Flattens the collection into multiple entries using the same key name.                                                  |
| **None**                                  | `application/json`   | Serialized as `null`.                                                                                                   |

### Nested Collection Note
If an iterable (like a list) contains another collection (like a list of lists or a list of dicts), the nested collection is automatically serialized as a JSON string within that form entry.

### Technical Details
The renderer uses a custom boundary string: `BoUnDaRyStRiNgetpvelarptriznzsespgfmagoxpjpjluxkwqroqgsilzbdfsfgffddg`

It adheres to standard multipart formatting, using `\r\n` line endings as required by the HTTP specification.

Every component of the multipart payload (including field names, text values, JSON objects, and headers) is encoded using UTF-8 to ensure universal character compatibility.

## TESTS
To run the test suite for this package, use the following command:

```shell
 DJANGO_SETTINGS_MODULE="src.tests.settings" python -m django test
```

## License
MIT
