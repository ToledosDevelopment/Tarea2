import os
from PIL import Image
import ImageHelper
import MorphologyHelper
import TableHelper
from JSONHelper import JSONHelper

# Define input and output directories
img_dir = "imagenes"
txt_dir = "txt_images"
plot_img_dir = "plt_images"
contour_txt_dir = "contour_txt_images"
morph_dir = "morph_images"

# obtenemos las imágenes de la carpeta de imágenes
imgList =  os.listdir("imagenes")[0:5]
images = []
for imPath in imgList:
    with Image.open(os.path.join("imagenes", imPath)) as im:
        im = im.convert("1")
        ImageHelper.setImageID(im)
        images.append(im)


# ImageHelper.getTxtImagesFromFolder(img_dir, txt_dir)

# Punto 2, 3 y 4

# definimos la imagen base para el escalado de las imágenes
baseImage = images[0]
# escalamos las imágenes, obtenemos los invariantes eta y los uno pixeles
scaledImages, etaInvariants, etaInvariantsScaled, scales, opx, opxScaled = ImageHelper.scaleImagesAndGetInvariants(baseImage, images)
TableHelper.presentEtaInvariantsOnTable(imgList, scales, etaInvariants, etaInvariantsScaled, opx, opxScaled)

# Con la función getTxtImagesFromFolder() generamos los archivos txt de las imagenes originales ya en aproximadamente la misma escala de 1-pixeles

# Punto 5

# ImageHelper.plotBinaryImagesFromFolder(txt_dir,plot_img_dir)

# Punto 6

# ImageHelper.plotBinaryImageNoGridFromFolder(contour_txt_dir,"contour_images")

# ImageHelper.getContoursOfFolder(txt_dir,contour_txt_dir)

# Punto 7

# trasladamos las imágenes y obtenemos las invariantes de mu (momentos centrales)
translatedImages, muInvariants, muInvariantsTranslated, translations = ImageHelper.translateImagesAndGetInvariants(images)
TableHelper.presentMuInvariantsOnTable(imgList, translations, muInvariants, muInvariantsTranslated)

# Punto 8

# rotamos las imágenes y obtenemos los invariantes de phi
scaledImages, phiInvariants, phiInvariantsScaled, degrees = ImageHelper.rotateImagesAndGetInvariants(images)
TableHelper.presentPhiInvariantsOnTable(imgList, degrees, phiInvariants, phiInvariantsScaled)

# Punto 9
# Generamos los cambios mofologicos y remarcamos las diferencias con la imagen original con color verde

# MorphologyHelper.getMorphImagesFromFolder(txt_dir,morph_dir)