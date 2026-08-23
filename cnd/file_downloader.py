import os
from pathlib import Path
import requests
import concurrent.futures
from urllib.parse import urlparse
from typing import List, Tuple


def download_file(url: str, destination_folder: Path) -> Tuple[str, bool]:
    """
    Downloads a single file from a URL to a specified folder.

    Args:
        url (str): The URL of the file to download.
        destination_folder (str): The path to the folder where the file will be saved.

    Returns:
        tuple: A tuple containing the URL and a boolean indicating success.
    """
    try:
        # Extract filename from the URL and construct the full path
        filename = os.path.basename(urlparse(url).path)
        if not filename:
            # Handle cases where the URL doesn't have a clear filename
            filename = url.split("/")[-1]

        filepath = os.path.join(destination_folder, filename)

        # print(f"Starting download of {filename}...")

        # Use stream=True to download the file in chunks, which is memory-efficient
        with requests.get(url, stream=True) as response:
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            with open(filepath, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

        # print(f"Successfully downloaded {filename}")
        return url, True

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return url, False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return url, False


def download_files_parallel(
    urls: List[str], destination_folder: Path, max_workers: int = 5
) -> None:
    """
    Downloads multiple files in parallel using a ThreadPoolExecutor.

    Args:
        urls (list): A list of URLs of the files to download.
        destination_folder (str): The path to the folder where files will be saved.
        max_workers (int): The maximum number of threads to use for downloading.
    """
    # Create the destination folder if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Use a dictionary to map futures to URLs, allowing us to track which download is which
        future_to_url = {
            executor.submit(download_file, url, destination_folder): url for url in urls
        }

        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                # Retrieve the result of the download task
                url_result, success = future.result()
                if success:
                    print(f"Finished processing {url_result}")
                else:
                    print(f"Failed to process {url_result}")
            except Exception as e:
                print(f"An exception occurred for {url}: {e}")


if __name__ == "__main__":
    # List of sample URLs to download. You can replace these with your own.
    sample_urls = [
        "https://www.w3.org/TR/PNG/iso_8859-1.txt",
        "https://www.gutenberg.org/files/2701/2701-0.txt",
        "https://www.gutenberg.org/files/1342/1342-0.txt",
    ]

    # Define the folder where the files will be saved
    download_dir = Path("downloads")

    print(
        f"Starting parallel download of {len(sample_urls)} files to the '{download_dir}' directory..."
    )
    download_files_parallel(sample_urls, download_dir)
    print("All download tasks have been submitted.")
