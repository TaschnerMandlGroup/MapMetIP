<img src="https://github.com/TaschnerMandlGroup/MapMetIP/blob/main/docs/img/logo.png" align="right" alt="Logo" width="55" />

# MapMet - Image Processing Pipeline
[comment]: <> (repo-specific shields will work once the repo is online)
![Python Version](https://img.shields.io/badge/python-3.10.9-blue)
![Suggestions Welcome](https://img.shields.io/badge/suggestions-welcome-green)

A pipeline for processing multi-modal (IF and IMC) & multiplexed images within the MapMet (Mapping Metastases in neuroblastoma) project. 

---

* [Introduction](#introduction)
* [Usage](#usage)
* [Support](#support)
* [Authors](#authors)
* [References](#references)

## Introduction

## Usage

In order to use the image-processing pipeline, the following steps have to be performed:
- install environment from env.yml
- download example data and cellpose and ilastik models
- pull docker image for spillover compensation
  
### Installation
- Create a virtual environment
```
$ conda create -n 'mapmet_ip' python=3.10
```
### Docker

### Download example data
[comment]: <> (zenodo get has to be installed first)
```
$ zenodo_get 10.5281/zenodo.10801832
```
## Authors

[Simon Gutwein](https://github.com/SimonBon/)

[Daria Lazic](https://github.com/LazDaria)

## References
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


