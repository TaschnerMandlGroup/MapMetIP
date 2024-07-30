import os
import h5py
import argparse
from readimc import MCDFile
import re
import numpy as np
import exifread
from tifffile import imread
import pandas as pd

def parse():
    
    parser = argparse.ArgumentParser()

    parser.add_argument("--source_folder", type=str, required=bool, help="Path to data to compress.")
    parser.add_argument("--out_file", type=str, required=bool, help="Output h5file.")
    parser.add_argument("--level", type=int, required=bool, help="Compression level.")
    args = parser.parse_args()

    return args 

def read_IMC_rois(mcd_file):

    rois = {}
    with MCDFile(mcd_file) as f:

        for acq in f.slides[0].acquisitions:
            try:
                img = f.read_acquisition(acq)
            except:
                continue

            roi_num = int(re.findall("[0-9]+", acq.description)[0])
            channels = np.array(acq.channel_labels)
            
            rois[roi_num] = {
                    "image": img,
                    "channels": channels
                }

    return rois

def read_IF_rois(tif_files):
        
    rois = {}
    info = []
    for file in tif_files:
        
        with open(file, 'rb') as f:
            tags = exifread.process_file(f)
        try:
            roi_num = int(re.findall("(?<=[rR][oO][iI]_)[0-9]+", str(tags["Image Tag 0xB0B7"]))[0])
        except:
            roi_num = int(re.findall("(?<=[rR][oO][iI])[0-9]+", str(tags["Image Tag 0xB0B7"]))[0])

        channel = re.findall("(?<=_)[A-Z]\.", file)[0][0]
        info.append([roi_num, channel, file])
        
    info = pd.DataFrame(info, columns=["roi", "channel", "filename"])
    
    for roi in np.unique(info.roi):
    
        tmp = info[info.roi == roi]
        tmp = tmp.sort_values("channel")
        image_stack = np.stack([imread(row.filename) for _, row in tmp.iterrows()], axis=-1).transpose(2,0,1)
        channels = np.array([row.channel for _, row in tmp.iterrows()])
    
        rois[roi] = {
                "image": image_stack,
                "channels": channels
            }
        
    return rois

def compress_rois_to_h5(modality_group, roi_list, l):
    for key, value in roi_list.items():
        roi = modality_group.create_group(str(key))
        roi.attrs['channel_names'] = value['channels'].astype(str).tolist()
        roi.create_dataset('image', data=value['image'], compression='gzip', compression_opts=l)

    return modality_group

def compress_folder_to_h5(out, root, files, level):
    with h5py.File(os.path.join(out, (os.path.basename(root)) + '.h5'), 'w') as h5file:

        mcd_files = [os.path.join(root, file) for file in files if file.endswith('.mcd')]
        tif_files = [os.path.join(root, file) for file in files if file.endswith('.TIF')]

        # Create subgroup for IF and a sub-subgroup for each ROI and fill with compressed data
        rois = read_IF_rois(tif_files)
        IF = h5file.create_group('IF')
        IF = compress_rois_to_h5(IF, rois, level)

        # Create subgroup for IMC and a sub-subgroup for each ROI and fill with compressed data
        rois = read_IMC_rois(mcd_files[0])
        IMC = h5file.create_group('IMC')
        IMC = compress_rois_to_h5(IMC, rois, level)
        x=0

def compress_all_folders(source, out, lev):
    for root, _, files in os.walk(source):
        # Skip first iteration where root = path
        if not files and root == source:
            continue 

        compress_folder_to_h5(out, root, files, lev)

# source_folder = '/home/daria_l/isilon_images_mnt/10_MetaSystems/MetaSystemsData/Multimodal_Imaging_Daria/Publication/compression_test'  # Change to your source folder path
# output_h5_file = '/home/daria_l/isilon_images_mnt/10_MetaSystems/MetaSystemsData/Multimodal_Imaging_Daria/Publication/compression_out'    # Change to your desired output file
# compression_level = 6  # Set your desired compression level (0-9)

# compress_all_folders(source_folder, output_h5_file, compression_level)

if __name__ == "__main__":
    args = parse()
    compress_all_folders(args.source_folder, args.out_file, args.level)