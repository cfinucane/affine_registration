#!/usr/bin/env python

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import os
import sys
import json
from transformations import affine_matrix_from_points
from scipy.ndimage import affine_transform
from PIL import Image
import multiprocessing
import functools
import scipy.misc

def transform_image(d, tp):
    # Unpack the label data for this image
    filename = d["filename"]
    fp = np.array(d["points"]).T

    # Convert from image coordinates to matrix coordinates
    fp = np.flipud(fp)

    # Load the image data
    print "Processing {!r}...".format(os.path.basename(filename))
    im = Image.open(filename)
    im_r, im_g, im_b = map(np.array, im.split())

    # Calculate the affine transformation
    H = affine_matrix_from_points(tp, fp)

    # Apply the transformation (to each component individually)
    im2_r = affine_transform(im_r, H[:2, :2], (H[0, 2], H[1, 2]))
    im2_g = affine_transform(im_g, H[:2, :2], (H[0, 2], H[1, 2]))
    im2_b = affine_transform(im_b, H[:2, :2], (H[0, 2], H[1, 2]))

    # Recombine components
    im2 = Image.merge('RGB', (Image.fromarray(im2_r),
                              Image.fromarray(im2_g),
                              Image.fromarray(im2_b)))

    # Save the output file
    out_filename = os.path.join(os.path.dirname(filename),
                                "transformed_" + os.path.basename(filename))
    scipy.misc.imsave(out_filename, im2)

    # Release images from memory (just in case)
    del im, im_r, im_g, im_b
    del im2, im2_r, im2_g, im2_b

def transform_images_in_directory(img_dir):
    # Load in marker point data
    with open(os.path.join(img_dir, "label_data.json")) as f:
        label_data = json.load(f)

    # Make all image paths absolute
    for d in label_data:
        d["filename"] = os.path.join(img_dir, d["filename"])

    # Use the marker locations in the 1st image as the target for all subsequent images
    tp = np.array(label_data[0]["points"]).T
    tp = np.flipud(tp) # Convert from image coordinates to matrix coordinates

    # Run multiple calls to transform_image in parallel in order to properly
    # utilize multi-core systems
    pool = multiprocessing.Pool()
    pool.map(functools.partial(transform_image, tp=tp), label_data)

    print "Finished."
    pool.terminate()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: {} [source_image_directory]".format(sys.argv[0])
        sys.exit(1)

    transform_images_in_directory(sys.argv[1])

