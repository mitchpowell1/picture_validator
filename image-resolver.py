import struct
import imghdr
import os
from shutil import copy
from sys import argv

dir_name = '.'
minimum_size = 1024 * 768
valid_directory_path = dir_name + '/valid-pictures'
invalid_directory_path = dir_name + '/invalid-pictures'

def get_image_size(fname):
    '''Determine the image type of fhandle and return its size.
    from draco'''
    with open(fname, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return
        if imghdr.what(fname) == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', head[16:24])
        elif imghdr.what(fname) == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif imghdr.what(fname) == 'jpeg':
            try:
                fhandle.seek(0) # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception: #IGNORE:W0703
                return
        else:
            return
        return width, height

def construct_image_list(dirname): 
    image_formats = [".jpg", ".gif", ".png", ".tga"]
    image_list = []
    for f in os.listdir(dirname):
        extension = os.path.splitext(f)[1]
        if extension.lower() not in image_formats:
            continue
        image_list.append(os.path.join(dirname, f))
    return image_list

def validate_image_size(height, width):
    return (height * width) >= minimum_size


def main():
    if not os.path.exists(invalid_directory_path):
        os.makedirs(invalid_directory_path)
    if not os.path.exists(valid_directory_path):
        os.makedirs(valid_directory_path)
    for image_path in construct_image_list(dir_name):
        image_size = get_image_size(image_path)
        is_valid = False
        try:
            is_valid = validate_image_size(image_size[0], image_size[1])
        except:
            continue

        if is_valid:
            copy(image_path, valid_directory_path)
        else:
            copy(image_path, invalid_directory_path)

if len(argv) > 1:
    dir_name = argv[1]
    main()
else:
    main()
