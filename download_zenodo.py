import requests

def download_and_save(url, save_path):
    """
    Download a file from a given URL and save it to a specified path.

    Parameters:
    - url (str): The URL of the file to download.
    - save_path (str): The path (including filename) where the file should be saved.
    """

    try:
        # Send a GET request to the URL
        response = requests.get(url, stream=True)

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=128):
                    file.write(chunk)
            print(f"File successfully downloaded and saved to {save_path}")
        else:
            print(f"Failed to download the file. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
url = "https://zenodo.org/records/10801832/files/MapMet_TestDataset.zip"  # Replace with your actual URL
save_path = "/data_isilon_main/isilon_images/10_MetaSystems/MetaSystemsData/Multimodal_Imaging_Daria/Publication/test_data.zip"
download_and_save(url, save_path)

#also works from bash:
# zenodo_get 10.5281/zenodo.10801832