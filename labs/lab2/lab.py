#!/usr/bin/env python3

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
import math
from PIL import Image


# VARIOUS FILTERS

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

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    
    def one_color(image, color):
        
        """
        Parameters
        ----------
        image : dict corresponding to a colored image
        color : int corresponding to which colored pixels we want from the image
                0 = red
                1 = blue
                2 = green

        Returns
        -------
        dict containing a list of int corresponding to pixel values of a particular color

        """
        return {'height': image['height'], 'width': image['width'], 'pixels' : [x[color] for x in image['pixels']]}
        
    def color_filter(image):
        """
        Parameters
        ----------
        image : a dict corresponding to a colored image

        Returns
        -------
        a dict, with the filter applied to all the pixel values

        """
        # apply filter to each of the pixel colors
        red = filt(one_color(image, 0))
        green = filt(one_color(image, 1))
        blue = filt(one_color(image, 2))
        # get list of tuples of pixels after filter has been applied
        recombined_pixels = [(r, g, b) for r, g, b in zip(red['pixels'], green['pixels'], blue['pixels'])]
        return {'height': image['height'], 'width': image['width'], 'pixels' : recombined_pixels}
    
    return color_filter
        

def make_blur_filter(n):
    """
    Takes an int n as input and outputs a function that takes an image as input,
    applies a box blur of size n and returns an image
    """
    def blur(image):
        """
        Takes an image dict and outputs an image with a box blur of size n applied
        """
        return blurred(image, n)
    return blur

def make_sharpen_filter(n):
    """
    Takes an int n as input and outputs a function that takes an image as input,
    applies a sharpening filter of size n and returns an image    
    """
    def sharpen(image):
        """
        Takes an image dict and outputs an image with a sharpening filter of size n applied
        """
        return sharpened(image, n)
    return sharpen


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def filter_sum(image):
        """
        Takes an image dict and applies to it filters in a list, and returns the 
        resulting image
        """
        x = image
        for f in filters:
            x = f(x)
        return x
    return filter_sum


# SEAM CARVING

# Main Seam Carving Implementation

def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image.
    """
    for col in range(ncols):
        grey = greyscale_image_from_color_image(image)
        energy = compute_energy(grey)
        cem = cumulative_energy_map(energy)
        seam = minimum_energy_seam(cem)
        image = image_without_seam(image, seam)
    
    return image


# Optional Helper Functions for Seam Carving

def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    
    greyscale_pixels = [round(0.299 * x[0] + 0.587 * x[1] + 0.114 * x[2]) for x in image['pixels']]
    return {'height': image['height'], 'width': image['width'], 'pixels': greyscale_pixels}


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy
    function), computes a "cumulative energy map" as described in the lab 2
    writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    
    for x in range(1, energy['height']):
        for y in range(energy['width']):
            set_pixel(energy, x, y, get_pixel(energy, x, y) + min(get_pixel_extended(energy, x - 1, y - 1), \
                                    get_pixel(energy, x - 1, y), get_pixel_extended(energy, x - 1, y + 1)))
    return energy


def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """
    res = [] # initialize list to store pixel values of seam
    
    # get min value pixel at bottom row
    cem_2d = pixel_dim_change(cem)
    last_row = cem_2d['pixels'][cem['height'] - 1]
    y_low = last_row.index(min(last_row))
    res.append((cem['height'] - 1, y_low)) # store pixels as x,y tuples
    

    # backtrack to find seam
    for x in range(cem['height'] - 2, -1, -1):
        #check top adjacent values
        temp = [get_pixel_extended(cem, x, y_low - 1),get_pixel(cem, x, y_low), get_pixel_extended(cem, x, y_low + 1)]
        if y_low - 1 < 0:
            temp[0] = math.inf # set to infinity if out of bounds
        elif y_low + 1 >= cem['width']:
            temp[2] = math.inf # set to infinity if out of bounds
        y_low = temp.index(min(temp)) + y_low - 1 # get y index of minimum value
        res.append((x, y_low))
    
    #calculate 1d pixel values from x,y tuples, and return
    return [p[0] * cem['width'] + p[1] for p in res]


def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    seam.sort()
    new_pixels = image['pixels'][:]
    shift = 0 # to compensate for reduction in length of list when pixels are deleted
    for i in seam:
        del new_pixels[i - shift]
        shift += 1
    
    return {'height': image['height'], 'width': image['width'] - 1, 'pixels': new_pixels}


# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES

def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
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


def save_greyscale_image(image, filename, mode='PNG'):
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

def threshold(image, n):
    """
    Given an image, set the pixel values to 255 if pixel value is greater or equal to n. Else set to 0.
    Return new image
    """
    
    new_pixels = [255 if p >= n else 0 for p in image['pixels']]
    return {'height': image['height'], 'width': image['width'], 'pixels': new_pixels}

def outline(filename, thickness):
    '''takes the filename of a color image and returns a grayscale image of the outline'''
    
    image = load_greyscale_image(filename)
    return inverted(threshold(edges(image), thickness))

def blueprint(filename, thickness):
    '''takes the filename of a color image and returns a color image corresponding to the blueprint'''
    
    image = outline(filename, thickness) #get outline of image
    new_pixels = [(255, 255, 255) if p == 0 else (74, 109, 229) for p in image['pixels']] # create blueprint
    return {'height': image['height'], 'width': image['width'], 'pixels': new_pixels}

def edge_enhancement(filename, thickness):
    '''takes the filename of a color image and returns the image with edges enhanced'''
    
    original = load_color_image(filename) # original image
    modified = outline(filename, thickness) # get outline of image
    
    new_pixels = original['pixels'][:]
    
    #enhance outline
    for idx, p in enumerate(modified['pixels']):
        if p == 0: new_pixels[idx] = (0, 0, 0)
            
    return {'height': original['height'], 'width': original['width'], 'pixels': new_pixels}

if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    #inverted_image = color_filter_from_greyscale_filter(inverted)(load_color_image("test_images/cat.png"))
    #save_color_image(inverted_image, "results/inverted_cat.png")
    # blurred_image = color_filter_from_greyscale_filter(make_blur_filter(9))(load_color_image("test_images/python.png"))
    # save_color_image(blurred_image, "results/blurred_python.png")
    # sharpened_image = color_filter_from_greyscale_filter(make_sharpen_filter(7))(load_color_image("test_images/sparrowchick.png"))
    # save_color_image(sharpened_image, "results/sharpened_sparrowchick.png")
    # filter1 = color_filter_from_greyscale_filter(edges)
    # filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    # filt = filter_cascade([filter1, filter1, filter2, filter1])
    # modified_frog = filt(load_color_image("test_images/frog.png"))
    # save_color_image(modified_frog, "results/modified_frog.png")
    # im = load_color_image("test_images/tree.png")
    # print(minimum_energy_seam(im))
    # print(seam_carving(im, 1)[0])
    # save_color_image(seam_carving(load_color_image("test_images/pattern.png"), 1), "results/pattern_1seam.png")
    #save_color_image(seam_carving(load_color_image("test_images/twocats.png"), 100), "results/twocats_100seam.png")
    
    save_greyscale_image(outline("test_images/construct.png", 150), "results/construct_outline.png")
    # save_greyscale_image(outline("test_images/engine.png", 170), "results/engine_outline.png")
    # save_color_image(blueprint("test_images/engine.png", 150), "results/engine_blueprint.png")
    # save_color_image(edge_enhancement("test_images/construct.png", 100), "results/construct_edges_enhanced.png")
    # save_color_image(edge_enhancement("test_images/frog.png", 130), "results/frog_edges_enhanced.png")