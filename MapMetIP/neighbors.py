from steinbock.measurement.neighbors import measure_neighbors, NeighborhoodType
from tqdm import tqdm

def extract_neighbors(sample, dmax):
    
    for roi, data in tqdm(sample.data.items()):
        
        masks = data["small_segmentation_masks"]
    
        neighbors = measure_neighbors(masks, NeighborhoodType.CENTROID_DISTANCE, "euclidean", dmax=dmax)
        
        sample.data[roi]["neighbors"] = neighbors
        
    return sample