from PIL import Image
import numpy as np
import hashlib
from JSONHelper import JSONHelper
import math

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

def interpolate(pixels, x, y):
    # obtenemos las coordenadas de los 4 puntos mas cercanos a x,y
    x_floor = int(np.floor(x))
    y_floor = int(np.floor(y))
    x_ceil = int(np.ceil(x))
    y_ceil = int(np.ceil(y))

    # decimales de diferencia
    decimal_x = x - x_floor
    decimal_y = y - y_floor

    # obtenemos los pixeles mas cercanos a nuestras coordenadas
    p1 = pixels[y_floor, x_floor] if (0 <= y_floor < pixels.shape[0] and 
                                     0 <= x_floor < pixels.shape[1]) else 0
    p2 = pixels[y_floor, x_ceil] if (0 <= y_floor < pixels.shape[0] and
                                     0 <= x_ceil < pixels.shape[1]) else 0
    p3 = pixels[y_ceil, x_floor] if (0 <= y_ceil < pixels.shape[0] and 
                                    0 <= x_ceil < pixels.shape[1]) else 0
    p4 = pixels[y_ceil, x_ceil] if (0 <= y_ceil < pixels.shape[0] and 
                                   0 <= x_ceil < pixels.shape[1]) else 0

    # realizamos la interpolacion biliniear
    interpolated = (
        (1 - decimal_x) * (1 - decimal_y) * p1 + #contribucion de p1
        decimal_x * (1 - decimal_y) * p2 + # contribucion de p2
        (1 - decimal_x) * decimal_y * p3 + # contribucion de p3
        decimal_x * decimal_y * p4 # contribucion de p4
    )
    return interpolated

def addPaddingToImage(image : Image, mx : int, my : int):
    xl, xr = int(mx/2), int(mx/2)
    yt, yb = int(my/2), int(my/2)

    pixels = getPixels(image)
    heigth, width = pixels.shape[0], pixels.shape[1]

    paddedPixels = None

    if image.mode == "RGB":
        paddedPixels = np.zeros((heigth + yt + yb, width + xl + xr, 3), np.uint8)

    else:
        paddedPixels = np.zeros((heigth + yt + yb, width + xl + xr), np.uint8)
    
    for y in range(heigth):
        for x in range(width):
            paddedPixels[y + yt, x + xl] = pixels[y, x]

    paddedImage = Image.fromarray(paddedPixels)
    setImageID(paddedImage)

    return paddedImage

    
    

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

    if image.mode == "RGB":
        for y in range(sHeight):
            for x in range(sWidth):
                # obtenemos las coordenadas relativas a la imagen original
                orig_x = x / scale
                orig_y = y / scale
                # intepolamos para obtener su valor aproximado
                interpolated = interpolate(pixels, orig_x, orig_y)
                for channel in range(3):
                    image_resampled[y,x,channel] = np.clip(int(interpolated[channel]), 0, 255)
    else:
        for y in range(sHeight):
            for x in range(sWidth):
                # obtenemos las coordenadas relativas a la imagen original
                orig_x = x / scale
                orig_y = y / scale

                # intepolamos para obtener su valor aproximado
                interpolated = interpolate(pixels, orig_x, orig_y)
                image_resampled[y,x] = np.clip(int(interpolated), 0, 255)
    

    scaledImage = Image.fromarray(image_resampled)
    setImageID(scaledImage)
    return scaledImage

def translateImage(image : Image, tx : int = 0, ty : int = 0):
    image_translated = None
    pixels = getPixels(image)
    width, height  = pixels.shape[1], pixels.shape[0]
    newHeight = height + abs(ty)
    newWidth = width + abs(tx)

    ty*=-1

    if image.mode == "RGB":
        image_translated = np.zeros((newHeight,newWidth,3), dtype=np.uint8)
    else:
        image_translated = np.zeros((newHeight,newWidth), dtype=np.uint8)

    # iteramos por las dimensiones de la imagen
    for y in range(height):
        for x in range(width):
            new_x = x + tx
            if ty < 0:
                new_y = y
            else:
                new_y = y + ty
            
            if tx < 0:
                new_x = x
            else:
                new_x = x + tx
            if 0 <= new_x < newWidth and 0 <= new_y < newHeight:
                image_translated[new_y, new_x] = pixels[y, x] 

    translatedImage = Image.fromarray(image_translated)
    setImageID(translatedImage)
    return translatedImage

