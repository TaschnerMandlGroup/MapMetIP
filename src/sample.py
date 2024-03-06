import os
import glob
from tifffile import imread, TiffFile
import exifread
import re
from pathlib import Path
from datetime import datetime
from readimc import MCDFile
from . import lookup
from .utils import crop_image
import numpy as np
import pandas as pd
import cv2
import tifffile
#from xtiff import to_tiff

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Sample():
    
    def __init__(self, dir_path, log=True):
        
        assert os.path.isdir(dir_path)
        
        self.dir_path = Path(dir_path)
        
        parts = self.dir_path.stem.split("_")
        
        if len(parts) == 5:
            
            self.sample_name = "_".join(parts[:-1])
            self.sample_info = parts[-1]

        else:
        
            self.sample_name = self.dir_path.stem
            
        self.date0, self.date1, self.sample_id, self.sample_type, = self.sample_name.split("_")
        self.date0 = datetime.strptime(self.date0, "%Y%m%d")
        self.date1 = datetime.strptime(self.date1, "%Y%m%d")
        self.sample_number = int(self.sample_id.split("-")[1])
        self.sample_year = 2000 + int(self.sample_id.split("-")[0])
        self.files = glob.glob(f"{self.dir_path}/*.*")
        
        logger.debug(f"dir_path: {self.dir_path}")
        logger.debug(f"date0: {self.date0}")
        logger.debug(f"date1: {self.date1}")
        logger.debug(f"sample_number: {self.sample_number}")
        logger.debug(f"sample_year: {self.sample_year}")
        logger.debug(f"files: {self.files}")
        
        self.data = {}
        
class ROI():
    
    pass

        
class MapMetIP_Sample(Sample):
    
    def __init__(self, dir_path):
    
        
        super().__init__(dir_path)
        
        self.LOOKUP_TABLE = getattr(lookup, f"LOOKUP_TABLE_{self.sample_type}")
        self.NUCLEAR_MARKER = getattr(lookup, f"NUCLEAR_MARKER_{self.sample_type}")
        self.PERCENTILE_LOOKUP = getattr(lookup, f"PERCENTILE_LOOKUP_{self.sample_type}")
        self.KEEP_CHANNELS = getattr(lookup, f"KEEP_CHANNELS_{self.sample_type}")

        logger.debug(f"self.LOOKUP_TABLE: LOOKUP_TABLE_{self.sample_type}")
        logger.debug(f"self.NUCLEAR_MARKER: NUCLEAR_MARKER_{self.sample_type}")
        logger.debug(f"self.PERCENTILE_LOOKUP: PERCENTILE_LOOKUP_{self.sample_type}")
        logger.debug(f"self.KEEP_CHANNELS: KEEP_CHANNELS_{self.sample_type}")
        
        self.tif_files = [x for x in self.files if ".tif" in x.lower()]
        self.mcd_files = [x for x in self.files if ".mcd" in x.lower()]
        
        assert len(self.mcd_files) == 1, "currently only one mcd file possible"
        
        self.mcd_files = self.mcd_files[0]
        
        self.mod0 = self.read_tif_rois()
        self.mod1 = self.read_IMC_rois()
        
        self.match_rois()
        
        logger.debug(f"tif_files: {self.tif_files}")
        logger.debug(f"mcd_files: {self.mcd_files}")
        logger.debug(f"self.mod0.keys(): {list(self.mod0.keys())}")
        logger.debug(f"self.mod1.keys(): {list(self.mod1.keys())}")
        
        for k, v in self.mod0.items():
            logger.debug(f"self.mod0.image_stack.shape: ROI: {k}, {v.image_stack.shape}")
            logger.debug(f"self.mod0.stack_channels: ROI: {k}, {list(v.stack_channels)}")
            
        for k, v in self.mod1.items():
            logger.debug(f"self.mod1.image_stack.shape: ROI: {k}, {v.image_stack.shape}")
            logger.debug(f"self.mod1.stack_channels: ROI: {k}, {list(v.stack_channels)}")

        del self.rois
        del self.info
        
    def match_rois(self):
    
        
        mod0_rois = set(self.mod0.keys())
        mod1_rois = set(self.mod1.keys())
        
        keep_rois = mod0_rois & mod1_rois
        
        self.mod0 = {k: self.mod0[k] for k in keep_rois}
        self.mod1 = {k: self.mod1[k] for k in keep_rois}
        
        self.roi_nums = keep_rois
        
        logger.debug(f"mod0 found rois: {mod0_rois}")
        logger.debug(f"mod1 found rois: {mod1_rois}")
        logger.debug(f"keep_rois: {keep_rois}")
        
        
    def read_tif_rois(self):

    
        self.rois = {}
        self.info = []
        for file in self.tif_files:
            
            with open(file, 'rb') as f:
                tags = exifread.process_file(f)
             
            print(str(tags["Image Tag 0xB0B7"]))
            try:
                roi_num = int(re.findall("(?<=[rR][oO][iI]_)[0-9]+", str(tags["Image Tag 0xB0B7"]))[0])
            except:
                roi_num = int(re.findall("(?<=[rR][oO][iI])[0-9]+", str(tags["Image Tag 0xB0B7"]))[0])
                
            print(file)
            channel = re.findall("(?<=_)[A-Z]\.", file)[0][0]
            
            logger.debug(f"filename - channel - roi: {file} - {channel}- {roi_num}")
            
            self.info.append([roi_num, channel, file])
            
        self.info = pd.DataFrame(self.info, columns=["roi", "channel", "filename"])
        
        for roi in np.unique(self.info.roi):
            
            tmp = self.info[self.info.roi == roi]
            self.add_roi(tmp)
            
        return self.rois
            
    def add_roi(self, roi_df):
        
        roi_df = roi_df.sort_values("channel")
        
        image_stack = np.stack([imread(row.filename) for _, row in roi_df.iterrows()], axis=-1).transpose(2,0,1)
        channels = np.array([self.LOOKUP_TABLE[row.channel] for _, row in roi_df.iterrows()])
        
        self.rois[list(roi_df.roi)[0]] = ROI()
        
        setattr(self.rois[list(roi_df.roi)[0]], "image_stack", image_stack)
        setattr(self.rois[list(roi_df.roi)[0]], "stack_channels", channels)
            
            
    def read_IMC_rois(self):
    
        
        self.rois = {}
        with MCDFile(self.mcd_files) as f:

            for acq in f.slides[0].acquisitions:
                try:
                    img = f.read_acquisition(acq)
                    if img.shape[1] != 700 or img.shape[2] != 700:
                        roi_num = int(re.findall("[0-9]+", acq.description)[0])
                        logger.debug(f"Found image with size different than 700x700: {img.shape}, roi_num: {roi_num}")
                        continue
                except:
                    continue
            
                roi_num = int(re.findall("[0-9]+", acq.description)[0])
                channels = np.array(acq.channel_labels)
                
                self.rois[roi_num] = ROI()
                
                img = crop_image(img, px=2, axis=(1,2))
                
                setattr(self.rois[roi_num], "image_stack", img)
                setattr(self.rois[roi_num], "stack_channels", np.array([self.LOOKUP_TABLE[c] for c in channels]))

        return self.rois

    def calculate_nuclear_image(self):
        
        for roi in self.mod1.keys():
            
            logger.debug(f"self.NUCLEAR_MARKER: {self.NUCLEAR_MARKER}")
            
            nuclear_image = np.expand_dims(np.mean(self.mod1[roi].image_stack[np.array([c in self.NUCLEAR_MARKER for c in self.mod1[roi].stack_channels])], axis=0), 0)
            setattr(self.mod1[roi], "nuclear_image", nuclear_image)
            
            logger.debug(f"self.mod1[{roi}].nuclear_image.shape: {self.mod1[roi].nuclear_image.shape}")
            
 
