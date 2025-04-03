import os
from PIL import Image
import numpy as np
import ImageHelper

# Define input and output directories
img_dir = "imagenes"
txt_dir = "txt_images"
plot_img_dir = "plt_images"
contour_txt_dir = "contour_txt_images"



# ImageHelper.getTxtImagesFromFolder(img_dir, txt_dir)

# Punto 5

# ImageHelper.plotBinaryImagesFromFolder(txt_dir,plot_img_dir)

ImageHelper.getContoursOfFolder(txt_dir,contour_txt_dir)