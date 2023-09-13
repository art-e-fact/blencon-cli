import argparse
import os
import zipfile
import requests
import shutil
import dotenv

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

def push_model_to_roboprop(model_name):
    zip_filename, zip_path = create_zip_file(model_name)
    # Upload the ZIP file in a POST request
    with open(zip_path, "rb") as zip_file:
        files = {"files": (zip_filename, zip_file)}
        asset_name = os.path.splitext(zip_filename)[0]
        url = f"models/{asset_name}/"
        response = make_post_request(url, files=files)
    
    delete_folders(["models", "textures"])

def main(args):
    convert_blender_model(args.model, args.name)
    response  = push_model_to_roboprop(args.name)
    
    


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
        help="The name of the model. Needs to be Unique",
    )

    args = parser.parse_args()

    main(args)
