module load apptainer

# Temporary:
export SINGULARITY_BINDPATH=/apps:/apps,/datasets:/datasets,/scratch1:/scratch1,/scratch2:/scratch2,/flush5:/flush5

export ROENTGEN_CUDA_DEVICE=$1  # Use 'nvidia-smi' to find a free device.
IMAGE_PATH=/datasets/work/hb-digitaltwin/work/images/roentgen_server.sif
APPTAINERENV_CUDA_VISIBLE_DEVICES=$ROENTGEN_CUDA_DEVICE apptainer run --pwd / --nv $IMAGE_PATH $2
