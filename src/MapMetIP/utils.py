import numpy as np
import torch
import GPUtil
import logging

class DEBUGGER():
    pass

def crop_image(image, px=2, axis=(0, 1)):
    
    assert image.ndim >= len(axis)
    
    slices = tuple(slice(px, -px) if a in axis else slice(None) for a in range(image.ndim))
        
    return image[slices]


def GPU(verbose=False):
    
    gpus = GPUtil.getGPUs()
    
    if len(gpus) == 0:
        return torch.device("cpu")
    
    max_free = 0
    for n, gpu in enumerate(gpus):

        if verbose:
            print(f"{round(gpu.memoryFree/1000, 2)} GB free on cuda:{n}")
        
        if gpu.memoryFree > max_free:
            idx = n
            max_free = gpu.memoryFree
            
    return torch.device(idx)

def float2uint8(inp):
    
    if np.issubdtype(inp.dtype, np.floating):
        return (inp*255).astype(np.uint8)
    elif inp.dtype == np.uint8:
        return inp
    else:
        raise Exception("wrong datatype")
    
def uint82float32(inp):
    
    if np.issubdtype(inp.dtype, np.integer):
        return (inp/255).astype(np.float32)
    elif inp.dtype == np.float32:
        return inp
    else:
        raise Exception("wrong datatype")
    
def alpha_blend(a, b):
    
    ret = np.zeros((*a.shape, 3))
    ret[..., 0] = uint82float32(a)
    ret[..., 1] = uint82float32(b)
    
    return ret


def color_by_value(seg, idx, colors) -> np.ndarray:
    
    cols = [colors[idx==i][0] if i in idx else 0 for i in range(idx.max()+1)]

    return np.array(cols)[seg]


def rand_col_seg(seg) -> np.ndarray:
    
    vals = np.unique(seg)
    colors = np.random.uniform(0.1, 1, (vals.max()+1, 3))
    colors[0] = [0, 0, 0]

    return colors[seg]


def setup_logger(sample_name, log_path):
    
    logging.root.handlers = []
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')    
    fh = logging.FileHandler(f'{log_path}/{sample_name}.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logging.root.addHandler(fh)