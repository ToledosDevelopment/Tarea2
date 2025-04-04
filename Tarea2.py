from PIL import Image
import numpy as np
import os
import ImageHelper
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

# trasladamos las imágenes y obtenemos las invariantes de mu o momentos centrales
translatedImages, muInvariants, muInvariantsTranslated, translations = ImageHelper.translateImagesAndGetInvariants(images)
TableHelper.presentMuInvariantsOnTable(imgList, translations, muInvariants, muInvariantsTranslated)

# escalamos las imágenes y obtenemos los invariantes eta
scaledImages, etaInvariants, etaInvariantsScaled, scales = ImageHelper.scaleImagesAndGetInvariants(baseImage, images)
TableHelper.presentEtaInvariantsOnTable(imgList, scales, etaInvariants, etaInvariantsScaled)

# rotamos las imágenes y obtenemos los invariantes de phi
scaledImages, phiInvariants, phiInvariantsScaled, degrees = ImageHelper.rotateImagesAndGetInvariants(images)
TableHelper.presentPhiInvariantsOnTable(imgList, degrees, phiInvariants, phiInvariantsScaled)