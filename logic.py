from pathlib import Path

def gather_file_contents(file_path: list[Path]) ->str:
    """
    Reads a list of files and merges their contents into a single string,
    with headers indicating the file path.
    """

    print(f"")