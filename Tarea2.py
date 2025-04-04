import os
from PIL import Image
import numpy as np
import ImageHelper
import MorphologyHelper

# Define input and output directories
img_dir = "imagenes"
txt_dir = "txt_images"
plot_img_dir = "plt_images"
contour_txt_dir = "contour_txt_images"
morph_dir = "morph_images"

import TableHelper
from JSONHelper import JSONHelper

# obtenemos las imágenes de la carpeta de imágenes
imgList =  os.listdir("imagenes")[0:5]
images = []
for imPath in imgList:
    with Image.open(os.path.join("imagenes", imPath)) as im:
        im = im.convert("1")
        im.id = ImageHelper.getImageID(im)
        images.append(im)

# definimos la imagen base para el escalado de las imágenes
baseImage = images[0]


# ImageHelper.getTxtImagesFromFolder(img_dir, txt_dir)

# Punto 5

# ImageHelper.plotBinaryImagesFromFolder(txt_dir,plot_img_dir)

# Punto 6

# ImageHelper.plotBinaryImageNoGridFromFolder(contour_txt_dir,"contour_images")

# ImageHelper.getContoursOfFolder(txt_dir,contour_txt_dir)

# Punto 8

MorphologyHelper.getMorphImagesFromFolder(txt_dir,morph_dir)

# trasladamos las imágenes y obtenemos las invariantes de mu o momentos centrales
translatedImages, muInvariants, muInvariantsTranslated, translations = ImageHelper.translateImagesAndGetInvariants(images)
TableHelper.presentMuInvariantsOnTable(imgList, translations, muInvariants, muInvariantsTranslated)

# escalamos las imágenes y obtenemos los invariantes eta
scaledImages, etaInvariants, etaInvariantsScaled, scales = ImageHelper.scaleImagesAndGetInvariants(baseImage, images)
TableHelper.presentEtaInvariantsOnTable(imgList, scales, etaInvariants, etaInvariantsScaled)

# rotamos las imágenes y obtenemos los invariantes de phi
scaledImages, phiInvariants, phiInvariantsScaled, degrees = ImageHelper.rotateImagesAndGetInvariants(images)
TableHelper.presentPhiInvariantsOnTable(imgList, degrees, phiInvariants, phiInvariantsScaled)