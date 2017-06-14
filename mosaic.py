# get coll of images
# determine mean colors and mean intensity for each
# read the input image

import sys
import os
from math import ceil
import numpy as np
from skimage import color, data, io
from skimage.transform import resize
from scipy.spatial import KDTree
from random import randint


def is_grey(image):
    return len(image.shape) == 2

def create_mosaic(
    image_path, tiles_path_list, outfile=None,
    horizontal_tiles=100,
    colorization=0,
    even_factor=1
):
    if outfile is None:
        filename = os.path.basename(image_path)
        dirname = os.path.dirname(image_path)
        outfile = ('%s/mosaic.%s') % (dirname, filename)

    image = data.imread(image_path)
    image_is_grey = is_grey(image)

    tiles = []
    tile_means = []
    for filepath in tiles_path_list:
        im = data.imread(filepath)
        if image_is_grey: im = np.uint8(color.rgb2grey(im) * 255)
        if not image_is_grey and is_grey(im):
            continue # TODO avoid grayscale images for now

        tiles.append(im)
        print('path: %s' % filepath)
        print('size: ', im.shape)

        im_mean = np.mean(im, axis=(0, 1))
        if image_is_grey: im_mean = [np.mean(im_mean)]
        tile_means.append(im_mean)

    print('making a KDTree from tile means')
    print(np.asarray(tile_means).shape)
    tile_means_tree = KDTree(tile_means)

    # general assumption that all tiles have the same dims
    (tile_y, tile_x) = tiles[0].shape[0:2]
    mosaic_shape = [0, 0]
    mosaic_shape[1] = tile_x * horizontal_tiles # x
    mosaic_shape[0] = ceil(mosaic_shape[1] * image.shape[0] / image.shape[1]) # y
    mosaic_shape[0] = int(mosaic_shape[0] + tile_y - (mosaic_shape[0] % tile_y)) # y
    if not image_is_grey: mosaic_shape.append(image.shape[2]) # color
    mosaic_shape = tuple(mosaic_shape)

    VERTICAL_TILES = mosaic_shape[0] / tile_y

    print('image original shape', image.shape[0:2])
    print('tile shape', (tile_y, tile_x))
    print('resize image to shape', mosaic_shape[0:2])
    print(mosaic_shape)
    image = resize(image, mosaic_shape, preserve_range=True, order=0)
    mosaic = np.zeros(mosaic_shape, dtype=np.uint8)
    for y in range(0, mosaic_shape[0], tile_y):
        print('y=%d, x=%d' % (y, 0))
        for x in range(0, mosaic_shape[1], tile_x):
            mean = np.mean(image[y:y+tile_y, x:x+tile_x], axis=(0, 1))
            if image_is_grey: mean = [mean]

            # TODO if tile exists in the last k tiles used, use another
            if even_factor > 1:
                (_, smallest_distance_indices) = tile_means_tree.query(mean, k=even_factor)
                rand_idx = randint(0, even_factor-1)
                smallest_distance_index = smallest_distance_indices[rand_idx]
            else:
                (_, smallest_distance_index) = tile_means_tree.query(mean)

            if colorization != 0:
                mosaic[y:y+tile_y, x:x+tile_x] = (
                    colorization * mean +
                    (1 - colorization) * tiles[smallest_distance_index]
                )
            else:
                mosaic[y:y+tile_y, x:x+tile_x] = tiles[smallest_distance_index]

    io.imsave(outfile, mosaic)

    return outfile


if __name__ == '__main__':
    tiles_path = sys.argv[1]
    image_path = sys.argv[2]

    tiles_path_list = [
        os.path.join(tiles_path, f)
        for f in os.listdir(tiles_path)
    ]

    create_mosaic(image_path, tiles_path_list,
        outfile='test.jpg',
        horizontal_tiles=200)
