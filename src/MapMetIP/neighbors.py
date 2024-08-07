from steinbock.measurement.neighbors import measure_neighbors, NeighborhoodType
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def extract_neighbors(sample, dmax):
    
    for roi, data in tqdm(sample.data.items()):
        
        masks = data["small_segmentation_masks"]
    
        neighbors = measure_neighbors(masks, NeighborhoodType.EUCLIDEAN_BORDER_DISTANCE, "euclidean", dmax=dmax)
        
        sample.data[roi]["neighbors"] = neighbors

        logger.debug(f"Extracted neighbors for ROI {str(roi)} with dimensions {neighbors.shape}.")
        
    return sample