def rotateImage(image : Image, degrees : float):
    degrees = math.radians(degrees)

    paddedImage = addPaddingToImage(image, 100, 100)

    image_rotated = None
    pixels = getPixels(paddedImage)
    width, height = pixels.shape[1], pixels.shape[0]

    massCenter = getMassCenter(paddedImage)
    x_center = int(massCenter['x'])
    y_center = int(massCenter['y'])
    rotation_matrix = np.transpose(np.array([[np.cos(degrees), -np.sin(degrees)], 
                               [np.sin(degrees), np.cos(degrees)]
                            ]))

    if paddedImage.mode == "RGB":
        image_rotated = np.zeros((height, width, 3), dtype=np.uint8)
        for y in range(height):
            for x in range(width):
                # obtenemos la posicion del punto actual relativo al centro de masa de la imagen 
                point = np.array([x - x_center, y - y_center])

                # hacemos el producto punto con la matriz de rotacion y sumamos los valores del centro de masa
                # para devolverlo a su posicion absoluta en la matriz de pixeles
                rotated_point = np.dot(point, rotation_matrix) + np.array([x_center, y_center])

                # obtenemos su valor mediante interpolacion biliniear
                interpolated = interpolate(pixels, rotated_point[0], rotated_point[1])

                for channel in range(3):
                    # nos aseguramos que no salga de los limites de 0 y 255 con la funcion  de np.clip
                    image_rotated[y, x, channel] = np.clip(int(interpolated[channel]), a_min=0, a_max = 255)

    else:
        image_rotated = np.zeros((height, width), dtype=np.uint8)
        for y in range(height):
            for x in range(width):
                # obtenemos la posicion del punto actual relativo al centro de masa de la imagen 
                point = np.array([x - x_center, y - y_center])

                # hacemos el producto punto con la matriz de rotacion y sumamos los valores del centro de masa
                # para devolverlo a su posicion absoluta en la matriz de pixeles
                rotated_point = np.dot(point, rotation_matrix) + np.array([x_center, y_center])

                # obtenemos su valor mediante interpolacion biliniear
                interpolated = interpolate(pixels, rotated_point[0], rotated_point[1])

                # nos aseguramos que no salga de los limites de 0 y 255 con la funcion  de np.clip
                image_rotated[y, x] = np.clip(int(interpolated), a_min=0, a_max = 255)
    rImage = Image.fromarray(image_rotated)
    setImageID(rImage)
    return rImage
        

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

def getMuInvariant(image : Image, p : int, q : int): # this one is translation invariant
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
    cache.set_value(path, centralMoment)
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

def getEtaInvariant(image : Image, p : int, q : int):
    npqPath = f"n{p}{q}.{image.id}"
    npq = cache.get_value(npqPath)

    if npq != None:
        return npq

    m00 = getMuInvariant(image, 0, 0)

    mpq = getMuInvariant(image, p, q)

    npq = mpq / m00**((p+q)/2 + 1)
    cache.set_value(npqPath, npq)
    return npq

def getPhiInvariants(image : Image):
    phi1 = getMuInvariant(image, 2, 0) + getMuInvariant(image, 0, 2)
    phi2 = getMuInvariant(image, 2, 0) - getMuInvariant(image, 0, 2) ** 2 + 4 * getMuInvariant(image, 1, 1) ** 2
    phi3 = (getMuInvariant(image, 3, 0) - 3 * getMuInvariant(image, 1, 2)) ** 2 + (3 * getMuInvariant(image, 2, 1) - getMuInvariant(image, 0, 3)) ** 2
    return phi1, phi2, phi3


def scaleImagesAndGetInvariants(image : Image, images : (Image)):
    scales = []
    scaledImages = []
    pixelsNoScaled = []
    # pixelsScaled = []
    pixelsBaseImage = getOnePixels(image)
    base = np.sqrt(pixelsBaseImage)
    etaInvariants = []
    etaInvariantsScaled = []

    for im in images:
        pixelsNoScaled.append(getOnePixels(im))
        invariants = (getEtaInvariant(im, 0, 0), getEtaInvariant(im, 1, 1), getEtaInvariant(im, 2, 2))
        etaInvariants.append(invariants)

    for i in range(images.__len__()):
        root = np.sqrt(pixelsNoScaled[i])
        scale = (base - root) / root + 1
        scaledImage = images[i]
        if scale != 1:
            scaledImage = scaleImage(images[i], scale=scale)
            setImageID(scaledImage)
        scaledImages.append(images[i])
        invariants = (getEtaInvariant(scaledImage, 0, 0), getEtaInvariant(scaledImage, 1, 1), getEtaInvariant(scaledImage, 2, 2))
        etaInvariantsScaled.append(invariants)

        scales.append(scale)

    return scaledImages, etaInvariants, etaInvariantsScaled, scales

def translateImagesAndGetInvariants(images : (Image)):
    translations = []
    translatedImages = []
    muInvariants = []
    muInvariantsTranslated = []

    for image in images:
        m00 = getMuInvariant(image, 0, 0)
        m11 = getMuInvariant(image, 1, 1)
        m22 = getMuInvariant(image, 2, 2)

        muInvariants.append((m00, m11, m22))

        x, y = np.random.randint(-250, 250), np.random.randint(-250, 250)
        translations.append((x,y))
        translatedImage = translateImage(image, x, y)
        translatedImages.append(image)

        m00 = getMuInvariant(translatedImage, 0, 0)
        m11 = getMuInvariant(translatedImage, 1, 1)
        m22 = getMuInvariant(translatedImage, 2, 2)

        muInvariantsTranslated.append((m00, m11, m22))
    return translatedImages, muInvariants, muInvariantsTranslated, translations

def rotateImagesAndGetInvariants(images : (Image)):
    rotatedImages : list[any] = []
    rotatedDegrees : list[int] = []
    phiInvariants = []
    phiInvariantsRotated = []


    for im in images:
        degrees = np.random.randint(30, 331) # para qeu sean ángulos que si se notan
        rotatedDegrees.append(degrees)
        phiInvariants.append(getPhiInvariants(im))
        im = rotateImage(im, degrees)
        setImageID(im)
        rotatedImages.append(im)
        phiInvariantsRotated.append(getPhiInvariants(im))

    return rotatedImages, phiInvariants, phiInvariantsRotated, rotatedDegrees  