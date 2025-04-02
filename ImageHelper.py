from PIL import Image
import numpy as np
import hashlib
from JSONHelper import JSONHelper

cache = JSONHelper("cache.json")

def getImageID(image : Image):
    image_bytes = image.tobytes()
    return hashlib.md5(image_bytes).hexdigest()

def setImageID(image : Image):
    image.id = getImageID(image)

def getPixels(image : Image):
    height, width  = image.size
    pixel_values = list(image.getdata())
    if image.mode == "RGB":
        channels = 3
    elif image.mode == "L" or image.mode == "P" or image.mode == "1":
        channels = 1
    else:
        print("Unknown mode: %s" % image.mode)
        return None
    if channels == 1:
        pixel_values = np.array(pixel_values).reshape((width, height))
    else:
        pixel_values = np.array(pixel_values).reshape((width, height, channels))
    return pixel_values

def getOnePixels(image : Image):
    height, width  = image.size
    pixels : np = getPixels(image)
    count = 0

    if image.mode == "RGB":
        for x in range(width):
            for y in range(height):
                if np.average(pixels[x][y]) == 255:
                    count += 1
    elif image.mode == "L" or image.mode == "P" or image.mode == "1":
        for x in range(width):
            for y in range(height):
                if pixels[x][y] != 0:
                    count += 1
    return count

def scaleImage(image : Image, scale):
    pixels = getPixels(image)
    width, height = pixels.shape[1], pixels.shape[0]

    sWidth = int(width * scale)
    sHeight = int(height * scale)

    image_resampled = None
    
    if image.mode == "RGB":
        image_resampled = np.zeros((sHeight, sWidth, 3), dtype=np.uint8)
    else:  
        image_resampled = np.zeros((sHeight, sWidth), dtype=np.uint8)

    for y in range(sHeight):
        for x in range(sWidth):
            orig_x = x / scale
            orig_y = y / scale

            x0, y0 = int(orig_x), int(orig_y)
            x1, y1 = min(x0 + 1, width - 1), min(y0 + 1, height - 1)
            dx, dy = orig_x - x0, orig_y - y0

            if image.mode == "RGB":
                for c in range(3): 
                    top = (1 - dx) * pixels[y0, x0, c] + dx * pixels[y0, x1, c]
                    bottom = (1 - dx) * pixels[y1, x0, c] + dx * pixels[y1, x1, c]
                    image_resampled[y, x, c] = int((1 - dy) * top + dy * bottom)
            else: 
                top = (1 - dx) * pixels[y0, x0] + dx * pixels[y0, x1]
                bottom = (1 - dx) * pixels[y1, x0] + dx * pixels[y1, x1]
                image_resampled[y, x] = int((1 - dy) * top + dy * bottom)

    scaledImage = Image.fromarray(image_resampled)
    setImageID(scaledImage)
    return scaledImage

def translateImage(image : Image, tx : int = 0, ty : int = 0):
    image_translated = None
    pixels = getPixels(image)
    width, height  = pixels.shape[1], pixels.shape[0]
    newHeight = height + abs(ty)
    newWidth = width + abs(tx)

    if image.mode == "RGB":
        image_translated = np.zeros((newHeight,newWidth,3), dtype=np.uint8)
    else:
        image_translated = np.zeros((newHeight,newWidth), dtype=np.uint8)

    # iteramos por las dimensiones de la imagen
    for y in range(height):
        for x in range(width):
            new_x = x + tx
            new_y = y + ty
            if 0 <= new_x < newWidth and 0 <= new_y < newHeight:
                image_translated[new_y, new_x] = pixels[y, x] 

    translatedImage = Image.fromarray(image_translated)
    setImageID(translatedImage)
    return translatedImage

# ESTA ES MANTENIENDO LAS DIMENSIONES DE LA IMAGEN, PERO ESO NO QUIERE EL PROFESOR
# def translateImageClassic(image : Image, tx : int = 0, ty : int = 0):
#     image_translated = None
#     pixels = getPixels(image)
#     width, height  = pixels.shape[1], pixels.shape[0]

#     ty *= -1

#     if image.mode == "RGB":
#         image_translated = np.zeros((height,width,3), dtype=np.uint8)
#     else:
#         image_translated = np.zeros((height,width), dtype=np.uint8)

#     for y in range(height):
#         for x in range(width):
#             new_x = x + tx
#             new_y = y + ty
#             if 0 <= new_x < width and 0 <= new_y < height:
#                 image_translated[new_y, new_x] = pixels[y, x] 

