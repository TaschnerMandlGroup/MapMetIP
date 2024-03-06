import numpy as np
from tqdm import tqdm

def mean_intensity(I, masks, channel_names=None):
    
    if I.ndim == 2:
        np.expand_dims(I, 0)
    
    labels = []
    vals = []
    
    for c in tqdm(np.unique(masks)):
        
        if c != 0:
            
            labels.append(c)
            vals.append(I[:, masks==c].mean(axis=1))          
        
    labels = np.array(labels)
    vals = np.array(vals).T
    
    results = {"Object": labels}
    
    for n, val in enumerate(vals):
        
        if isinstance(channel_names, (list, tuple, np.ndarray)):
            results[f"{channel_names[n]}" + "_mean"] = val
            
        else:
            results[f"{n}" + "_mean"] = val
    
    return results


def mean_80_intensity(I, masks, channel_names=None):
    
    if I.ndim == 2:
        np.expand_dims(I, 0)
    
    labels = []
    vals = []
    
    for c in tqdm(np.unique(masks)):
        
        if c != 0:
            
            labels.append(c)

            intensity_values = np.sort(I[:, masks==c])
            top80 = int(0.8*intensity_values.shape[1])
            vals.append(intensity_values[:, top80:].mean(axis=1))
        
    labels = np.array(labels)
    vals = np.array(vals).T
    
    results = {"Object": labels}
    
    for n, val in enumerate(vals):
        
        if isinstance(channel_names, (list, tuple, np.ndarray)):
            results[f"{channel_names[n]}"  + "_mean-80"] = val
            
        else:
            results[f"{n}" + "_mean-80"] = val
    
    return results