import sys

def open_file(path: str):
    try:
        return open(path, encoding="utf-8")
    except FileNotFoundError:
        print(f"Failo \"{path}\" nėra.")
        
        sys.exit(1)