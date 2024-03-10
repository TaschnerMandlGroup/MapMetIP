<img src="https://github.com/TaschnerMandlGroup/MapMetIP/blob/main/docs/img/logo.png" align="right" alt="Logo" width="55" />

# MapMet - Image Processing Pipeline
[comment]: <> (repo-specific shields will work once the repo is online)
![Python Version](https://img.shields.io/badge/python-3.10.9-blue)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10801832.svg)](https://doi.org/10.5281/zenodo.10801832)
![Suggestions Welcome](https://img.shields.io/badge/suggestions-welcome-green)

A pipeline for processing multi-modal (IF and IMC) multiplexed images within the MapMet (Mapping Metastases in neuroblastoma) project. 

---

* [Overview](#overview)
* [Installation](#installation)
* [Usage](#usage)
* [Contributors](#contributors)
* [Citation](#citation)
* [References](#references)
* [Funding](#funding)

## Overview
This code supplements the [publication]() by Lazic, Gutwein et al. Therein, we use 3-plex immmunofluorescence (IF) microscopy and 41-plex imaging mass cytometry (IMC) to spatially and temporally map primary and metastatic neuroblastoma. The pipeline can be largely divided into the following steps:
1. **Segmentation** based on nuclear IF (DAPI) image using [cellpose](https://github.com/MouseLand/cellpose) [1] model finetuned on our own data - individual models were trained for primary tumor (`CP_TU`) and metastatic bone marrow samples (`CP_BM`)
2. **Registration** between IF and IMC images/masks via scale-invariant feature transformation ([SIFT](https://ieeexplore.ieee.org/document/6396024)) [2]
3. **Spillover compensation** of IMC images according to [[3]](https://github.com/BodenmillerGroup/cyTOFcompensation)
4. **DIMR hot pixel removal** according to [[4]](https://github.com/PENGLU-WashU/IMC_Denoise)
5. **Background correction and normalization** using background/foreground classifiers trained in [Ilastik](https://github.com/ilastik/ilastik/tree/main) [5] - individual models were trained for each marker and tissue type (primary tumor/bone marrow)
6. **Feature Extraction**: extraction of marker intensity and morphological features

## Installation

First clone the repository:
```ruby
git clone https://github.com/TaschnerMandlGroup/MapMetIP.git
```
It is recommended to install `MapMetIP` into a conda environment together with other necessary packages. If you are new to conda, please refer to these [instructions](https://biapol.github.io/blog/mara_lampert/getting_started_with_mambaforge_and_python/readme.html) first. 
```ruby
conda env create -f env.yml
```
You can then activate the environment:
```ruby
conda activate mapmet_ip
```
And install `MapMetIP`
```ruby
cd MapMetIP
pip install -e .
```
## Usage
In order to be able to use the segmentation and background correction within `MapMetIP`, the segmentation models and background/foreground classifiers are required. We will download the fine-tuned cellpose models and ilastik-trained background/foreground classifiers, along with a test dataset, from `zenodo`. 
### Download cellpose models, ilastik classifiers and test data
[comment]: <> (also possible like this: zenodo_get 10.5281/zenodo.10801832)
```ruby
cd ..
wget https://sandbox.zenodo.org/records/34123/files/MapMet_TestDataset.zip
unzip MapMet_TestDataset.zip
```
If you want to unzip the file into a specific directory, use:
```ruby
unzip MapMet_TestDataset.zip - /path/to/extract_directory
```
### Pull R-based docker image for spillover compensation
Spillover compensation is executed in an R-based docker container. In case you need to setup docker, follow these [instructions](https://docs.docker.com/get-started/overview/). Then, pull our image from docker hub. 
```ruby
docker image pull mapmetip_spillovercomp
```
### Testing

Notebooks demonstrating each step of the pipeline on one representative primary tumor sample ([tests/process_TU_sample.ipynb](https://github.com/TaschnerMandlGroup/MapMetIP/blob/main/tests/process_TU_sample.ipynb)) and one representative bone marrow sample ([tests/process_BM_sample.ipynb](https://github.com/TaschnerMandlGroup/MapMetIP/blob/main/tests/process_BM_sample.ipynb)) are provided. 

### Process entire dataset
To process the entire dataset, described in Lazic et al., download the complete dataset:
```ruby
wget https://sandbox.zenodo.org/records/34123/files/MapMet_FullDataset.zip #to be uploaded
unzip MapMet_FullDataset.zip
```
And either run sample per sample using 
```ruby
python3 main.py -s path/to/your/sample #make sure this works, are more args needed?
```
or the full dataset via
```ruby
python3 run_all.py -s sample1 sample2 sample3 #find out how the directory can be passed instead samples
```
## Contributors

[Simon Gutwein](https://github.com/SimonBon/)

[Daria Lazic](https://github.com/LazDaria)

## Citation
Please cite the following paper when using `MapMetIP`:

>  Lazic, D., Gutwein, S., Humhal V. et al. Mapping Metastases in Neuroblastoma. Nat Cancer (2024). https://doi.org/DOI

    @article{Lazic2024,
        author = {Lazic, Daria and Gutwein, Simon and },
        title = {Mapping Metastases in Neuroblastoma},
        year = {2024},
        doi = {DOI},
        URL = {URL},
        journal = {Nature Cancer - let's hope}
    }

## References
- [1] [Pachitariu et al. (2022), Nature Methods.](https://www.nature.com/articles/s41592-022-01663-4)
- [2] [Mahesh et al. (2012), ICCCNT'12.](https://ieeexplore.ieee.org/document/6396024)
- [3] [Chevrier et al. (2018), Cell Systems.](https://doi.org/10.1016/j.cels.2018.02.010)
- [4] [Lu et al. (2023), Nature Communications.](https://www.nature.com/articles/s41467-023-37123-6)
- [5] [Berg et al. (2019), Nature Methods.](https://www.nature.com/articles/s41592-019-0582-9)

## Funding

This work was funded by the Austrian Science Fund (FWF#I4162 and FWF#35841), the Vienna Science and Technology Fund (WWTF; LS18-111), the Swiss Government Excellence Scholarship and the St. Anna Kinderkrebsforschung e.V.

