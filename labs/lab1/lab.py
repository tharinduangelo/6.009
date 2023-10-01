#!/usr/bin/env python3
#6.009 lab 1
# Tharindu Withanage
# collaborators: none

import math

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!

def pixel_dim_change(image):
    """
    Parameters
    ----------
    image : dict with key:value pairs 'height':int, 'width':list, 'pixels': list of ints

    Returns
    -------
    dict, an image with pixels stored as a two dimensional list, with each list in the list corresponding to
    a particular row in the image

    """
    res = []
    for i in range(image['height']):
        res.append(image['pixels'][i * image['width'] : (i + 1) * image['width']])
    return {'height': image['height'], 'width': image['width'], 'pixels': res}
    
def get_pixel(image, x, y):
    """
    Parameters
    ----------
    image : dict with key:value pairs 'height':int, 'width':list, 'pixels': list of ints
    x: int
    y: int

    Returns
    -------
    an int corresponding to the pixel value at row x and column y of the image

    """
    return image['pixels'][x * image['width'] + y]


def set_pixel(image, x, y, c):
    """
    Parameters
    ----------
    image : dict with key:value pairs 'height':int, 'width':list, 'pixels': list of ints
    x: int
    y: int
    c: float
    
    Returns
    -------
    None, sets the value of the pixel at row x and column y of the image to c

    """
    image['pixels'][x * image['width'] + y] = c

def get_pixel_extended(image, x, y):
    """
    Parameters
    ----------
    image : dict with key:value pairs 'height':int, 'width':list, 'pixels': list of ints
    x: an int
    y: an int
    Returns
    -------
    int, returns pixel values of a point with row value x and column value y, including points outside
    of the image
    
    Values to the left of the image should be considered to have the values from the first column
    Values to the right of the image should be considered to have the values from the last column
    Values to the top of the image should be considered to have the values from the first row
    Values to the bottom of the image should be considered to have the values from the last row
    """
    
    x = 0 if x < 0 else image['height'] - 1 if x >= image['height'] else x
    y = 0 if y < 0 else image['width'] - 1 if y >= image['width'] else y
    return image['pixels'][x * image['width'] + y] 

def apply_per_pixel(image, func):
    """
    Parameters
    ----------
    image : dict with key:value pairs 'height':int, 'width':list, 'pixels': list of ints
    func: a function

    Returns
    -------
    dict, an image with each of the pixel values altered by the function

    """
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'][:]
    }
    for x in range(image['height']):
        for y in range(image['width']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)
    return result


def inverted(image):
    """
    Parameters
    ----------
    image : dict with key:value pairs 'height':int, 'width':list, 'pixels': list of ints

    Returns
    -------
    dict, an image with each of the pixel values inverted, i.e. reflected over the middle value

    """
    return apply_per_pixel(image, lambda c: 255-c)


# HELPER FUNCTIONS

def correlate(image, kernel):
    """
    Compute the result of correlating the given image with the given kernel.

    The output of this function should have the same form as a 6.009 image (a
    dictionary with 'height', 'width', and 'pixels' keys), but its pixel values
    do not necessarily need to be in the range [0,255], nor do they need to be
    integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    Kernel is represented as a 2D list (list of lists), with each list inside the main list 
    corresponding to a particular row.
    """
    f = len(kernel) // 2 # get the distance from the middle element of the kernel to the side
    img = pixel_dim_change(image) # convert the pixels to a 2d list
    res = {'height': img['height'], 'width': img['width'], 'pixels': []} # initialize dict to store results
    # go through every pixel element
    for x in range(img['height']):
        for y in range(img['width']):
            temp = 0
            # apply the kernel to all surrounding values of the pixel
            for i in range(-f, f + 1):
                for j in range(-f, f + 1):
                    temp += get_pixel_extended(image, x + i, y + j) * kernel[i + f][j + f]
            res['pixels'].append(temp)
    return res


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    for i, p in enumerate(image['pixels']):
        if p > 255:
            image['pixels'][i] = 255
        elif p < 0:
            image['pixels'][i] = 0
        elif type(p) != int:
            image['pixels'][i] = round(p)
    
    return image

def kernel(m, n, a):
    """
    Parameters
    ----------
    m : an int, representing the row size of the kernel to be outputted
    n : an int, representing the column size of the kernel to be outputted

    Returns
    -------
    list, a 2d list of size nxn, with each element having the value a

    """
    return [[a for j in range(n)] for i in range(m)]

def box_kernel(n):
    """
    Parameters
    ----------
    n : an int, odd number representing the size of the kernel to be outputted

    Returns
    -------
    list, a 2d list of size nxn, with each element having the value 1/n^2

    """
    return kernel(n, n, 1 / (n * n))

# FILTERS

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    kernel = box_kernel(n)

    # then compute the correlation of the input image with that kernel
    img = correlate(image, kernel)

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    return round_and_clip_image(img)

def sharp_kernel(n):
    """
    Parameters
    ----------
    n: an int, odd number indicating the size of the kernel

    Returns
    -------
    list, a 2D list representing the sharpness kernel of size nxn. All the elements have a value
    of -1/n^2 apart from the middle value which has a value of 2-1/n^2

    """
    res = kernel(n, n, -1 / (n * n))
    res[n // 2][n // 2] += 2
    return res
    
def sharpened(image, n):
    """
    Parameters
    ----------
    image : dict with key:value pairs 'height':int, 'width':list, 'pixels': list of ints
    n: int, odd number indicating size of sharpness kernel to be applied

    Returns
    -------
    dict, an image with each of the pixel values altered by the sharpness kernel

    """
    # create sharpness kernel
    kernel = sharp_kernel(n)
    # get the image with pixels altered by sharpness kernel
    img = correlate(image, kernel)
    #round and clip the pixel values to return a valid image representation
    return round_and_clip_image(img)

def edges(image):
    """
    Parameters
    ----------
    image : dict with key:value pairs 'height':int, 'width':list, 'pixels': list of ints

    Returns
    -------
    dict, an image with each of the pixel values altered so that the edges are highlighted using
    a Sobel operator

    """
    # create two kernels
    Kx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    Ky = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
    # get two images after applying the kernels
    Ox = correlate(image, Kx)
    Oy = correlate(image, Ky)
    res = {'height': image['height'], 'width': image['width'], 'pixels': []}
    # take the squared root of the sum of each of the squared pixel values of the two images
    #round and add to add to pixel list of result image to return
    for i in range(len(image['pixels'])):
        res['pixels'].append(round(math.sqrt(Ox['pixels'][i] ** 2 + Oy['pixels'][i] ** 2)))
        
    return round_and_clip_image(res)
                  

# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    #save_image(load_image('test_images/cat.png'), 'test_images/test2/cat2.png')
    #save_image(inverted(load_image('test_images/bluegill.png')),'test_images/test2/bluegill_inverted.png')
    # kernel = []
    # kernel_size = 9
    # for i in range(kernel_size):
    #     kernel.append([0,0,0,0,0,0,0,0,0])
    # kernel[2][0] = 1
    # save_image(round_and_clip_image(correlate(load_image('test_images/pigbird.png'), kernel)),'test_images/test2/pigbird_correlated.png')
    #save_image(blurred(load_image('test_images/cat.png'), 5),'test_images/test2/cat_blur.png')
    #save_image(sharpened(load_image('test_images/python.png'), 11),'test_images/test2/python_sharpen.png')
    #save_image(edges(load_image('test_images/construct.png')), 'test_images/test2/construct_edges.png')
    #save_image(edges(load_image('test_images/centered_pixel.png')), 'test_results/centered_pixel_edges.png')
    pass