#     return Image.fromarray(image_translated)

def getMassCenter(image: Image):
    path = f"mass_center.{image.id}"
    massCenter = cache.get_value(path)
    if massCenter != None:
        return massCenter

    My, Mx = float(0), float(0)
    pixels = getPixels(image)
    totalMass = np.sum(pixels)
    width, height = pixels.shape[1], pixels.shape[0]

    if image.mode == "RGB":
        for y in range(height):
            for x in range(width):
                sum_val = np.sum(pixels[y][x])
                My += x * sum_val  
                Mx += y * sum_val
    else:
        for y in range(height):
            for x in range(width):
                value = pixels[y][x]
                My += (x * value)
                Mx += (y * value)
    x = My / totalMass
    y = Mx / totalMass
    massCenter = {}
    massCenter["x"] = float(x)
    massCenter["y"] = float(y)
    cache.set_value(path, massCenter)
    return massCenter

def getCentralMoment(image : Image, p : int, q : int): # this one is translation invariant
    pixels = getPixels(image)
    massCenter = getMassCenter(image)
    width, height = pixels.shape[1], pixels.shape[0]

    path = f"m{p}{q}.{image.id}"

    centralMoment = cache.get_value(path)
    if centralMoment != None:
        return centralMoment
    else: centralMoment = 0

    if image.mode == "RGB":
        for y in range(height):
            for x in range(width):
                centralMoment += (x - massCenter['x'])**p * (y - massCenter['y'])**q * np.sum(pixels[y][x])
    else:
        for y in range(height):
            for x in range(width):
                centralMoment += (x - massCenter['x'])**p * (y - massCenter['y'])**q * pixels[y][x]
    cache.set_value(path, centralMoment[0])
    return centralMoment

def getRawMoment(image : Image, p : int, q : int):
    pixels = getPixels(image)
    width, height = pixels.shape[1], pixels.shape[0]
    rawMoment = 0
    if image.mode == "RGB":
        for y in range(height):
            for x in range(width):
                rawMoment += (x)**p * (y)**q * np.sum(pixels[y][x])
    else:
        for y in range(height):
            for x in range(width):
                rawMoment += (x)**p * (y)**q * pixels[y][x]
    
    return rawMoment

def getNuInvariant(image : Image, p : int, q : int):
    npqPath = f"n{p}{q}.{image.id}"
    npq = cache.get_value(npqPath)
    print("Obteniendo npq")

    if npq != None:
        return npq

    m00 = getCentralMoment(image, 0, 0)

    mpq = getCentralMoment(image, p, q)

    npq = mpq / m00**((p+q)/2 + 1)
    cache.set_value(npqPath, npq[0])
    return npq

def ScaleImagesToEqualOnePixels(image : Image, images : (Image)):
    scales = []
    scaledImages = []
    pixelsNoScaled = []
    # pixelsScaled = []
    pixelsBaseImage = getOnePixels(image)
    base = np.sqrt(pixelsBaseImage)
    nuInvariant = [[] for _ in range(3)]
    nuInvariantScaled = [[] for _ in range(3)]

    for im in images:
        pixelsNoScaled.append(getOnePixels(im))
        nuInvariant[0].append(getNuInvariant(im, 0, 0))
        nuInvariant[1].append(getNuInvariant(im, 1, 1))
        nuInvariant[2].append(getNuInvariant(im, 2, 2))

    for i in range(images.__len__()):
        root = np.sqrt(pixelsNoScaled[i])
        scale = (base - root) / root + 1
        im = images[i]
        if scale == 1:
            scaledImages.append(images[i])
            # pixelsScaled.append(getOnePixels(images[i]))
            nuInvariantScaled[0].append(nuInvariant[0][i])
            nuInvariantScaled[1].append(nuInvariant[1][i])
            nuInvariantScaled[2].append(nuInvariant[2][i])
        else:
            image = scaleImage(images[i], scale=scale)
            scaledImages.append(image)
            # pixelsScaled.append(getOnePixels(image))
            nuInvariantScaled[0].append(getNuInvariant(im, 0, 0))
            nuInvariantScaled[1].append(getNuInvariant(im, 1, 1))
            nuInvariantScaled[2].append(getNuInvariant(im, 2, 2))

        scales.append(scale)
    
    return scaledImages, nuInvariant, nuInvariantScaled, scales