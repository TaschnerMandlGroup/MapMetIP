from ilastik.experimental.api import from_project_file
import os
from xarray import DataArray
import numpy as np
import warnings
from glob import glob
from IMC_Denoise.IMC_Denoise.IMC_Denoise_main.DIMR import DIMR
import random
import tifffile as tiff

# import pickle
warnings.filterwarnings('ignore')

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class BackgroundCorrecter():
    
    def __init__(self, model_path):
        
        assert os.path.isdir(model_path)
        
        self.model_path = model_path
        
        self.models = [x for x in os.listdir(model_path) if "ilp" in x.lower()]
        
        logger.debug(f"model_path: {model_path}")
        logger.debug(f"models: {self.models}")
        
    
    def correct(self, clipped_stack, image_stack, channels, threshold=0.5, keep_channels=None):
        
        logger.debug(f"threshold: {threshold}")
        logger.debug(f"channels: {channels}")
        logger.debug(f"keep_channels: {keep_channels}")
        
        mask_stack, clip_stack, new_channels = [], [], []
        for channel, clipped_image, image in zip(channels, clipped_stack, image_stack):
            
            if channel in keep_channels:
                
                mask_stack.append(np.ones_like(image))
                clip_stack.append(clipped_image)
                new_channels.append(channel)
                continue

            model = [x for x in self.models if channel in x]
            
            if len(model)==0:
                logger.debug(f"Skipping {channel} no model found!")
                continue
            
            assert len(model)==1 
            
            model = model[0]
            logger.debug(f"channel_name: {channel}; used_model: {os.path.join(self.model_path, model)}")

            model = from_project_file(os.path.join(self.model_path, model))

            marker_image = DataArray(image, dims=("y", "x"))
            
            prediction = model.predict(marker_image)

            clip_stack.append(clipped_image)
            mask_stack.append(prediction[..., 0].to_numpy() > threshold)
            new_channels.append(channel)

        mask_stack = np.stack(mask_stack)
        return_stack = mask_stack * clip_stack
        
        logger.debug(f"final_stack: {return_stack.shape}")
        logger.debug(f"final_masks: {mask_stack.shape}")

        return return_stack, mask_stack, new_channels
