import logging
import os
import subprocess
import datetime
import sys
import argparse

def setup_logger():
    now = datetime.datetime.now()
    logger = logging.getLogger(__name__)
    fh = logging.FileHandler(f"/data_isilon_main/isilon_images/10_MetaSystems/MetaSystemsData/Multimodal_Imaging_Daria/MapMetIP/RUN_ALL/RUN_{now.year}{now.month:0>{2}}{now.day:0>{2}}_{now.hour:0>{2}}{now.minute:0>{2}}{now.second:0>{2}}.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')    
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)
    
    return logger

def parse():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sample_list", nargs='+')
    args = parser.parse_args()
    
    return args


if __name__ == "__main__":
    
    args = parse()
    samples = args.sample_list
    
    logger = setup_logger()
    
    for sample in samples:
        
        now = datetime.datetime.now()
        
        logger.debug(f"{sample}")
        
        if "BM" in sample:

            segmentation_diameter = 55
            backgroundcorrection_folder = "/data_isilon_main/isilon_images/10_MetaSystems/MetaSystemsData/Multimodal_Imaging_Daria/MapMetIP/ILP_NEW_BM/"
            segmentation_model = "/data_isilon_main/isilon_images/10_MetaSystems/MetaSystemsData/Multimodal_Imaging_Daria/MapMetIP/.cellpose_model/CP_BM"
            refine_threshold = 0.12
            registration_scale = 1
            log_path = "/data_isilon_main/isilon_images/10_MetaSystems/MetaSystemsData/Multimodal_Imaging_Daria/MapMetIP/test_logs"
            save_dir = "/data_isilon_main/isilon_images/10_MetaSystems/MetaSystemsData/Multimodal_Imaging_Daria/MapMetIP/TEST_RESULTS/"
            

        elif "TU" in sample:
            
            segmentation_diameter = 31
            backgroundcorrection_folder = "/data_isilon_main/isilon_images/10_MetaSystems/MetaSystemsData/Multimodal_Imaging_Daria/MapMetIP/ILP_NEW_TU/"
            segmentation_model = "/data_isilon_main/isilon_images/10_MetaSystems/MetaSystemsData/Multimodal_Imaging_Daria/MapMetIP/.cellpose_model/CP_TU"
            refine_threshold = "None"
            registration_scale = 1
            log_path = "/data_isilon_main/isilon_images/10_MetaSystems/MetaSystemsData/Multimodal_Imaging_Daria/MapMetIP/test_logs"
            save_dir = "/data_isilon_main/isilon_images/10_MetaSystems/MetaSystemsData/Multimodal_Imaging_Daria/MapMetIP/TEST_RESULTS/"

        try:
            
            return_value = subprocess.call(f"cd ~/src/MapMetIP; python3 main.py -s {sample} \
                                            --segmentation_diameter {segmentation_diameter} \
                                            --backgroundcorrection_folder {backgroundcorrection_folder} \
                                            --segmentation_model {segmentation_model} \
                                            --refine_threshold {refine_threshold} \
                                            --registration_scale {registration_scale} \
                                            --log_path {log_path}\
                                            --save_dir {save_dir}", shell=True)
            
            if return_value != 0:
                logger.error(f"{sample} HAD ERROR DURING COMPUTATION CHECK LOGFILE")
            
            else:
                logger.debug(f"{sample} IS FINE")

        except KeyboardInterrupt:
            
            sys.exit()
            
        