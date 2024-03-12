import tifffile 
import os 
import subprocess
from tqdm import tqdm
from glob import glob
import logging
import numpy as np
import sys
import docker

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def spillover_correction(sample, spillover_matrix_path, out, roi=None):
    
    files_before = os.listdir(out)

    files_created = []

    if roi is not None: 
        rois = [roi]
    else:
        rois=list(sample.mod0.keys())

    for k in tqdm(rois):
        
        files_created.append(f"{sample.sample_name}_{k}.tiff")
        files_created.append(f"{sample.sample_name}_{k}.csv")
            
        tifffile.imwrite(
            os.path.join(f"{out}/{sample.sample_name}_{k}.tiff"),
            data=sample.mod1[k].image_stack
        )

        with open(f"{out}/{sample.sample_name}_{k}.csv", "w+") as fout:
            fout.write(",".join([l.split("_")[-1] for l in sample.mod1[k].stack_channels]) + "\n")
            
    logger.debug(f"files_before: {files_before}")
    logger.debug(f"files_created: {files_created}")
    
    client = docker.from_env()
    try:
        
        container = client.containers.run("lazdaria/spillovercomp", "Rscript /home/generate_spillovermatrix.R", volumes={out: {'bind': '/home/tmp', 'mode': 'rw'}, spillover_matrix_path: {'bind': '/home/SPILLOVER', 'mode': 'rw'}}, stdout=True, stderr=True, remove=True)
        result = container.wait()
        res0 = result['StatusCode']

        if res0 == 0:
            logger.debug(f"Successfull generate_spillovermatrix.R: {res0}")
            logger.debug(f"result generate_spillovermatrix.R Exit Code {res0}")
        
        else:
            logger.warning(f"Error in generate_spillovermatrix.R with Exit Code:{res0}")

        container = client.containers.run("lazdaria/spillovercomp", "Rscript /home/spillover_compensation.R", volumes={out: {'bind': '/home/tmp', 'mode': 'rw'}, spillover_matrix_path: {'bind': '/home/SPILLOVER', 'mode': 'rw'}}, stdout=True, stderr=True, remove=True)
        result = container.wait()
        res1 = result['StatusCode']

        if res1 == 0:
            logger.debug(f"Successfull spillover_compensation.R")
            logger.debug(f"result spillover_compensation.R Exit Code {res1}")

        else:
            logger.warning(f"Error in spillover_compensation.R with Exit Code:{res1}")
            
    except:
        
        cleanup(out, files_before, sample, log_message="ERROR")


    cleanup(out, files_before, sample)
        
    return sample


def cleanup(out, files_before, sample, log_message=None):
    
    files_after = os.listdir(out) 
    new_files = set(files_after) - set(files_before) 
    
    if log_message:
        
        logger.error(f"{log_message} SPILLOVER ABORTED {log_message}")
        logger.debug(f"{log_message} STARTING CLEANUP {log_message}")
        
        for file in new_files:
            logger.debug(f"removing: {file}")
            os.remove(os.path.join(out, file))
            
        sys.exit()
        
        
    logger.debug(f"files_after: {files_after}")    
    logger.debug(f"new_files: {new_files}")  
    
    SOC_files = [x for x in new_files if "SOC" in x and sample.sample_name in x]

    for soc in SOC_files:
        
        roi = int(soc.split("_")[-2])
        image_stack = tifffile.imread(os.path.join(out, soc))
        
        logger.debug(f"SOC file for ROI{roi} read: {soc}")
        
        sample.mod1[roi].image_stack = image_stack.astype(np.float32)


    for file in new_files:
        
        logger.debug(f"removing: {file}")
        os.remove(os.path.join(out, file))