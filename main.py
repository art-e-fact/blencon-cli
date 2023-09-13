import argparse
from load_blenderkit import convert_blender_model

def main(args):
    convert_blender_model(args.model, args.name)


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
