## To build and run the docker image:

```shell
sh run.sh
```

## Docker image I/O:
 - Input: a single DICOM or PNG/JPEG image.
 - Output: JSON output with **findings** and **impression** section fields.

## Example requests using `curl` for a DICOM image:

```shell
curl --location '127.0.0.1:80/dicom_to_report' --form 'input_file=@"./e084de3b-be89b11e-20fe3f9f-9c8d8dfe-4cfd202c.dcm"'
```

## Example requests using `curl` for a PNG image:

```shell
curl --location '127.0.0.1:80/image_to_report' --form 'input_file=@"./CXR1_1_IM-0001-3001.png"'
```

## Other information about the Docker image:
 - On an NVIDIA RTX 3090, uses 2GB of VRAM.
 - Uses 3.3GB of RAM.
 - The model that is being used: https://huggingface.co/aehrc/cxrmate-single-tf. 
 - The paper (under review) that the model is from: https://arxiv.org/pdf/2307.09758.pdf.
 - Note that this is the simplest model from the paper, there are several improvements (let me know if you want to try to handle one of these cases):
    - Conditioning all the X-rays of a patient's study: https://huggingface.co/aehrc/cxrmate-multi-tf,
    - Additionally conditioning on the report from the patient's previous study: https://huggingface.co/aehrc/cxrmate-tf.
    - Additionally training with reinforcement learning: https://huggingface.co/aehrc/cxrmate.

## To run outside of Docker (this will allow you to use Apple silicon GPUs):
 1. Install the packages from `requirements.txt` in a virtual environment, e.g., https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/.
 2. Run: ```uvicorn api.api:api --host 0.0.0.0 --port 80 --log-level trace```
