from pathlib import Path
from src.tools.text.read_file import read_raw_file
from src.tools.text.write_file import write_file


def insert_file(
    file_path: Path,
    new_content: str,
    insert_line: int = -1,
):
    old_content = read_raw_file(file_path)

    new_content = new_content.expandtabs()
    lines = old_content.splitlines()

    if insert_line == -1:
        insert_line = len(lines) + 1

    if insert_line <= 0 or insert_line > len(lines) + 1:
        raise ValueError(
            f"insert_line must be in range [1, {len(lines) + 1}], but got {insert_line}"
        )

    lines.insert(insert_line - 1, new_content)
    new_content = "\n".join(lines)

    return write_file(
        file_path,
        old_content,
        new_content,
    )


if __name__ == "__main__":
    file_path = ".gitignore"

    diff_str = insert_file(
        Path(file_path),
        new_content="""test""",
    )
    print(diff_str)
