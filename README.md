# SPECTRE (ANN based IDS)


## Dataset Used 

1. CICIDS2017
2. ISCX-IDS-2012
3. DDoS Dataset

## Prepping Datasets

### ISCX 2012
1. Download the [ISCX 2012](http://www.unb.ca/cic/datasets/ids.html) Dataset
2. Convert `.pcap` to `.xml` using [ISCX FlowMeter](https://github.com/ISCX/ISCXFlowMeter) or [CIC FlowMeter](https://github.com/ISCX/CICFlowMeter).
3. Preprocess data from `.xml` to `.npy` with `Data_Extraction_Revised.py`.

### CICIDS2017


## Setup Development Environment
- Use the Docker containers available in the repo:
    - Tensorflow Container: `dev-tensorflow`
    - Ubuntu 20.04 - Cuda Container: `dev-ubuntu-cuda`


References: 
- [VGG-19 deep learning model trained using ISCX 2012 IDS Dataset](https://github.com/tamimmirza/Intrusion-Detection-System-using-Deep-Learning)
- [SafeML and Intrusion Detection Evaluation Dataset (CICIDS2017)](https://www.kaggle.com/code/kooaslansefat/cicids2017-safeml/notebook)
 
