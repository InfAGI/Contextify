from pathlib import Path
from charset_normalizer import from_bytes


def read_file(file_path: Path, start_line: int = 1, end_line: int = -1):
    raw_data = file_path.read_bytes()
    result = from_bytes(raw_data).best()
    if result is None:
        encoding = "utf-8"
    else:
        encoding = result.encoding

    content = file_path.read_text(encoding=encoding, errors="replace").expandtabs()

    lines = content.splitlines()
    start_line = max(1, start_line)
    end_line = min(len(lines), end_line) if end_line != -1 else len(lines)

    range_content = ""
    for i in range(start_line - 1, end_line):
        range_content += f"{i + 1}: {lines[i]}\n"

    if start_line > 1:
        range_content = (
            f"(From start line 1 to end line {start_line - 1} are omitted.)\n"
            + range_content
        )

    if end_line < len(lines):
        range_content += (
            f"(From start line {end_line + 1} to end line {len(lines)} are omitted.)\n"
        )

    return f"<file path={file_path}>\n{range_content}</file>"


if __name__ == "__main__":
    # file_path = ".gitignore"
    file_path = "C:\\\\\\\\Users\\\\\\\\hylnb\\\\\\\\Workspace\\\\\\\\deploy\\\\\\\\valuecell\\\\\\\\README.md"
    res = read_file(Path(file_path))
    print(res)
    res = read_file(Path(file_path), start_line=3, end_line=3)
    print(res)
