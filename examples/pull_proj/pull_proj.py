import os
import subprocess
from pathlib import Path


def main():
    """
    Main function to read URLs from a file and clone the repositories into a target directory.

    Functionality:
    1. Defines source file path containing URLs and target directory for cloning.
    2. Ensures the target directory exists.
    3. Reads the list of URLs from the source file.
    4. Iterates through each URL and executes a 'git clone' command.

    Dependencies:
    - os: For directory operations and path handling.
    - subprocess: For executing shell commands (git clone).
    - pathlib: For robust path manipulation.

    Constraints:
    - Assumes 'git' is installed and available in the system PATH.
    - Assumes the user has permissions to write to the target directory.
    - Assumes the URLs in the file are valid git repository URLs.
    """

    # Define the absolute paths for the source file and target directory
    # Using raw strings for Windows paths to avoid escape character issues
    urls_file_path = Path(r"c:\Users\hylnb\Workspace\Contextify\.contextify\urls.txt")
    target_directory = Path(r"C:\Users\hylnb\Workspace\deploy_benchmark")

    # Check if the URLs file exists
    if not urls_file_path.exists():
        print(f"Error: URLs file not found at {urls_file_path}")
        return

    # Ensure the target directory exists; create it if it doesn't
    if not target_directory.exists():
        print(f"Target directory {target_directory} does not exist. Creating it...")
        try:
            target_directory.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"Error creating directory {target_directory}: {e}")
            return

    print(f"Reading URLs from: {urls_file_path}")
    print(f"Cloning into: {target_directory}")

    # Read the URLs from the file
    try:
        with open(urls_file_path, "r", encoding="utf-8") as f:
            # Read lines and strip whitespace
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading file {urls_file_path}: {e}")
        return

    # Iterate over each URL and clone the repository
    repo_paths = []

    for url in urls:
        print(f"\nProcessing URL: {url}")

        # Extract the repository name from the URL to check if it already exists
        # e.g., https://github.com/open-webui/open-webui -> open-webui
        repo_name = url.split("/")[-1].replace(".git", "")
        repo_path = target_directory / repo_name

        if repo_path.exists():
            print(
                f"Repository '{repo_name}' already exists in {target_directory}. Skipping..."
            )
            repo_paths.append(str(repo_path.resolve()))
            continue

        try:
            # Construct the git clone command
            # We run this in the target directory context or pass the full path
            # Using subprocess.run to execute the command
            # cwd=target_directory ensures the repo is cloned INTO the target dir
            print(f"Cloning {url}...")
            result = subprocess.run(
                ["git", "clone", url],
                cwd=target_directory,
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"Successfully cloned {repo_name}")
            repo_paths.append(str(repo_path.resolve()))
            # print(result.stdout) # Optional: print git output

        except subprocess.CalledProcessError as e:
            print(f"Failed to clone {url}")
            print(f"Error: {e.stderr}")
        except Exception as e:
            print(f"An unexpected error occurred while cloning {url}: {e}")

    print(f"Repo paths: {repo_paths}")


if __name__ == "__main__":
    main()
