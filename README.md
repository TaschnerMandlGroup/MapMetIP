<img src="https://github.com/TaschnerMandlGroup/MapMetIP/blob/main/docs/img/logo.png" align="right" alt="Logo" width="55" />

# MapMet - Image Processing Pipeline
[comment]: <> (repo-specific shields will work once the repo is online)
![Python Version](https://img.shields.io/badge/python-3.10.9-blue)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10801832.svg)](https://doi.org/10.5281/zenodo.10801832)
![Suggestions Welcome](https://img.shields.io/badge/suggestions-welcome-green)

_This repository is currently under development._

This code supplements the publication (in preparation) by Lazic, Gutwein et al. Therein, we use 3-plex immmunofluorescence (IF) microscopy and 41-plex imaging mass cytometry (IMC) to spatially and temporally map primary and metastatic neuroblastoma. The image processing pipeline can be largely divided into the following steps:
1. **Segmentation** based on nuclear IF (DAPI) image using [cellpose](https://github.com/MouseLand/cellpose) [1] model finetuned on our own data - individual models were trained for primary tumor (`CP_TU`) and metastatic bone marrow samples (`CP_BM`)
2. **Registration** between IF and IMC images/masks via scale-invariant feature transformation ([SIFT](https://ieeexplore.ieee.org/document/6396024)) [2]
3. **Spillover compensation** of IMC images according to [[3]](https://github.com/BodenmillerGroup/cyTOFcompensation)
4. **DIMR hot pixel removal** according to [[4]](https://github.com/PENGLU-WashU/IMC_Denoise)
5. **Background correction and normalization** using background/foreground classifiers trained in [Ilastik](https://github.com/ilastik/ilastik/tree/main) [5] - individual models were trained for each marker and tissue type (primary tumor/bone marrow)
6. **Feature Extraction**: extraction of marker intensity and morphological features

## Installation

 <details>
 <summary><strong>Docker</strong></summary>
  
 The test dataset and models required to run `MapMetIP`are downloaded autmoatically during container startup. 
 First, clone the repository.
 
 ```bash
 git clone https://github.com/TaschnerMandlGroup/MapMetIP.git
 ```
 Build the docker image.
 ```bash
 cd MapMetIP
 docker build -t mapmet_ip .
 ```
 The docker-based implementation assumes that the R-based docker image for spillover compensation was pulled from docker hub. 
 ```bash
 docker image pull lazdaria/spillovercomp
 ```
 Then start the mapmet_ip container, mounting
 - the Docker daemon socket to ensure that the the R-based docker container for spillover compensation can be started from within
 - the MapMetIP project directory and
 - the data volume (`/path/to/data` for storing the test dataset and models - will be automatically downloadeded during container startup)
 - access to GPUs on host
 
 The R-based docker container is launched by the host's Docker daemon and hence requires the aboslute path to the host data volume (`/absolute/path/to/data`).

 ```bash
 docker run -e "DOODPATH=</absolute/path/to/data>" -p 8888:8888 -v /var/run/docker.sock:/var/run/docker.sock -v "$(pwd)":/usr/src/app/MapMetIP  -v </path/to/data>:/data --gpus all -it mapmet_ip
 ```
A Jupyter Notebook server session can then be accessed via your browser at `localhost:8888`. The `stdout` of the started container will provide a token, which has to be copied for login.

 </details>
    
 <details>
 <summary><strong>Manual</strong></summary>

 First clone the repository:
 ```bash
 git clone https://github.com/TaschnerMandlGroup/MapMetIP.git
 ```
 It is recommended to install `MapMetIP` into a conda environment together with other necessary packages. If you are new to conda, please refer to these [instructions](https://biapol.github.io/blog/mara_lampert/getting_started_with_mambaforge_and_python/readme.html) first. 
 ```bash
 cd MapMetIP
 conda env create -f env.yml
 ```
 You can then activate the environment:
 ```bash
 conda activate mapmet_ip
 ```
 And install `MapMetIP`
 ```bash
 pip install -e .
 ```
 Then pull R-based image for spillover compensation:
 ```bash
 docker image pull lazdaria/spillovercomp
 ```
 To be able to use DIMR hot-poxel removal, clone the [IMC-Denoise github repository]() to the parent directory of MapMetIP. 
 ```bash
 cd ..
 git clone --branch v1.0.0 https://github.com/PENGLU-WashU/IMC_Denoise.git
 ```
 In case problems with Tensorflow versions, occur, add the path to the IMC_Denoise parent directory to your `~/.bashrc`:
 ```bash
 export PYTHONPATH="${PYTHONPATH}:{pwd}}"
 ```
 </details>
  
## Download data

<details>
 <summary><strong>Download cellpose models, spillover measurements and ilastik classifiers</strong></summary>
 
 In order to be able to use the segmentation, spillover compensation and background correction within `MapMetIP`, the fine-tuned cellpose models, spillover measurements and ilastik-trained background/foreground classifiers have to be downloaded from `zenodo`. 
 <!--also possible like this: zenodo_get 10.5281/zenodo.10801832-->
 Replace `path/to/extract/directory` with the absolute path to the directory, where the data should be stored.
 ```bash
 wget -P <path/to/extract/directory> https://sandbox.zenodo.org/records/34881/files/MapMetIP_models.zip
 unzip <path/to/extract/directory>/MapMetIP_models.zip -d <path/to/extract/directory>
 rm <path/to/extract/directory>/MapMetIP_models.zip
 ```
 </details>
<details>
 <summary><strong>Download test dataset</strong></summary>
 
 We prepared a small test dataset with one representative primary tumor and bone marrow sample to be used in the notebooks for demonstration purposes.
 Replace `path/to/extract/directory` with the absolute path to the directory, where the data should be stored.
 ```bash
 wget -P <path/to/extract/directory> https://sandbox.zenodo.org/records/34881/files/MapMetIP_TestDataset.zip
 unzip <path/to/extract/directory>/MapMetIP_TestDataset.zip -d <path/to/extract/directory>
 rm <path/to/extract/directory>/MapMetIP_TestDataset.zip
 ```
 </details>
<details>
 <summary><strong>Download full dataset</strong></summary>
 
 The entire dataset, described in Lazic et al., will be uploaded with the publication.
 </details>
  
## Usage

<details>
 <summary><strong>Notebooks for demonstration</strong></summary>
 
 Notebooks, demonstrating each step of the pipeline on the primary tumor sample are provided:
 - Demonstration of pipeline on one representative tumor sample ([tests/process_TU_sample.ipynb](https://github.com/TaschnerMandlGroup/MapMetIP/blob/main/tests/process_TU_sample.ipynb))
 - Demonstration of pipeline on one representative bone marrow sample([tests/process_BM_sample.ipynb](https://github.com/TaschnerMandlGroup/MapMetIP/blob/main/tests/process_BM_sample.ipynb)) 
 </details>
<details>
 <summary><strong>Process multiple samples from CL</strong></summary>
 

 First, make sure the conda environment is activated. 
 ```bash
 conda activate mapmet_ip
 ```
 To run the complete image processing pipeline on a defined sample, use the command below. 
 ```bash
 cd MapMetIP
 python3 run_all.py -s <sample_name> --data_path <path/to>/MapMetIP_TestDataset/raw_data --model_path <path/to>/MapMetIP_models --save_dir <path/to/save/results> --log_path <path/to/save/logs>
 ```
 To run the complete image processing pipeline on a list of samples, use the command below.
 ```bash
 cd MapMetIP
 python3 run_all.py -s <sample_name1> <sample_2> <sample_name3> --data_path <path/to>/MapMetIP_TestDataset/raw_data --model_path <path/to>/MapMetIP_models --save_dir <path/to/save/results> --log_path <path/to/save/logs>
 ```
 </details>

## Contributors

[Daria Lazic](https://github.com/LazDaria)

[Simon Gutwein](https://github.com/SimonBon/)

## Citation

Please cite the following paper (in preparation) when using `MapMetIP`:

>  Lazic, D., Gutwein, S., Humhal V. et al. Title to be selected. Journal (2024). https://doi.org/DOI

    @article{Lazic2024,
        author = {Lazic, Daria and Gutwein, Simon and },
        title = {Title to be selected},
        year = {2024},
        doi = {DOI},
        URL = {URL},
        journal = {Journal}
    }

## References

- [1] [Pachitariu et al. (2022), Nature Methods.](https://www.nature.com/articles/s41592-022-01663-4)
- [2] [Mahesh et al. (2012), ICCCNT'12.](https://ieeexplore.ieee.org/document/6396024)
- [3] [Chevrier et al. (2018), Cell Systems.](https://doi.org/10.1016/j.cels.2018.02.010)
- [4] [Lu et al. (2023), Nature Communications.](https://www.nature.com/articles/s41467-023-37123-6)
- [5] [Berg et al. (2019), Nature Methods.](https://www.nature.com/articles/s41592-019-0582-9)

## Funding

This work was funded by the Austrian Science Fund (FWF#I4162 and FWF#35841), the Vienna Science and Technology Fund (WWTF; LS18-111), the Swiss Government Excellence Scholarship and the St. Anna Kinderkrebsforschung e.V.

