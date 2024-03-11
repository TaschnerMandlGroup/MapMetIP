from MapMetIP.sample import MapMetIP_Sample, save_sample
from MapMetIP.spillover import spillover_correction
from MapMetIP.segmentation import Segmenter
from MapMetIP.register import Registerer
from MapMetIP.normalize import percentile_clip
from MapMetIP.neighbors import extract_neighbors
import argparse
import os
from MapMetIP.utils import setup_logger
import logging
import numpy as np
import cv2
from MapMetIP.background_correction import BackgroundCorrecter
from tqdm import tqdm
from MapMetIP.normalize import minmax_sample
from MapMetIP.feature_extraction import FeatureExtractor, extract_sample_features, MORPH_MEASURES
from IMC_Denoise.IMC_Denoise.IMC_Denoise_main.DIMR import DIMR
import tifffile
import sys
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import json
from MapMetIP.utils import DEBUGGER

def parse():
    
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--sample_name", type=str, required=bool, help="Name of the sample to process.")
    parser.add_argument("--base", type=str, required=bool, help="Path to sample folder.")
    parser.add_argument("--spillover_folder", type=str, help="Path to spillover measurements. Will be skipped unless defined.")
    parser.add_argument("--docker_folder", type=str, help="Path to store temporary data during spillover compensation. Required for spillover compensation.")
    parser.add_argument("--registration_scale", default=1., type=float, help="Scale for SIFT-registration.")
    parser.add_argument("--segmentation_diameter", type=int, required=bool, help="Average diameter used in cellpose semgentation. ")
    parser.add_argument("--backgroundcorrection_folder", type=str, help="Path to ilastik background/foreground classifiers. Will be skipped unless defined.")
    parser.add_argument("--save_dir", type=str, required=bool, help="Path to write results.")
    parser.add_argument("--refine_threshold", type=float, required=bool, help="Threshold used for refinement of mask. Will be skipped, unless defined."),
    parser.add_argument("--segmentation_model", type=str, required=bool, help="Path to cellpose segmentation model."),
    parser.add_argument("--log_path", type=str, required=bool, help="Path to write log files.")
    parser.add_argument("--perform_dimr", default=True, help="Skip DIMR hot pixel removal.")
    
    
    for arg in vars(args):
        if getattr(args, arg) == 'none' or getattr(args, arg) == 'None':
            setattr(args, arg, None)

    print(args)

    return args 

