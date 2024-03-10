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
* [Contributing](#contributing)
* [License](#license)

## Introduction
## Installation

### Binary installation

Go to the [download page][download-page], get the latest _non-beta_ version for your operating system, and follow the [installation instructions][how-to-install].
If you are new to ilastik, we suggest to start from the [pixel classification workflow][pixel-classification].
If you don't have a dataset to work with, download one of the example projects to get started.

### Conda installation (experimental)

ilastik is also available as a conda package on our `ilastik-forge` conda channel.
We recommend using [mamba][mamba] instead of conda, for faster installation:

```bash
mamba create -n ilastik --override-channels -c pytorch -c ilastik-forge -c conda-forge ilastik

# activate ilastik environment and start ilastik
conda activate ilastik
ilastik
````

#### Python compatibility notes

Versions of ilastik until `1.4.1b2` are based on, and only compatible with Python `3.7`
Starting from ilastik `1.4.1b3` ilastik environments can be created with Python versions `3.7` to `3.9`.
Limitations when going with Python `3.7`: please use a version of tifffile `>2020.9.22,<=2021.11.2` (see also note in [environment-dev.yml](dev/environment-dev.yml)).


## Usage

ilastik is a collection of workflows, designed to guide you through a sequence of steps.
You can select a new workflow, or load an existing one, via the [startup screen][startup].
The specific steps vary between workflows, but there are some common elements like [data selection][data-selection] and [data navigation][data-navigation].
See more details on the [documentation page][documentation].

## Support

If you have a question, please create a topic on the [image.sc forum][imagesc-url].
Before doing that, [search][imagesc-search] for similar topics first: maybe your issue has been already solved!
You can also open an [issue][issues] here on GitHub if you have a technical bug report and/or feature suggestion.

## Contributing

We always welcome good pull requests!
If you just want to suggest a documentation edit, [you can do this directly here, on GitHub][edit-files-on-github].
For more complex changes, see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

[GPL](LICENSE)

[circleci-img]: https://img.shields.io/circleci/build/github/ilastik/ilastik/main?logo=circleci
[circleci-url]: https://app.circleci.com/pipelines/github/ilastik/ilastik?branch=main
[appveyor-img]: https://img.shields.io/appveyor/build/ilastik/ilastik/main?logo=appveyor
[appveyor-url]: https://ci.appveyor.com/project/ilastik/ilastik/branch/main
[codecov-img]: https://img.shields.io/codecov/c/github/ilastik/ilastik/main
[codecov-url]: https://codecov.io/gh/ilastik/ilastik/branch/main
[imagesc-img]: https://img.shields.io/badge/dynamic/json?color=informational&label=forum.image.sc&query=%24.topic_list.tags%5B0%5D.id&suffix=%20topics&url=https%3A%2F%2Fforum.image.sc%2Ftag%2Filastik.json
[imagesc-url]: https://forum.image.sc/tags/ilastik
[black-img]: https://img.shields.io/badge/code%20style-black-black
[black-url]: https://github.com/psf/black
[ilastik-logo]: https://www.ilastik.org/assets/ilastik-logo.png
[screenshot]: https://www.ilastik.org/assets/img/carousel/crop_training1.jpg
[download-page]: https://www.ilastik.org/download.html
[how-to-install]: https://www.ilastik.org/documentation/basics/installation.html
[documentation]: https://www.ilastik.org/documentation/index.html
[pixel-classification]: https://www.ilastik.org/documentation/pixelclassification/pixelclassification
[startup]: https://www.ilastik.org/documentation/basics/startup
[data-selection]: https://www.ilastik.org/documentation/basics/dataselection
[data-navigation]: https://www.ilastik.org/documentation/basics/navigation
[imagesc-search]: https://forum.image.sc/search
[issues]: https://github.com/ilastik/ilastik/issues
[edit-files-on-github]: https://docs.github.com/en/free-pro-team@latest/github/managing-files-in-a-repository/editing-files-in-another-users-repository
[mamba]: https://github.com/mamba-org/mamba
