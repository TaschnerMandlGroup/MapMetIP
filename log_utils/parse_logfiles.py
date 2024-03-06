import re
import pathlib
import numpy as np

def parse_runall_logfile(path):
    
    with open(path, "r") as fin:
        
        lines = fin.readlines()

    lines = lines[1::2]

    errors = [re.findall("[0-9]+_[0-9]+_[0-9]+-[0-9]+_.{2}", line)[0] for line in lines if "error" in line.lower()]

    print(f"{len(lines)} analysed")
    print(f"{len(errors)} errors in samples {errors}")        
    

def parse_sample_logfile(path):
    
    expected_scale = 4096/700
    
    sample = pathlib.Path(path).stem
    
    with open(path, "r") as fin:
        
        lines = fin.readlines()
        
    if not "FINISHED" in lines[-1]:
        print(f"{sample} did not finish!")
    
    sample_ids = []
    roi_dict = {}
    for line in lines:
        
        if "Registration for ROI" in line:
            
            roi_num = int(re.findall("(?<=Registration for ROI).+", line)[0])
            
        if "keep_rois" in line:
            
            idx = re.findall("(?<={).+(?=})", line)[0].split(",")
            if len(idx) == 0:
                print("No common rois!")
        
        if "self.h_fix2mov" in line: 
            
            vals = np.array([float(x) for x in re.findall("(?<=\[).+(?=\])", line)[0].split(",")]).reshape(2,3)
            scales = get_scale(vals)
            if np.any(np.logical_or(scales < 0.95*expected_scale, scales > 1.05*expected_scale)):
                print(f"{sample} ROI {roi_num} has wrong scale: {scales}")
                sample_ids.append(f"{sample}")
                
        if "warning" in line.lower() and not "exifread" in line.lower():
            
            warning_message = re.findall("(?<=WARNING - ).+", line)[0]
            
            roi_dict[roi_num] = warning_message
            
            sample_ids.append(sample)
        
    for k, v in roi_dict.items():
        print(f"{sample} ROI {k} {v}")
        
    return np.unique(sample_ids)  

    
from scipy.linalg import polar
def get_scale(h):
    
    h = np.concatenate((h, np.array([[0,0,1]])))
    
    #extract transformation
    T = np.eye(3)
    T[:,2] = h[:, 2]

    L = h.copy()
    L[:2,2] = 0

    #checken ob T@L unsere original matrix ergeben
    assert np.allclose(h, T @ L)

    R, K = polar(L)
    
    if np.linalg.det(R) < 0:
        R[:3,:3] = -R[:3,:3]
        K[:3,:3] = -K[:3,:3]
        
    assert np.allclose(L, R @ K)
    assert np.allclose(h, T @ R @ K)

    f, X = np.linalg.eig(K)

    #extract scales
    S = []
    for factor, axis in zip(f, X.T):
        if not np.isclose(factor, 1):
            scale = np.eye(3) + np.outer(axis, axis) * (factor-1)
            S.append(scale)
            
    assert np.allclose(K, S[0] @ S[1])
    assert np.allclose(h, T @ R @ S[0] @ S[1])

    ret = []
    for s in S:
        ret.append(s[np.logical_and(s!=1, s!=0)])
        
    return np.array(ret).squeeze()