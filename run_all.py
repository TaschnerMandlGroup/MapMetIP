import logging
import os
import subprocess
import datetime
import sys
import argparse

def setup_logger(path):
    now = datetime.datetime.now()
    logger = logging.getLogger(__name__)
    fh = logging.FileHandler(f"{path}/RUN_{now.year}{now.month:0>{2}}{now.day:0>{2}}_{now.hour:0>{2}}{now.minute:0>{2}}{now.second:0>{2}}.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')    
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)
    
    return logger

def parse():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sample_list", nargs='+', required=bool, help="Define samples to process.")
    parser.add_argument("--data_path", type=str, required=bool, help="Path to the folder with downloaded raw_data.")
    parser.add_argument("--model_path", type=str, required=bool, help="Path to the folder with downloaded models/classifiers.")
    parser.add_argument("--save_dir", type=str, required=bool, help="Path to write results. Will be overwritten in consecutive runs.")
    parser.add_argument("--log_path", type=str, required=bool, help="Path to write logs. Will be overwritten in consecutive runs.")
    args = parser.parse_args()
    
    return args

if __name__ == "__main__":
    
    args = parse()
    samples = args.sample_list
    base = args.data_path
    save_dir = args.save_dir
    log_path = args.log_path

    spillover_folder = os.path.join(args.model_path, "spillover")
    docker_folder = os.path.join(spillover_folder, "out")
    
    logger = setup_logger(args.log_path)
    
    for sample in samples:
        
        now = datetime.datetime.now()
        
        logger.debug(f"{sample}")
        
        if "BM" in sample:

            segmentation_diameter = 55
            backgroundcorrection_folder = os.path.join(args.model_path, "BM/BC_classifiers")
            segmentation_model = os.path.join(args.model_path, "BM/segmentation_model/CP_BM")
            refine_threshold = 0.12
            

        elif "TU" in sample:
            
            segmentation_diameter = 31
            backgroundcorrection_folder = os.path.join(args.model_path, "TU/BC_classifiers")
            segmentation_model = os.path.join(args.model_path, "TU/segmentation_model/CP_TU")
            refine_threshold = None


        try:
            script_path = os.path.abspath(__file__)
            script_dir = os.path.dirname(script_path)

            return_value = subprocess.call(f"cd {script_dir}; python3 main.py -s {sample} \
                                            --base {base} \
                                            --segmentation_diameter {segmentation_diameter} \
                                            --docker_folder {docker_folder} \
                                            --spillover_folder {spillover_folder} \
                                            --backgroundcorrection_folder {backgroundcorrection_folder} \
                                            --segmentation_model {segmentation_model} \
                                            --refine_threshold {refine_threshold} \
                                            --log_path {log_path}\
                                            --save_dir {save_dir}", shell=True)
            
            if return_value != 0:
                logger.error(f"{sample} HAD ERROR DURING COMPUTATION CHECK LOGFILE")
            
            else:
                logger.debug(f"{sample} IS FINE")

        except KeyboardInterrupt:
            
            sys.exit()
            
        