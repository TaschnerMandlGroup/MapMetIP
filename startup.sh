#!/bin/bash
echo "test"
echo "Setting up your docker container."
cd /usr/src/app/MapMetIP

echo "Acivating conda environment."
source activate mapmet_ip

echo "Installing MapMetIP in editable mode."
pip install -e .

echo "Downloading data and models from Zenodo and storing it in /data/raw and /data/models. Assuming /data is the mounted volume directory"
wget -P /data https://sandbox.zenodo.org/record/34280/files/MapMetIP_models.zip
unzip /data/MapMetIP_models.zip -d /data

wget -P /data https://sandbox.zenodo.org/records/34280/files/MapMetIP_TestDataset.zip
unzip /data/MapMetIP_TestDataset.zip -d /data

echo "Creating log_files and results directories within /data"
mkdir -p /data/log_files
mkdir -p /data/results

echo "Starting jupyter notebook"
#Notebook authentication disabled - adapt later - https://jupyter-notebook.readthedocs.io/en/6.2.0/security.html
jupyter lab notebook --notebook-dir=/usr/src/app/MapMetIP --ip='0.0.0.0' --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''

# Keep the container running after startup tasks are complete
exec "$@"

