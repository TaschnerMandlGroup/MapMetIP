from skimage.morphology import convex_hull_image, binary_erosion
import matplotlib.pyplot as plt
from skimage.measure import moments, label, regionprops_table
import numpy as np
from skan.csr import skeleton_to_csgraph
from skan import draw
from skan import Skeleton, summarize
from skimage.morphology import skeletonize

def get_centroid(mask):
    
    M = moments(mask)
    cx, cy = M[1, 0] / M[0, 0],  M[0, 1] / M[0, 0]
    
    return cx, cy


def assymetry(regionmask):
    
    chull = convex_hull_image(regionmask)

    cx_m, cy_m = get_centroid(regionmask)
    cx_h, cy_h = get_centroid(chull)
    
    dist = np.sqrt((cx_m - cx_h)**2 + (cy_m - cy_h)**2)
    
    return dist / regionmask.sum()
    
    
def concavity(regionmask):
    
    chull = convex_hull_image(regionmask)
    
    concavities = binary_erosion((chull.astype(float) - regionmask.astype(float)).astype(bool), footprint=np.ones((3, 3)))
    
    labeled_image = label(concavities)

    num = 0
    for color in np.unique(labeled_image):
         if color != 0:
             if (labeled_image == color).sum() > 10:
                 num += 1

    return num


def fill(regionmask):
    
    chull = convex_hull_image(regionmask)
    return (chull.astype(float) - regionmask.astype(float)).sum() / chull.sum()


def aspect_ratio(regionmask):
    
    props = regionprops_table(regionmask.astype(int), properties=["axis_major_length", "equivalent_diameter_area"])
    
    return props["axis_major_length"] / props["equivalent_diameter_area"] 
    
    
def perimeter_ratio(regionmask):
        
    props = regionprops_table(regionmask.astype(int), properties=["perimeter"])
    
    return (props["perimeter"] ** 2) / regionmask.sum()


def skeleton_morphology(regionmask):

    skeleton = skeletonize(regionmask, method="lee").astype(float)

    _, coordinates = skeleton_to_csgraph(skeleton)

    if len(coordinates[0]) == 1:
        return float(1)

    branch_data = summarize(Skeleton(skeleton, spacing=1), find_main_branch=True)

    longest_path = branch_data["branch-distance"][branch_data["main"]].sum()

    if not any(branch_data["main"]):
        return float(1)
    
    src_nodes = list(branch_data["node-id-src"][branch_data["main"]])
    dst_nodes = list(branch_data["node-id-dst"][branch_data["main"]])

    combined_nodes = [*src_nodes ,*dst_nodes]
    branch_ends = [i for i in combined_nodes if combined_nodes.count(i) == 1]

    start_node_coordinates = np.array([coordinates[0][branch_ends[0]], coordinates[1][branch_ends[0]]])
    end_node_coordinates = np.array([coordinates[0][branch_ends[1]], coordinates[1][branch_ends[1]]])

    image_dist = np.linalg.norm(start_node_coordinates-end_node_coordinates)

    return (longest_path / image_dist).astype(float)