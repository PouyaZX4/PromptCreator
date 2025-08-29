# core/logic.py

from pathlib import Path

# We removed the unused imports for sounddevice, scipy, and numpy.
# This file is now only responsible for file logic.

def gather_file_contents(file_paths: list[Path], root_path: Path) -> str:
    """
    Reads a list of files and merges their contents into a single string.
    Each file's content is prefixed with its relative path and wrapped in
    markdown code fences for AI-friendly formatting.
    """
    full_text_context = []

    for file_path in file_paths:
        try:
            relative_path = file_path.relative_to(root_path)

            # --- THE FIX IS HERE ---
            # 1. First, create the clean path string with forward slashes.
            clean_path_str = str(relative_path).replace('\\', '/')

            # 2. Then, use that clean string inside the f-string. This avoids the backslash error.
            header = f"--- FILE: {clean_path_str} ---\n"
            # --- END OF FIX ---
            
            full_text_context.append(header)

            file_extension = file_path.suffix.lstrip('.')
            opening_fence = f"```{file_extension}\n"
            
            content = file_path.read_text(encoding="utf-8", errors='ignore')

            full_text_context.append(opening_fence)
            full_text_context.append(content)
            full_text_context.append("\n```\n\n")

        except Exception as e:
            error_message = f"--- ERROR READING FILE: {file_path.name} ---\nError: {e}\n\n"
            full_text_context.append(error_message)

    return "".join(full_text_context)