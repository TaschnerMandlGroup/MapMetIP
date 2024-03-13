# Use Miniconda base image
FROM continuumio/miniconda3

# Install necessary packages
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 git wget unzip -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /usr/src/app

# Clone the external repository into the parent directory
RUN git clone --branch v1.0.0 https://github.com/PENGLU-WashU/IMC_Denoise.git
ENV PYTHONPATH="${PYTHONPATH}:/usr/src/app"

# Update Conda
RUN conda update -n base -c defaults conda

# Create the environment from the env.yml file
COPY env.yml /usr/src/app/env.yml
RUN conda env create -f env.yml

RUN conda install -n mapmet_ip -c conda-forge jupyterlab=3 "ipykernel>=6" xeus-python
ENV SHELL=/bin/bash

# Copy the startup script into the container
COPY startup.sh /usr/src/app/startup.sh

# Make the startup script executable
RUN chmod +x /usr/src/app/startup.sh

#Inform Docker that container listens on port 8888 at runtime
EXPOSE 8888

# Set the entry point to run the startup script
ENTRYPOINT ["/usr/src/app/startup.sh"]

# Open interactive bash shell upon startup
CMD ["/bin/bash"]