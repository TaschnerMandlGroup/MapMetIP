import os
import re
import shutil
from glob import glob
from tqdm import tqdm

def copy_sample(base, sample_name, out_dir):
    
    all_files = os.listdir(os.path.join(base, sample_name))
    
    file_list = []
    for root, dirs, files in os.walk(os.path.join(base, sample_name)):
        for name in files:
            if "tif" in name.lower() and "spot" in root.lower() and "spot" in name.lower() or "mcd" in name.lower() :
                file_list.append([os.path.join(root, name), name])

    new_sample_name = [re.findall(".+[0-9]+_[0-9]+_[0-9]+-[0-9]+.+", f) for f in all_files]
    new_sample_name = [x for x in new_sample_name if len(x) != 0][0][0]
    
    if not os.path.exists(os.path.join(out_dir, new_sample_name)):
        os.mkdir(os.path.join(out_dir, new_sample_name))
        
    else:
        print(f"{new_sample_name} exists already")
        return 0
    
    
    for file in file_list:
        
        if not os.path.exists(os.path.join(out_dir, new_sample_name, file[1])):
        
            shutil.copyfile(file[0], os.path.join(out_dir, new_sample_name, file[1]))
    
        else:
            print(f"{os.path.join(out_dir, new_sample_name, file[1])} exists already")

            
    return new_sample_name

def change_names(base, folder):
    
    files = os.listdir(os.path.join(base, folder))
    
    for f in files:
        if not "mcd" in f:
            
            # print(f, re.findall("-[a-zA-Z]+0{1,5}[0-9]+-", f))
            
            sample_name = re.findall(".+_[0-9]+-[0-9]+_..", f)[0]
            roi_num = int("".join([x for x in re.findall("-[a-zA-Z]+0{1,5}[0-9]+-", f)[0][:-1] if x.isnumeric()]))
            channel = re.findall("(?<=-)([A-Z])(?=\.)", f)[0]

            if not os.path.exists(f"{os.path.join(base, folder)}/{sample_name}_{roi_num}_{channel}.TIF"):

                shutil.move(f"{os.path.join(base, folder)}/{f}", f"{os.path.join(base, folder)}/{sample_name}_{roi_num}_{channel}.TIF")
       
            else:
                
                print(f"{os.path.join(base, folder)}/{sample_name}_{roi_num}_{channel}.TIF exists already")

def move_rename_sample(base, sample, out):

    new_name = copy_sample(base, sample, out)
    
    if new_name:
        change_names(out, new_name)
        
        
if __name__ == "__main__":
    
    import os
    from tqdm import tqdm

    samples = [x for x in os.listdir("/data_isilon_main/isilon_images/10_MetaSystems/MetaSystemsData/Multimodal_Imaging_Daria/BM") if "-" in x]

    for sample in samples:
        
        print(sample)
        move_rename_sample("/data_isilon_main/isilon_images/10_MetaSystems/MetaSystemsData/Multimodal_Imaging_Daria/BM", sample, "/data_isilon_main/isilon_images/10_MetaSystems/MetaSystemsData/Multimodal_Imaging_Daria/MapMetIP/SAMPLES")