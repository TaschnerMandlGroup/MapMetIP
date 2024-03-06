import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import polar
from .preprocess import preprocess
from .utils import float2uint8
import logging
from numpy import linalg

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Registerer():

    def __init__(self, type, *args, **kwargs) -> None:

        self.type = type.upper()

        if self.type == "SIFT":
            self.extractor = cv2.SIFT_create(*args, **kwargs)
            self.norm = cv2.NORM_L2

        else:
            raise ValueError(f"{type} is not a valid feature detection algorithm. Chose one of 'SIFT'")

        logger.debug(f"type: {self.type}")


    def register(self, fix, mov, preprocessing=True) -> None:
        
        self.h_mov2fix = None
        self.h_fix2mov = None
        
        if preprocessing:
            self.fix = preprocess(fix)
            self.mov = preprocess(mov)
            logger.debug("Preprocessing images before registration")
            
        else:
            self.fix = float2uint8(fix)
            self.mov = float2uint8(mov)
            logger.debug("Skipping preprocessing images before registration")


        self.kp_fix, self.des_fix = self.extractor.detectAndCompute(self.fix, None)
        self.kp_mov, self.des_mov = self.extractor.detectAndCompute(self.mov, None)
    
        self.match()
        self.estimate()
        
        logger.debug(f"len(self.des_fix): {len(self.des_fix)}")
        logger.debug(f"len(self.des_moving): {len(self.des_mov)}")        
        logger.debug(f"len(self.matches): {len(self.matches)}")
        
        if not isinstance(self.h_mov2fix, type(None)):
            logger.debug(f"self.h_mov2fix: {list(self.h_mov2fix.flatten())}")
            logger.debug(f"self.h_fix2mov: {list(self.h_fix2mov.flatten())}")
            
            
    def match(self, ratio_thresh=0.7) -> None:
        
        matcher = cv2.BFMatcher(self.norm) 
        
        des_fix = self.des_fix[:260000]
        des_mov = self.des_mov[:260000]
        
        knn_matches = matcher.knnMatch(des_fix, des_mov, 2)
        
        self.matches = [[m] for m, n in knn_matches if m.distance < ratio_thresh*n.distance]


    def estimate(self) -> None:
            
        self.points = np.round(np.array([np.array((self.kp_fix[m[0].queryIdx].pt, self.kp_mov[m[0].trainIdx].pt)) for m in self.matches]),0).astype(np.uint64)
        
        if self.points.size != 0:
            
            h_mov2fix, _ = cv2.estimateAffinePartial2D(self.points[:, 1], self.points[:, 0])
            h_fix2mov = np.linalg.inv(np.concatenate([h_mov2fix, np.array([[0, 0, 1]])], axis=0))[:2]
            self.h_mov2fix = h_mov2fix
            self.h_fix2mov = h_fix2mov
            
        else:
            logger.warning("NO MATCHES FOUND")
    
    @staticmethod
    def warp(src, sz, h, interpolation=cv2.INTER_NEAREST):
        
        if src.ndim == 2:
            
            src = np.expand_dims(src, 0)
            
        logger.debug(f"warping: src.shape {src.shape}; sz {sz}; transformation matrix {list(h.flatten())}; interpolation {interpolation}")
        
        return np.array([cv2.warpAffine(im, h, dsize=(sz[1], sz[0]), flags=interpolation) for im in src]).squeeze()
        
        
    