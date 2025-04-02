from PIL import Image
import numpy as np
import os
import ImageHelper
from JSONHelper import JSONHelper

imgList =  os.listdir("imagenes")[0:2]
images = [Image.open(os.path.join("imagenes", img)) for img in imgList]

for im in images:
    im.id = ImageHelper.getImageID(im)

baseImage = images[0]
# print(ImageHelper.ScaleImagesToEqualOnePixels(baseImage, images))

ImageHelper.getTxtImageFile(baseImage)
