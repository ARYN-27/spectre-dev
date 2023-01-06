# SPECTRE (ANN based IDS)

VGG-19 deep learning model trained using ISCX 2012 IDS Dataset

## Prepping Datasets
1. Download the [ISCX 2012](http://www.unb.ca/cic/datasets/ids.html) Dataset
2. Convert `.pcap` to `.xml` using [ISCX FlowMeter](https://github.com/ISCX/ISCXFlowMeter) or [CIC FlowMeter](https://github.com/ISCX/CICFlowMeter).
3. Preprocess data from `.xml` to `.npy` with `Data_Extraction_Revised.py`.

## Setup Development Environment
- Use the Docker containers available in the repo.
    - Tensorflow Container: `dev-tensorflow`
    - Ubuntu 20.04 - Cuda Container: `dev-ubuntu-cuda`

## Run the Python Notebook to train
- `FYP-Revised.ipynb`

