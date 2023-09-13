# BlenCon - Convert Blenderfiles to SDF

BlenCon is a CLI tool that will convert Blenderfiles to SDF, and then push the created model up to a Roboprop Server Instance, along with any associated metadata.

Models will be created in `.obj` as well as `.glb`

## Usage

### Environment Variables

* Replace `example.env` with `.env` and add the necessary values

### Running
BlenCon takes 3 arguments:

```
--model # location of your blender model .blend file
--name # name of your model
--metadata # location of metadata file (as JSON)
```

To use run:
```
python main.py --model <.blend_model_path> --name <model_name> --metadata <metadata_file_path>
```

