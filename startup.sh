#!/bin/bash
echo "test"
echo "Setting up your docker container."
cd /usr/src/app/MapMetIP

echo "Acivating conda environment."
source activate mapmet_ip

echo "Installing MapMetIP in editable mode."
pip install -e .

echo "Creating log_files and results directories within /data"
mkdir -p /data/log_files
mkdir -p /data/results

echo "Starting jupyter notebook"
#Notebook authentication disabled - adapt later - https://jupyter-notebook.readthedocs.io/en/6.2.0/security.html
#jupyter lab --notebook-dir=/usr/src/app/MapMetIP --ip='0.0.0.0' --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''
jupyter lab --notebook-dir=/usr/src/app/MapMetIP --ip='0.0.0.0' --port=8888 --no-browser --allow-root

# Keep the container running after startup tasks are complete
exec "$@"