if __name__ == "__main__":
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    debug_file = (os.path.join(script_dir, "debug_file.json")) #None
    
    if debug_file:
        with open(debug_file, 'rb') as fh:
            d = json.loads(fh.read())
            args = DEBUGGER()
            for k, v in d.items():
                setattr(args, k, v)
    else:
        args = parse()

    sample_name = args.sample_name
        
    setup_logger(args.sample_name, args.log_path)    
    
    sample_folder = os.path.join(args.base, args.sample_name)
    
    logger.debug(f"Computing sample: {args.sample_name} under {sample_folder}")
    
    sample = MapMetIP_Sample(sample_folder)

    sample.calculate_nuclear_image()

    segmenter = Segmenter(args.segmentation_model)    
    registerer = Registerer("SIFT")
    featureextractor = FeatureExtractor(additional_morphology_functions=MORPH_MEASURES)   

    all_pixelvalues = []
    for roi in sample.roi_nums:
        
        mod0 = sample.mod0[roi]
        mod1 = sample.mod1[roi]
        
        logger.debug(f"Registration for ROI {roi}")
        
        registerer.register(
            mov=mod0.image_stack[mod0.stack_channels == "IF1_DAPI"].squeeze(), 
            fix=mod1.nuclear_image.squeeze(), 
            preprocessing=True)
        
        if isinstance(registerer.h_mov2fix, type(None)):
            logger.warning(f"SKIPPING {roi} BECAUSE TRANSFORMATION MATRIX IS NONE")
            continue

        mod0_stack = registerer.warp(mod0.image_stack, mod1.nuclear_image.squeeze().shape, registerer.h_mov2fix)
        mod1_stack = mod1.image_stack

        if args.refine_threshold is not None:   

            logger.debug("Refining Masks")

            segmentation_masks, refined_segmentation_masks = segmenter.segment(
                mod0.image_stack[mod0.stack_channels == "IF1_DAPI"].squeeze(), 
                eval_kwargs={"diameter": args.segmentation_diameter},
                refine_threshold=args.refine_threshold)
        
            small_segmentation_masks = registerer.warp(segmentation_masks, mod1.nuclear_image.squeeze().shape, registerer.h_mov2fix, interpolation=cv2.INTER_NEAREST)
            small_refined_segmentation_masks = registerer.warp(refined_segmentation_masks, mod1.nuclear_image.squeeze().shape, registerer.h_mov2fix, interpolation=cv2.INTER_NEAREST)

            registration_mapping = np.ones_like(mod1.nuclear_image)
            large_mask = registerer.warp(registration_mapping, mod0.image_stack[mod0.stack_channels == "IF1_DAPI"].squeeze().shape, registerer.h_fix2mov)

            idxs = np.where(large_mask != 0)
            xmin, xmax = idxs[0].min(), idxs[0].max()
            ymin, ymax = idxs[1].min(), idxs[1].max()
            logger.debug(f"mapping idxs: {xmin}, {xmax}, {ymin}, {ymax}")
            
            large_segmentation_masks = segmentation_masks[xmin:xmax, ymin:ymax]
            large_refined_segmentation_masks = refined_segmentation_masks[xmin:xmax, ymin:ymax]
            
            sample.mod0[roi].image_stack = mod0_stack
            sample.mod1[roi].image_stack = mod1_stack
            
            sample.data[roi] = {
                "large_segmentation_masks": large_refined_segmentation_masks,
                "small_segmentation_masks": small_refined_segmentation_masks
            }
                
        else:
                        
            segmentation_masks = segmenter.segment(
                mod0.image_stack[mod0.stack_channels == "IF1_DAPI"].squeeze(), 
                eval_kwargs={"diameter": args.segmentation_diameter},
                refine_threshold=None)
        
            small_segmentation_masks = registerer.warp(segmentation_masks, mod1.nuclear_image.squeeze().shape, registerer.h_mov2fix, interpolation=cv2.INTER_NEAREST)

            registration_mapping = np.ones_like(mod1.nuclear_image)
            large_mask = registerer.warp(registration_mapping, mod0.image_stack[mod0.stack_channels == "IF1_DAPI"].squeeze().shape, registerer.h_fix2mov)

            idxs = np.where(large_mask != 0)
            xmin, xmax = idxs[0].min(), idxs[0].max()
            ymin, ymax = idxs[1].min(), idxs[1].max()
            
            logger.debug(f"mapping idxs: {xmin}, {xmax}, {ymin}, {ymax}")

            large_segmentation_masks = segmentation_masks[xmin:xmax, ymin:ymax]
        
            sample.mod0[roi].image_stack = mod0_stack
            sample.mod1[roi].image_stack = mod1_stack
        
            sample.data[roi] = {
                "small_segmentation_masks": small_segmentation_masks,
                "large_segmentation_masks": large_segmentation_masks,
            }
            
    
    to_delete = [k for k,v in sample.data.items() if "small_segmentation_masks" not in v]
    for key in to_delete:
        del sample.data[key]
    
    if args.spillover_folder is not None:
        sample = spillover_correction(sample, args.spillover_folder, args.docker_folder)
    
    for roi in sample.data.keys():
        
        all_stack = np.concatenate((sample.mod1[roi].image_stack, sample.mod0[roi].image_stack), axis=0)
        all_channels = np.concatenate((sample.mod1[roi].stack_channels, sample.mod0[roi].stack_channels))
        
        logger.debug(f"all_stack.shape: {all_stack.shape}")
        logger.debug(f"all_channels: {list(all_channels)}")

        all_pixelvalues.append(np.reshape(all_stack, (all_stack.shape[0], -1)))
        
        sample.data[roi]["all_stack"] = all_stack
        sample.data[roi]["all_channels"] = all_channels
        
    setattr(sample, "all_channels", all_channels)
    setattr(sample, "all_pixelvalues", np.concatenate(all_pixelvalues, axis=1))
        
    logger.debug(f"REMAINING KEYS: {list(sample.data.keys())}")
    
    if args.perform_dimr is not None:
    
        for roi, data in sample.data.items():
            
            logger.debug(f"Performing DIMR for roi {roi}")
            hrm_stack = []
            for image in data["all_stack"]:
                hrm_stack.append(DIMR(n_neighbours=4, n_iter=3, window_size=3).perform_DIMR(image))
            
            sample.data[roi]["all_stack"] = np.array(hrm_stack)
    
    else:
        logger.debug("Skipping DIMR!")
    
    sample = percentile_clip(sample)
    logger.debug("Clipped values")
    
    if args.backgroundcorrection_folder is not None:
    
        bc = BackgroundCorrecter(args.backgroundcorrection_folder)
        for roi, data in tqdm(sample.data.items()):
            corrected, masks, new_channels = bc.correct(data["clipped_stack"], data["all_stack"], channels=data["all_channels"], keep_channels=sample.KEEP_CHANNELS)
            sample.data[roi]["data_corrected"] = corrected
            sample.data[roi]["data_channels"] = new_channels
            
    else:
        
        logger.debug("Skipping background correction because backgroundcorrection_folder is None")
        for roi, _ in tqdm(sample.data.items()):
            sample.data[roi]["data_corrected"] = sample.data[roi]["clipped_stack"]
            sample.data[roi]["data_channels"] = sample.data[roi]["all_channels"]
    
    sample = minmax_sample(sample)
    
    sample = extract_sample_features(sample, featureextractor)
    
    sample = extract_neighbors(sample, dmax=150)

    save_sample(sample, args.save_dir)
    
    logger.debug("*"*10 + " FINISHED " + "*"*10)