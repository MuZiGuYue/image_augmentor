import sys, os, re, traceback
from os.path import isfile
from ops.rotate import Rotate
from ops.fliph import FlipH
from ops.flipv import FlipV
from ops.zoom import Zoom
from ops.blur import Blur
from ops.noise import Noise
from ops.translate import Translate
from skimage.io import imread, imsave

EXTENSIONS = ['png', 'jpg', 'jpeg', 'bmp']
OPERATIONS = [Rotate, FlipH, FlipV, Translate, Noise, Zoom, Blur]

'''
Augmented files will have names matching the regex below, eg

    original__rot90__crop1__flipv.jpg

'''
AUGMENTED_FILE_REGEX = re.compile('^.*(__.+)+\\.[^\\.]+$')
EXTENSION_REGEX = re.compile('|'.join(map(lambda n: '.*\\.' + n + '$', EXTENSIONS)))


def build_augmented_file_name(original_name, ops):
    root, ext = os.path.splitext(original_name)
    result = root
    for op in ops:
        result += '__' + op.code
    return result + ext


def work(d, f, op_lists):
    try:
        in_path = os.path.join(d, f)
        for op_list in op_lists:
            out_file_name = build_augmented_file_name(f, op_list)
            if isfile(os.path.join(d, out_file_name)):
                continue
            img = imread(in_path)
            for op in op_list:
                img = op.process(img)
            imsave(os.path.join(d, out_file_name), img)
    except:
        traceback.print_exc(file=sys.stdout)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: {} <image directory> <operation> (<operation> ...)'.format(sys.argv[0])
        sys.exit(1)

    image_dir = sys.argv[1]
    if not os.path.isdir(image_dir):
        print 'Invalid image directory: {}'.format(image_dir)
        sys.exit(2)

    op_codes = sys.argv[2:]
    op_lists = []
    for op_code_list in op_codes:
        op_list = []
        for op_code in op_code_list.split(','):
            op = None
            for op in OPERATIONS:
                op = op.match_code(op_code)
                if op:
                    op_list.append(op)
                    break

            if not op:
                print 'Unknown operation {}'.format(op_code)
                sys.exit(3)
        op_lists.append(op_list)

    matches = []
    for dir_info in os.walk(image_dir):
        dir_name, _, file_names = dir_info
        print 'Processing {}...'.format(dir_name)

        for file_name in file_names:
            if EXTENSION_REGEX.match(file_name):
                work(dir_name, file_name, op_lists)
