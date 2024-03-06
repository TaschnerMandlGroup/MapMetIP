
from skan.csr import skeleton_to_csgraph
from skan import draw
from skan import Skeleton, summarize
from skimage.morphology import skeletonize
import numpy as np

import matplotlib.pyplot as plt

def skeleton_morphology(regionmask):

    skeleton = skeletonize(regionmask, method="lee").astype(float)

    plt.imshow(skeleton); plt.show()

    _, coordinates = skeleton_to_csgraph(skeleton)
    
    # if len(coordinates[0]) == 1:
    #     return 1

    branch_data = summarize(Skeleton(skeleton, spacing=1), find_main_branch=True)

    longest_path = branch_data["branch-distance"][branch_data["main"]].sum()

    # if not any(branch_data["main"]):
    #     return 1

    src_nodes = list(branch_data["node-id-src"][branch_data["main"]])
    dst_nodes = list(branch_data["node-id-dst"][branch_data["main"]])

    combined_nodes = [*src_nodes ,*dst_nodes]
    branch_ends = [i for i in combined_nodes if combined_nodes.count(i) == 1]

    start_node_coordinates = np.array([coordinates[0][branch_ends[0]], coordinates[1][branch_ends[0]]])
    end_node_coordinates = np.array([coordinates[0][branch_ends[1]], coordinates[1][branch_ends[1]]])

    image_dist = np.linalg.norm(start_node_coordinates-end_node_coordinates)

    return longest_path / image_dist