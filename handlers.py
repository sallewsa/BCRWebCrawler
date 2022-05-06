import os
import uuid
from urllib.parse import urlparse


class LocalStoragePDFHandler:
    def __init__(self, directory, subdirectory):
        self.directory = directory
        self.subdirectory = subdirectory

    def handle(self, response, *args, **kwargs):
        parsed = urlparse(response.url)
        filename = str(uuid.uuid4()) + ".pdf"
        subdirectory = self.subdirectory or parsed.netloc
        directory = os.path.join(self.directory, subdirectory)
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, filename)
        path = _ensure_unique(path)
        with open(path, 'wb') as f:
            f.write(response.content)

        return path


def _ensure_unique(path):
    if os.path.isfile(path):
        short_uuid = str(uuid.uuid4())[:8]
        path = path.replace('.pdf', f'-{short_uuid}.pdf')
        return _ensure_unique(path)
    return path
