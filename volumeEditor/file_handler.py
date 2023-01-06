import io
from pathlib import Path


class FileHandler():

    def __init__(self):
        self.root_filepath = "./files"

    def save_user_file(self, session_id: str, filename: str, file: io.BytesIO):
        filepath = f"{self.root_filepath}/{session_id}/{filename}"
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, mode="wb") as fp:
            file.seek(0)
            fp.write(file.read())

    def get_user_file(self, session_id: str, filename: str) -> io.BytesIO:
        filepath = f"{self.root_filepath}/{session_id}/{filename}"
        if Path(filepath).exists():
            with open(filepath, mode="rb") as fp:
                buffer = io.BytesIO(fp.read())
                buffer.name=filename
            return buffer
