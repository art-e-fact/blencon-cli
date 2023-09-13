from pathlib import Path
import requests
import sys
import os
import argparse
import sys


# Trick to allow importing from the same directory in Blender
script_dir = os.path.dirname(os.path.realpath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from export_model import export_sdf

CACHE_PATH = Path(".cache")


def download_large_file(url, destination):
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Ensure we got an OK response

    with open(destination, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            # If you have chunk encoded response uncomment if
            # and set chunk_size parameter to None.
            # if chunk:
            f.write(chunk)


def load_asset_meta(asset_base_id: str):
    # Load asset meta data
    url_path = (
        f"https://www.blenderkit.com/api/v1/search/?query=asset_base_id:{asset_base_id}"
    )
    response = requests.get(url_path)
    data = response.json()
    if data["count"] == 0 or data["count"] > 1:
        return
    return data["results"][0]


def add_demo_world(model_name: str):
    with open("demo.sdf.template", "r") as template_file:
        template = template_file.read()

    output_text = template.replace("{{model_path}}", model_name + "/model.sdf")

    demo_path = "models/demo.sdf"
    with open(demo_path, "w") as f:
        f.write(output_text)

    return demo_path


def convert_blender_model(model: str, model_name: str = None):

    blend_file = model
    model_path = Path("models") / model_name

    export_sdf(model_path, model_name, blend_file)

    # Save metadata to index.json TODO

    demo_path = add_demo_world(model_name)



