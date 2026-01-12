import mimetypes
import os
from collections.abc import Iterable
from django.utils.encoding import force_bytes
from rest_framework.renderers import BaseRenderer, JSONRenderer

def to_bytes(s):
    return force_bytes(s, "utf-8")

def is_file(thing):
    return hasattr(thing, "read") and callable(thing.read)

class MultipartRenderer(BaseRenderer):
    """
    Renders a dictionary into a multipart byte string.

    Mapping keys to multipart entry names, this function automatically determines the
    Content-Type of each part based on the Python type of the value.

    Data Type Mapping Logic:
    -----------------------
    The renderer iterates through the input dictionary and processes values as follows:

    - **Strings (`str`)**:
        Encoded as `text/plain`.
    - **Primitives & Objects (`int`, `float`, `bool`, `dict`, `None`)**:
        Serialized via `JSONRenderer` and sent as `application/json`.
    - **Files (`io.IOBase`)**:
        Transmitted with a guessed Content-Type based on the filename.
        Defaults to `application/octet-stream`.
    - **Iterables (`list`, `tuple`, etc.)**:
        Flattened into multiple form entries using the same key name.
        *Note: Nested collections are serialized as JSON.*

    Example:
        >>> data = {
        ...     "title": "Project Alpha",
        ...     "metadata": {"version": 1.0, "active": True},
        ...     "image": open("logo.png", "rb"),
        ...     "tags": ["web", "api"]
        ... }
        >>> renderer = MultipartFormRenderer()
        >>> body = renderer.render(data)
        # Results in a body with 5 parts:
        # 1 plain text, 1 JSON object, 1 binary file, and 2 'tags' text entries.
    """
    boundary = 'BoUnDaRyStRiNgetpvelarptriznzsespgfmagoxpjpjluxkwqroqgsilzbdfsfgffddg'
    media_type = 'multipart/form-data'
    format = 'multipart'
    charset = f'utf-8; boundary={boundary}'

    def encode_str(self, lines, key, val):
        lines.extend(
            to_bytes(val) for val in [f"--{self.boundary}", f'Content-Disposition: form-data; name="{key}"', b"", val])

    def encode_json(self, lines, key, val):
        lines.extend(
            to_bytes(val) for val in [
                f"--{self.boundary}", f'Content-Disposition: form-data; name="{key}"', "Content-Type: application/json",
                b"",
                JSONRenderer().render(val)
            ])

    def encode_file(self, key, file):
        # file.name might not be a string. For example, it's an int for
        # tempfile.TemporaryFile().
        file_has_string_name = hasattr(file, "name") and isinstance(file.name, str)
        filename = os.path.basename(file.name) if file_has_string_name else None

        if hasattr(file, "content_type"):
            content_type = file.content_type
        elif filename:
            content_type = mimetypes.guess_type(filename)[0]
        else:
            content_type = None

        if content_type is None:
            content_type = "application/octet-stream"

        return [
            to_bytes(f"--{self.boundary}"),
            to_bytes(f'Content-Disposition: form-data; name="{key}"{f'; filename="{filename}"' if filename else ''}'),
            to_bytes(f"Content-Type: {content_type}"),
            b"",
            to_bytes(file.read()),
        ]

    def add_lines(self, lines, key, val):
        if isinstance(val, str):
            self.encode_str(lines, key, val)
        elif isinstance(val, int | float | bool | dict) or val is None:
            self.encode_json(lines, key, val)
        elif is_file(val):
            lines.extend(self.encode_file(key, val))
        elif isinstance(val, Iterable):
            for item in val:
                if isinstance(item, list | tuple):
                    self.encode_json(lines, key, item)
                else:
                    self.add_lines(lines, key, item)
        else:
            raise NotImplementedError(f"The {type(val)} type is not supported")

    def render(self, data, accepted_media_type=None, renderer_context=None):
        lines = []

        # Each bit of the multipart form data could be either a form value or a
        # file, or a *list* of form values and/or files. Remember that HTTP field
        # names can be duplicated!
        for key, val in data.items():
            self.add_lines(lines, key, val)

        lines.extend([to_bytes(f"--{self.boundary}--"), b""])
        return b"\r\n".join(lines)