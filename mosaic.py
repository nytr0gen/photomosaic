# get coll of images
# determine mean colors and mean intensity for each
# read the input image

import sys
from os import path, listdir
from math import ceil
from random import sample
import numpy as np
from skimage import color, data, io
from skimage.transform import resize


tiles_path = sys.argv[1]
image_path = sys.argv[2]

image = data.imread(image_path)
IS_GREY = (len(image.shape) == 2)
HORIZONTAL_TILES = 75

tiles = []
tiles_mean = []
for file in listdir(tiles_path):
    filepath = path.join(tiles_path, file)

    im = data.imread(filepath)
    if IS_GREY: im = color.rgb2grey(im)
    tiles.append(im)
    print('path: %s' % filepath)
    print('size: ', im.shape)

    im_mean = np.mean(im, axis=(0, 1))
    if IS_GREY: im_mean = np.mean(im_mean)
    tiles_mean.append(im_mean)

tile_shape = tiles[0].shape
mosaic_shape = list(image.shape)
mosaic_shape[1] = tile_shape[1] * HORIZONTAL_TILES # x
mosaic_shape[0] = ceil(mosaic_shape[1] * (image.shape[0] / image.shape[1])) # y
mosaic_shape[0] = mosaic_shape[0] + tile_shape[0] - (mosaic_shape[0] % tile_shape[0]) # y
mosaic_shape = tuple(mosaic_shape)
print(image.shape)
print(tile_shape)
print(mosaic_shape)

VERTICAL_TILES = mosaic_shape[0] / tile_shape[0]

image = resize(image, mosaic_shape, preserve_range=True)

tile_y = tile_shape[0]
tile_x = tile_shape[1]
mosaic = np.zeros(mosaic_shape, dtype=np.uint8)
for y in range(0, mosaic_shape[0], tile_y):
    for x in range(0, mosaic_shape[1], tile_x):
        mean = np.mean(image[y:y+tile_y, x:x+tile_x], axis=(0, 1))

        smallest_distance = 1e30
        smallest_distance_index = 0
        # for i in range(0, len(tiles_mean)):
        for i in sample(range(0, len(tiles_mean)), 100):
            distance = np.linalg.norm(mean - tiles_mean[i]) # euclidean distance
            if distance < smallest_distance:
                smallest_distance = distance
                smallest_distance_index = i

        mosaic[y:y+tile_y, x:x+tile_x] = tiles[smallest_distance_index]
        print(x, y)

io.imsave('test.jpg', mosaic)
