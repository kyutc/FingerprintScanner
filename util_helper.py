from pathlib import Path


def read_file(file: Path) -> str:
    file_h = Path.open(file, 'r')
    file_contents = file_h.read()
    file_h.close()
    return file_contents


def write_file(file: Path, content: str) -> None:
    file_h = Path.open(file, 'w')
    file_h.write(content)
    file_h.close()
