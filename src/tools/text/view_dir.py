from pathlib import Path


def view_directory(directory: Path):
    if not directory.is_dir():
        raise ValueError(f"Path {directory} is not a directory.")

    result = ""
    files = list(directory.iterdir())

    for i, file in enumerate(files):
        prefix = "└─ " if i == len(files) - 1 else "├─ "
        result += f"{prefix}{file.name}"
        if file.is_dir():
            result += "/"
        result += "\n"

    return f"<directory path={directory}>\n{result}</directory>"


if __name__ == "__main__":
    print(view_directory(Path(".")))
