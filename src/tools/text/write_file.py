import difflib
from pathlib import Path


def write_file(file_path: Path, old_content: str, new_content: str):
    new_content = new_content.expandtabs()
    file_path.write_text(new_content, encoding="utf-8")
    diff = difflib.unified_diff(
        old_content.splitlines(),
        new_content.splitlines(),
        fromfile=str(file_path),
        tofile=str(file_path),
    )
    return "\n".join(list(diff))


if __name__ == "__main__":
    file_path = ".gitignore"

    diff_str = write_file(
        Path(file_path),
        old_content=Path(file_path).read_text(),
        new_content="""*.log
__pycache__/
.cache/
.contextify/""",
    )
    print(diff_str)
