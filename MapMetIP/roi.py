import numpy as np

class ROIS():
    pass

class ROI():
    
    def __init__(self, im_type):
        
        self.im_type = im_type
        
    
    def add_channel(self, channel_name, image):
        
        setattr(self, channel_name, image)
        
        if all(hasattr(self, attr) for attr in ["R", "G", "B"]) and not hasattr(self, "RGB"):
            
            setattr(self, "RGB", np.stack((self.R, self.G, self.B)).transpose(1,2,0))
            setattr(self, "channels", ["R", "G", "B"])
        
    