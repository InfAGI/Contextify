from pathlib import Path
from src.tools.text.read_file import read_raw_file
from src.tools.text.write_file import write_file


def replace_file(
    file_path: Path,
    start_line: int,
    end_line: int,
    new_content: str,
):
    content = read_raw_file(file_path)
    new_content = new_content.expandtabs() if new_content else ""

    lines = content.splitlines()
    start_line = max(1, start_line)
    end_line = min(len(lines), end_line) if end_line != -1 else len(lines)

    pre_content = ""
    post_content = ""
    if start_line > 1:
        pre_content = "\n".join(lines[: start_line - 1])
    if end_line < len(lines):
        post_content = "\n".join(lines[end_line:])

    new_content = "\n".join(
        [
            pre_content,
            new_content,
            post_content,
        ]
    )
    return write_file(
        file_path,
        content,
        new_content,
    )


# def replace_file(
#     file_path: Path,
#     old_str: str,
#     new_str: str,
# ):
#     old_content = read_raw_file(file_path)

#     old_str = old_str.expandtabs()
#     new_str = new_str.expandtabs() if new_str else ""

#     occurrences = old_content.count(old_str)
#     if occurrences == 0:
#         raise ValueError(
#             f"No replacement was performed, old_str `{old_str}` did not appear verbatim in {file_path}."
#         )
#     elif occurrences > 1:
#         file_content_lines = old_content.splitlines()
#         lines = [
#             idx + 1 for idx, line in enumerate(file_content_lines) if old_str in line
#         ]
#         raise ValueError(
#             f"No replacement was performed. Multiple occurrences of old_str `{old_str}` in lines {lines}. Please ensure it is unique."
#         )

#     new_content = old_content.replace(old_str, new_str)
#     return write_file(
#         file_path,
#         old_content,
#         new_content,
#     )


if __name__ == "__main__":
    file_path = ".gitignore"

    # diff_str = replace_file(
    #     Path(file_path),
    #     old_str="test",
    #     new_str="",
    # )
    diff_str = replace_file(
        Path(file_path),
        start_line=5,
        end_line=5,
        new_content="xx",
    )
    print(diff_str)
