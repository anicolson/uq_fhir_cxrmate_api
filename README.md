# RoentGen FastAPI server Apptainer image

The server is in `api.py`

## Start the server:

Note: a GPU is needed. `bracewell-i1.hpc.csiro.au` is good place to do a quick test.

<!-- Temporary while flush6 is being decomissioned:
```shell
module load apptainer
export SINGULARITY_BINDPATH=/apps:/apps,/datasets:/datasets,/scratch1:/scratch1,/scratch2:/scratch2,/flush5:/flush5
``` -->


```shell
module load apptainer
export ROENTGEN_CUDA_DEVICE=0  # Use 'nvidia-smi' to find a free device.
IMAGE_PATH=/datasets/work/hb-digitaltwin/work/images/roentgen_server.sif
PORT=8005
APPTAINERENV_CUDA_VISIBLE_DEVICES=$ROENTGEN_CUDA_DEVICE apptainer run --pwd / --nv $IMAGE_PATH $PORT
```

or 

```shell
ROENTGEN_CUDA_DEVICE=0
PORT=8005
server.sh $ROENTGEN_CUDA_DEVICE $PORT
```

## Request to the server:

See `request.ipynb` for an example of a request to the server (run the Apptainer image first).

In python:

```python
url = 'http://127.0.0.1:8005/image'

x = {'prompt': 'left-sided pacemaker device is noted with leads terminating in the right atrium and right ventricle'}

received = requests.post(url, json=json.dumps(x))
```

Read the received bytes as a PILLOW image:

In python:

```python
Image.open(io.BytesIO(received.content))
```

## Building the Apptainer image:

`petrichor-login` is good for this as it is fast and has internet connection.

```shell
export APPTAINER_CACHEDIR=/scratch2/nic261/apptainer_cache  # Avoid exceeding the home directory quota.
WORK_DIR=/datasets/work/hb-digitaltwin/work/roentgen_api 
IMAGES_DIR=/datasets/work/hb-digitaltwin/work/images 
module load apptainer
cd $WORK_DIR
APPTAINER_BINDPATH="" SINGULARITY_BINDPATH="" apptainer build $IMAGES_DIR/roentgen_server.sif server.def
```
