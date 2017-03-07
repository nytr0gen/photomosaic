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
from scipy.spatial import KDTree


tiles_path = sys.argv[1]
image_path = sys.argv[2]

image = data.imread(image_path)
IS_GREY = (len(image.shape) == 2)
HORIZONTAL_TILES = 100

tiles = []
tiles_mean = []
for file in listdir(tiles_path):
    filepath = path.join(tiles_path, file)

    im = data.imread(filepath)
    if IS_GREY: im = np.uint8(color.rgb2grey(im) * 255)
    tiles.append(im)
    print('path: %s' % filepath)
    print('size: ', im.shape)

    im_mean = np.mean(im, axis=(0, 1))
    if IS_GREY: im_mean = [np.mean(im_mean)]
    tiles_mean.append(im_mean)

tiles_mean_tree = KDTree(tiles_mean, leafsize=1)

(tile_y, tile_x) = tiles[0].shape[0:2]
mosaic_shape = [0, 0]
mosaic_shape[1] = tile_x * HORIZONTAL_TILES # x
mosaic_shape[0] = ceil(mosaic_shape[1] * image.shape[0] / image.shape[1]) # y
mosaic_shape[0] = mosaic_shape[0] + tile_y - (mosaic_shape[0] % tile_y) # y
if not IS_GREY: mosaic_shape.append(image.shape[2]) # color
mosaic_shape = tuple(mosaic_shape)
print(image.shape)
print((tile_y, tile_x))
print(mosaic_shape)

VERTICAL_TILES = mosaic_shape[0] / tile_y

image = resize(image, mosaic_shape, preserve_range=True)
mosaic = np.zeros(mosaic_shape, dtype=np.uint8)
for y in range(0, mosaic_shape[0], tile_y):
    print('y=%d, x=%d' % (y, 0))
    for x in range(0, mosaic_shape[1], tile_x):
        mean = np.mean(image[y:y+tile_y, x:x+tile_x], axis=(0, 1))
        if IS_GREY: mean = [mean]

        (smallest_distance, smallest_distance_index) = tiles_mean_tree.query(mean)

        mosaic[y:y+tile_y, x:x+tile_x] = tiles[smallest_distance_index]

io.imsave('test.jpg', mosaic)
