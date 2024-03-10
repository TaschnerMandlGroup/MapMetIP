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

[Daria Lazic](https://github.com/LazDaria)

[Simon Gutwein](https://github.com/SimonBon/)

## References
