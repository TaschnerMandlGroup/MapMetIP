from cellpose import models 
import os
import torch
import cv2
import numpy as np
from .utils import GPU
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Segmenter():
    
    def __init__(self, model):
        
        self.model = model
        
        if not os.path.isfile(self.model): 
            
            raise Exception(f"Model {self.model} does not exist!")
            
        logger.debug(f"model_type: {self.model}")
        
        self.model = models.CellposeModel(model_type=self.model, gpu=torch.cuda.is_available(), device=GPU() if torch.cuda.is_available() else None)

        logger.debug(f"model: {self.model}")

    def segment(self, nuclear_image, eval_kwargs, refine_threshold=0.12):
        
        logger.debug(f"eval_kwargs: {eval_kwargs}")
        logger.debug(f"refine_threshold: {refine_threshold}")
        
        masks, _, _ = self.model.eval(nuclear_image, **eval_kwargs)
        
        logger.debug(f"nuclear_image.shape: {nuclear_image.shape}")
        logger.debug(f"detected masks: {masks.max()}")
              
        if not isinstance(refine_threshold, type(None)):
        
            # give it a threshold that is going to be used for thresholding t = 0.12
            refined = refine_masks(nuclear_image, masks, t=refine_threshold)
        
            return masks, refined
        
        else:
        
            return masks


def refine_masks(image, masks, t=0.12):
    
    image = image.copy()/image.max()
    binary_masks = masks.astype(bool)
    binary_masks[image < t] = 0
    
    # blurring to remove rough edges: cv2.GaussianBlur(patch0, ksize=(5,5), sigmaX=1.5, sigmaY=1.5)
    binary_masks = cv2.GaussianBlur(binary_masks.astype(np.uint8), ksize=(5,5), sigmaX=1.5, sigmaY=1.5).astype(bool)
    refined_masks = binary_masks*masks
    
    return refined_masks