import argparse
import os
import zipfile
import requests
import shutil
import dotenv
import json
import urllib
from pathlib import Path

from load_blenderkit import convert_blender_model

dotenv.load_dotenv()
FILESERVER_API_KEY = os.getenv("FILESERVER_API_KEY", "")
FILESERVER_URL = os.getenv("FILESERVER_URL", "")


def make_post_request(url, files):
    url = FILESERVER_URL + url + "?extract=true&clean=true"
    # At present all files are uploaded as a zip file.
    response = requests.post(
        url,
        files=files,
        headers={"X-DreamFactory-API-Key": FILESERVER_API_KEY},
        timeout=60,
    )

    return response


def create_zip_file(folder_name):
    zip_filename = f"{folder_name}.zip"
    zip_path = os.path.join("models", zip_filename)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(os.path.join("models", folder_name)):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(
                    file_path,
                    os.path.relpath(file_path, os.path.join("models", folder_name)),
                )

    return zip_filename, zip_path


def delete_folders(folders):
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)


def check_and_get_index():
    response = requests.get(
        FILESERVER_URL + "index.json",
        headers={"X-DreamFactory-API-KEY": FILESERVER_API_KEY},
    )
    if response.status_code == 200:
        # Convert the JSON response to a dictionary
        index = json.loads(response.content)
    elif response.status_code == 404:
        index = {}
    else:
        raise Exception(
            f"Failed to get index.json: {response.status_code} {response.content}"
        )
    return index


def push_model_to_roboprop(model_name):
    zip_filename, zip_path = create_zip_file(model_name)
    # Upload the ZIP file in a POST request
    with open(zip_path, "rb") as zip_file:
        files = {"files": (zip_filename, zip_file)}
        asset_name = os.path.splitext(zip_filename)[0]
        url = f"models/{asset_name}/"
        response = make_post_request(url, files=files)

    delete_folders(["models", "textures"])
    return response


def push_metadata_to_roboprop(metadata_path, model_name):
    # Get index.json
    index = check_and_get_index()
    url_safe_name = urllib.parse.quote(model_name)
    # convert the metadata as json to a dictionary
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    metadata["source"] = "Upload"
    metadata["scale"] = 1.0
    metadata["url"] = f"{FILESERVER_URL}models/{url_safe_name}/?zip=true"
    index[model_name] = metadata
    response = requests.put(
        FILESERVER_URL + "index.json",
        data = json.dumps(index),
        headers={"X-DreamFactory-API-KEY": FILESERVER_API_KEY},
    )
    return response


def main(args):
    # If name is not set, use the filename of the mode  l
    if args.name is None:
        args.name = Path(args.model).stem
    
    # If the metadata is not set, try to use metadata.json in the same folder as the model
    if args.metadata is None:
        args.metadata = str(Path(args.model).parent / "metadata.json")

    convert_blender_model(args.model, args.name)
    response = push_model_to_roboprop(args.name)
    print(response)
    if response.status_code == 201:
        print(f"Successfully uploaded {args.name} to RoboProp, Adding Metadata")
        response = push_metadata_to_roboprop(args.metadata, args.name)
        if response.status_code == 201:
            print(f"Successfully added metadata for {args.name}")
        else:
            print(f"Failed to add metadata for {args.name}")
    else:
        print(f"Failed to upload {args.name} to RoboProp")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        CLI app for converting Blender models to (Gazebo) SDF
        Example usage:
          python load_blenderkit.py --model model.blend --name cat-model
        """
    )

    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="The file location of the model",
    )

    parser.add_argument(
        "--name",
        type=str,
        help="The name of the model. Needs to be Unique. Defaults to the filename of the model without the extension.",
    )

    parser.add_argument(
        "--metadata",
        type=str,
        help="The file location of the metadata. Defaults to metadata.json in the same folder as the model.",
    )

    args = parser.parse_args()

    main(args)
