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

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import sys
import json

def request_labels_for_directory(img_dir):
    """ Interactively ask the user to mark the registration points for each image
        in the directory `img_dir`.

        Outputs label data into `img_dir/label_data.json`. """

    # Make sure that label data file doesn't already exist,
    # lest we inadvertently clobber it
    label_data_filename = os.path.join(img_dir, "label_data.json")
    if os.path.exists(label_data_filename):
        print "Label data for this directory appears to already exist in file {!r}.".format(label_data_filename)
        clobber = None
        while clobber not in ("y", "n"):
            clobber = raw_input("Overwrite (y/n)? ")
        if clobber == "n":
            print "Aborting."
            return

    label_data = []
    img_filenames = os.listdir(img_dir)

    for img_filename in img_filenames:
        print "Loading {!r}...".format(img_filename)
        try:
            img = mpimg.imread(os.path.join(img_dir, img_filename))
        except IOError:
            print "Does not appear to be an image file.  Skipping."
            continue

        plt.imshow(img)
        plt.draw()

        print "Please click on the 4 registration points, in order."
        pts = plt.ginput(4, timeout=0)
        label_data.append({'filename': img_filename,
                           'points': pts})

        print "Got points: ", pts

        # release image from memory
        del img

    print "Saving label data to file {!r}...".format(label_data_filename)
    with open(label_data_filename, "w") as f:
        json.dump(label_data, f)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: {} [source_image_directory]".format(sys.argv[0])
        sys.exit(1)

    request_labels_for_directory(sys.argv[1])