def ensure_dir(file_path):
    """Ensure that the directory exists for the given file path."""
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
            
def save_sample(sample, out_dir):

    for k,v in sample.data.items():
        
        logger.debug("-"*10)
        
        roi_num = k
        
        print(k, v.keys())
        img = v["data_minmax"]
        img_vis = img[np.array(v["data_channels"])=="IF1_DAPI"].squeeze()
        intensities_0px = v["intensiy_features_0"]
        intensities_1px = v["intensiy_features_1"]
        regionprops = v["morphological_features"]
        masks_vis = v["small_segmentation_masks"]
        large_masks = v["large_segmentation_masks"]
        channel_names = v["data_channels"]
        
        masks = np.expand_dims(masks_vis, (0, 1, 2, 5))

        folders = ["large_segmentation_masks", "intensities-0px", "intensities-1px", "regionprops", "img", "img-vis", "masks", "masks-vis"]
        file_types = ['.tif', '.csv', '.csv', '.csv', '.tif', '.tif', '.tif', '.tif']
        data_to_save = [large_masks, intensities_0px, intensities_1px, regionprops, img, img_vis, masks, masks_vis]
        save_functions = [tifffile.imwrite, 'to_csv', 'to_csv', 'to_csv', to_tiff, tifffile.imwrite, tifffile.imwrite, tifffile.imwrite]

        for folder, file_type, data, save_function in zip(folders, file_types, data_to_save, save_functions):
            save_path = os.path.join(out_dir, folder, f"{sample.sample_name}_{roi_num:0>{3}}{file_type}")
            ensure_dir(save_path)
            if save_function == 'to_csv':
                data.to_csv(save_path)
            elif save_function == to_tiff:
                save_function(data, save_path, image_name=f"{sample.sample_name}_{roi_num:0>{3}}{file_type}", channel_names=channel_names, pixel_size=1.0, pixel_depth=1.0)
            else:
                save_function(save_path, data)
            logger.debug(f"Saved {folder} under: {save_path}")