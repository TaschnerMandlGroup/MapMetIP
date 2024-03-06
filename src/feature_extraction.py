from skimage.measure import regionprops_table
from skimage.segmentation import expand_labels
from .intensity_functions import mean_80_intensity, mean_intensity
import pandas as pd
from .morphology_functions import *
import logging
import cv2

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

PROPERTIES = ["label", "area", "area_convex", "area_filled", "axis_major_length", "axis_minor_length", "eccentricity", "equivalent_diameter_area", "perimeter", "solidity", "centroid"]

MORPH_MEASURES = [assymetry, concavity, fill, aspect_ratio, perimeter_ratio]
     
class FeatureExtractor():
    
    def __init__(self, additional_morphology_functions=[]):
        
        self.additional_morphology_functions = additional_morphology_functions
        
       
       
    def extract(self, mask, intensity_images, channel_names=None):
        
        logger.debug(f"channel_names: {channel_names}")
        
        morph_features = self.extract_morphology(mask)
        intensity_features = self.extract_intensity(mask, intensity_images, channel_names)
        
        return morph_features, intensity_features
   
    def extract_morphology(self, mask):
        
        logger.debug(f"PROPERTIES: {PROPERTIES}")
        logger.debug(f"additional_morphology_functions: {self.additional_morphology_functions}")
        
        morph_features = regionprops_table(mask, properties=PROPERTIES, extra_properties=self.additional_morphology_functions)
        morph_features = pd.DataFrame(morph_features)
        morph_features = morph_features.rename(columns={"label": "Object"})
        morph_features = morph_features.set_index("Object")
        
        logger.debug(f"morph_features.shape: {morph_features.shape}")

        return morph_features
    
    def extract_intensity(self, mask, intensity_images, channel_names, expand_pixels=1):
        
        tmp_mask = expand_labels(mask, expand_pixels)
           
        mean = self.get_intensity(I=intensity_images, masks=tmp_mask, intensity_function=mean_intensity, channel_names=channel_names)
        mean_80 = self.get_intensity(I=intensity_images, masks=tmp_mask, intensity_function=mean_80_intensity, channel_names=channel_names)
        
        intensity_features = pd.concat([mean, mean_80], axis=1)
        
        logger.debug(f"dilation of masks: {expand_pixels} pixels")
        logger.debug(f"intensity_features.shape: {intensity_features.shape}")
        
        return intensity_features

        
    def get_intensity(self, I, masks, intensity_function, channel_names):
        
        results = intensity_function(I, masks, channel_names=channel_names)

        results = pd.DataFrame(results)
        results = results.set_index("Object")
                
        return results


def extract_sample_features(sample, Extractor):
      
    for roi, roi_data in sample.data.items():
        
        stack = roi_data["data_minmax"]
        
        morph_features = Extractor.extract_morphology(roi_data["large_segmentation_masks"])
        intensity_features_0 = Extractor.extract_intensity(roi_data["small_segmentation_masks"], stack, roi_data["data_channels"], expand_pixels=0)
        intensity_features_1 = Extractor.extract_intensity(roi_data["small_segmentation_masks"], stack, roi_data["data_channels"], expand_pixels=1)
        
        if np.any(np.isnan(intensity_features_0)):
            logger.warning("NaN values in intensity_features_0")
        if np.any(np.isnan(intensity_features_1)):
            logger.warning("NaN values in intensity_features_1")
        if np.any(np.isnan(morph_features)):
            logger.warning("NaN values in morph_features")

        sample.data[roi]["intensiy_features_0"] = intensity_features_0
        sample.data[roi]["intensiy_features_1"] = intensity_features_1
        sample.data[roi]["morphological_features"] = morph_features

    return sample
