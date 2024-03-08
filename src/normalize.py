from .sample import Sample
import numpy as np
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def normalize_per_sample(sample: Sample, percentage: float):
    
    stacks = []
    for _, v in sample.rois.items():
        
        stack = v.IMC.image_stack.transpose(2,0,1)
        
        stacks.append([x.flatten() for x in stack])
        
    stacks = np.concatenate(stacks, axis=1)
    channelwise_perc = np.percentile(stacks, percentage, axis=1)

    for _, v in sample.rois.items():
        
        stack = np.clip(np.stack([v.IMC.image_stack.transpose(2,0,1)[i]/channelwise_perc[i] for i in range(len(channelwise_perc))]), 0, 1)
        v.IMC.normed_stack = stack.transpose(1,2,0)
    

def normalize_per_sample_minmax(sample: Sample):
    
    stacks = []
    for _, v in sample.rois.items():
        
        stack = v.IMC.image_stack.transpose(2,0,1)
        
        stacks.append([x.flatten() for x in stack])
        
    stacks = np.concatenate(stacks, axis=1)
    channelwise_max = np.percentile(stacks, 100, axis=1)
    channelwise_min = np.percentile(stacks, 0, axis=1)

    for _, v in sample.rois.items():
        
        stack = np.clip(np.stack([(v.IMC.image_stack.transpose(2,0,1)[i]-channelwise_min[i])/(channelwise_max[i]-channelwise_min[i]) for i in range(len(channelwise_max))]), 0, 1)
        v.IMC.min_max_stack = stack.transpose(1,2,0)
    
    
    
def clip_sample(image_stack, clip_vals):
    
    ret_stack = []
    for im, clip_top in zip(image_stack, clip_vals):
    
        ret_stack.append(np.clip(im, 0, clip_top))
    
    logger.debug(f"clip_values: {clip_vals}")
    return np.array(ret_stack)

def normalize_sample_minmax(image_stack, min_vals, max_vals):
    
    ret_stack = []
    for i, (im, min_val, max_val) in enumerate(zip(image_stack, min_vals, max_vals)):
        
        if max_val != 0:
            
            ret_stack.append((im - min_val) / (max_val - min_val))

        else:
            
            logger.debug(f"stack with ID {i} has max value = 0; Concatenating without scaling")
            ret_stack.append(im)
        
    ret_stack = np.array(ret_stack)  
      
    new_mins = [x.min() for x in ret_stack]
    new_maxs = [x.max() for x in ret_stack]
    logger.debug(f"normalized_stack.shape: {ret_stack.shape}")
    logger.debug(f"mins after min_max scaling: {new_mins}")
    logger.debug(f"mins after min_max scaling: {new_maxs}")
    
    return ret_stack

def percentile_clip(sample):
    
    percentiles = [sample.PERCENTILE_LOOKUP[marker] for marker in sample.all_channels]
    logger.debug(f"sample.data_channels: {list(sample.all_channels)}")
    logger.debug(f"sample.PERCENTILE_LOOKUP: {sample.PERCENTILE_LOOKUP}")
    logger.debug(f"percentiles: {percentiles}")
 
    perc_values = [np.percentile(pv, perc) for pv, perc in zip(sample.all_pixelvalues, percentiles)]
    
    logger.debug(f"percentile_values: {perc_values}")
 
    assert not np.any(perc_values > sample.all_pixelvalues.max(axis=1)), "Error perc_values are higher than max, which cshould not happen"
 
    for roi, roi_data in sample.data.items():
        sample.data[roi]["clipped_stack"] = clip_sample(roi_data["all_stack"], perc_values)
        
    return sample


def minmax_sample(sample):
    
    sample_stack = []  
    for _, roi_data in sample.data.items():
        sample_stack.append(roi_data["data_corrected"])

    sample_stack = np.array(sample_stack).transpose(1,0,2,3)
    
    tmp_stack = sample_stack.reshape(sample_stack.shape[0], -1)
    
    logger.debug(f"sample_stack.shape: {sample_stack.shape}")
    logger.debug(f"tmp_stack.shape: {tmp_stack.shape}")
    
    min_vals, max_vals = tmp_stack.min(axis=1), tmp_stack.max(axis=1)
    
    logger.debug(f"min_vals, max_vals: {min_vals}, {max_vals}")

    for roi, roi_data in sample.data.items():
        sample.data[roi]["data_minmax"] = normalize_sample_minmax(roi_data["data_corrected"], min_vals, max_vals)
    
    return sample
        