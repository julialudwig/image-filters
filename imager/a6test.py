"""
Test script for Assignment 6.

You cannot even start to process images until the class Image is complete. Many of
test procedures will make sure that this class is working properly.

This script also contains test procedures for Filter and Encoder.  However, these
test procedures are sparse and are not guaranteed to find everything.

Author: Walker M. White (wmw2)
Date:   October 29, 2019
"""
import introcs
import a6image
import a6filter
import traceback

# Helper to read the test images

def load_image(file):
    """
    Returns an Image object for the give file in the tests folder.

    If it cannot read the image (either Image is not defined or the file
    is not an image file), this method returns None.

    Parameter file: The image file (without the png suffix)
    Precondition: file is a string
    """
    import os.path
    from PIL import Image as CoreImage
    path = os.path.split(__file__)[0]
    path = os.path.join(path,'tests',file+'.png')

    try:
        image = CoreImage.open(path)
        image = image.convert("RGB")
        buffer = list(image.getdata())
        size  = image.size[0]*image.size[1]
        width = image.size[0]
    except:
        traceback.print_exc()
        print('Could not load the file '+path)
        buffer = None

    result = None
    if not buffer is None:
        try:
            result = a6image.Image(buffer,width)
        except:
            traceback.print_exc()
            result = None
    return result


def load_text(file):
    """
    Returns an text string for the give file in the tests folder.

    If it cannot read the text, this method returns None.

    Parameter file: The text file (without the txt suffix)
    Precondition: file is a string
    """
    import os.path
    from PIL import Image as CoreImage
    path = os.path.split(__file__)[0]
    path = os.path.join(path,'tests',file+'.txt')

    try:
        data = open(path)
        result = data.read()
        data.close()
    except:
        traceback.print_exc()
        self.error('Could not load the text file')
        result = None

    return result


# Test functions
def test_pixel_list():
    """
    Tests the precondition helper _is_pixel_list
    """
    print('Testing helper _is_pixel_list')
    introcs.assert_false(a6image._is_pixel_list('a'))
    introcs.assert_false(a6image._is_pixel_list((0,244,255)))
    introcs.assert_false(a6image._is_pixel_list(['a']))
    introcs.assert_true(a6image._is_pixel_list([(0,244,255)]))
    introcs.assert_false(a6image._is_pixel_list([[(0,244,255)]]))
    introcs.assert_false(a6image._is_pixel_list([(304,244,255)]))
    introcs.assert_true(a6image._is_pixel_list([(0,244,255),(100,64,255),(50,3,250)]))
    introcs.assert_false(a6image._is_pixel_list([(0,244,255),(100,'64',255),(50,3,250)]))
    introcs.assert_false(a6image._is_pixel_list([(0,244,255),(100,-64,255),(50,3,250)]))


def test_image_init():
    """
    Tests the __init__ method and getters for class Image
    """
    print('Testing image initializer')
    p = [(0,0,0)]*6

    image = a6image.Image(p,3)
    # Normally it is bad to test things that are hidden
    # But without this you will not find the error until test_image_operators
    introcs.assert_equals(id(p),id(image._data))
    introcs.assert_not_equals(id(p),id(image.getData()))
    introcs.assert_equals(p,image.getData())
    introcs.assert_equals(3,image.getWidth())
    introcs.assert_equals(2,image.getHeight())

    image = a6image.Image(p,2)
    introcs.assert_equals(id(p),id(image._data))
    introcs.assert_not_equals(id(p),id(image.getData()))
    introcs.assert_equals(p,image.getData())
    introcs.assert_equals(2,image.getWidth())
    introcs.assert_equals(3,image.getHeight())

    image = a6image.Image(p,1)
    introcs.assert_equals(id(p),id(image._data))
    introcs.assert_not_equals(id(p),id(image.getData()))
    introcs.assert_equals(p,image.getData())
    introcs.assert_equals(1,image.getWidth())
    introcs.assert_equals(6,image.getHeight())

    # Test enforcement
    introcs.assert_error(a6image.Image,'aaa',3,message='Image does not enforce the precondition on data')
    introcs.assert_error(a6image.Image,p,'a',  message='Image does not enforce the precondition width type')
    introcs.assert_error(a6image.Image,p,5,    message='Image does not enforce the precondition width validity')


def test_image_setters():
    """
    Tests the width and height setters for class Image
    """
    print('Testing image setters for width/height')
    p = [(0,0,0)]*6

    image = a6image.Image(p,3)
    introcs.assert_equals(3,image.getWidth())
    introcs.assert_equals(2,image.getHeight())

    image.setWidth(2)
    introcs.assert_equals(2,image.getWidth())
    introcs.assert_equals(3,image.getHeight())

    image.setHeight(1)
    introcs.assert_equals(6,image.getWidth())
    introcs.assert_equals(1,image.getHeight())

    image.setWidth(1)
    introcs.assert_equals(1,image.getWidth())
    introcs.assert_equals(6,image.getHeight())

    # Test enforcement
    introcs.assert_error(image.setWidth,'a', message='setWidth does not enforce the precondition on width type')
    introcs.assert_error(image.setWidth,5,   message='setWidth does not enforce the precondition on width validity')
    introcs.assert_error(image.setHeight,'a',message='setHeight does not enforce the precondition on height type')
    introcs.assert_error(image.setHeight,5,  message='setHeight does not enforce the precondition on height validity')


def test_image_operators():
    """
    Tests the double-underscore methods for 1-d access in class Image.
    """
    print('Testing image operators for 1-dimensional access')
    p = [(0,0,0)]*4

    image = a6image.Image(p,2)
    introcs.assert_equals(4,len(image))

    p = [(255,0,0),(0,255,0),(0,0,255),(0,255,255),(255,0,255),(255,255,0)]
    rgb1 = (255,255,255)
    rgb2 = (64,128,192)

    image = a6image.Image(p,3)
    introcs.assert_equals(6,len(image))
    for n in range(6):
        introcs.assert_equals(p[n],image[n])
        introcs.assert_equals(id(p[n]),id(image[n]))

    image[4] = rgb1
    introcs.assert_equals(rgb1,image[4])
    image[4] = rgb2
    introcs.assert_equals(rgb2,image[4])
    introcs.assert_equals(rgb2,p[4])                # Because image has a reference to p

    introcs.assert_error(image.__getitem__,'a', message='__getitem__ does not enforce the precondition on type')
    introcs.assert_error(image.__getitem__,9,   message='__getitem__ does not enforce the precondition on range')
    introcs.assert_error(image.__setitem__,'a',(0,0,255), message='__setitem__ does not enforce the precondition on type')
    introcs.assert_error(image.__setitem__,9,(0,0,255),   message='__setitem__ does not enforce the precondition on range')
    introcs.assert_error(image.__setitem__,9,(0,0,'255'), message='__setitem__ does not enforce the precondition on pixel value')


def test_image_access():
    """
    Tests the methods the two-dimensional get/setPixel methods in class Image
    """
    print('Testing image get/setPixel methods')
    p = [(255,0,0),(0,255,0),(0,0,255),(0,255,255),(255,0,255),(255,255,0)]
    rgb1 = (255,255,255)
    rgb2 = (64,128,192)

    image = a6image.Image(p,2)
    for n in range(6):
        introcs.assert_equals(p[n],image.getPixel(n // 2, n % 2))
        introcs.assert_equals(id(p[n]),id(image.getPixel(n // 2, n % 2)))

    image.setPixel(2,1,rgb1)
    introcs.assert_equals(rgb1,image.getPixel(2,1))

    image.setPixel(2,1,rgb2)
    introcs.assert_equals(rgb2,image.getPixel(2,1))

    # Test enforcement
    introcs.assert_error(image.getPixel, 'a', 1, message='getPixel does not enforce the precondition on row type')
    introcs.assert_error(image.getPixel, 8, 1,   message='getPixel does not enforce the precondition on row value')
    introcs.assert_error(image.getPixel, 2, 'a', message='getPixel does not enforce the precondition on col value')
    introcs.assert_error(image.getPixel, 2, 8,   message='getPixel does not enforce the precondition on col value')
    introcs.assert_error(image.setPixel, 'a', 1, (0,0,255), message='setPixel does not enforce the precondition on row type')
    introcs.assert_error(image.setPixel, 8, 1, (0,0,255),   message='setPixel does not enforce the precondition on row value')
    introcs.assert_error(image.setPixel, 2, 'a', (0,0,255), message='setPixel does not enforce the precondition on col value')
    introcs.assert_error(image.setPixel, 2, 8, (0,0,255),   message='setPixel does not enforce the precondition on col value')
    introcs.assert_error(image.setPixel, 2, 1, (0,0,'255'), message='setPixel does not enforce the precondition on pixel value')


def test_image_str():
    """
    Tests the __str__ method in class Image
    """
    print('Testing image __str__ method')
    p = [(255, 64, 0),(0, 255, 64),(64, 0, 255),(64, 255, 128),(128, 64, 255),(255, 128, 64)]

    str0 = '[['+str(p[0])+', '+str(p[1])+'],\n['+str(p[2])+', '+str(p[3])+']]'
    str1 = '[['+str(p[0])+', '+str(p[1])+'],\n['+str(p[2])+', '+str(p[3])+'],\n['+str(p[4])+', '+str(p[5])+']]'
    str2 = '[['+str(p[0])+', '+str(p[1])+', '+str(p[2])+'],\n['+str(p[3])+', '+str(p[4])+', '+str(p[5])+']]'
    str3 = '[['+str(p[0])+', '+str(p[1])+', '+str(p[2])+', '+str(p[3])+', '+str(p[4])+', '+str(p[5])+']]'
    str4 = '[['+str(p[0])+'],\n['+str(p[1])+'],\n['+str(p[2])+'],\n['+str(p[3])+'],\n['+str(p[4])+'],\n['+str(p[5])+']]'

    image = a6image.Image(p[:4],2)
    introcs.assert_equals(str0,str(image))

    image = a6image.Image(p,2)
    introcs.assert_equals(str1,str(image))
    image.setWidth(3)
    introcs.assert_equals(str2,str(image))
    image.setWidth(6)
    introcs.assert_equals(str3,str(image))
    image.setWidth(1)
    introcs.assert_equals(str4,str(image))


def test_image_other():
    """
    Tests the copy and swapPixel methods in class Image
    """
    print('Testing image extra methods')
    p = [(255, 64, 0),(0, 255, 64),(64, 0, 255),(64, 255, 128),(128, 64, 255),(255, 128, 64)]
    q = p[:]  # Need to copy this

    # Test the copy
    image = a6image.Image(p,2)
    copy  = image.copy()
    introcs.assert_equals(len(image),len(copy))
    introcs.assert_equals(image.getWidth(),copy.getWidth())
    introcs.assert_not_equals(id(image), id(copy))
    introcs.assert_not_equals(id(image._data), id(copy._data))
    for pos in range(len(copy)):
        introcs.assert_equals(image[pos],copy[pos])

    # Test swap pixels
    image.swapPixels(0,0,2,1)
    introcs.assert_equals(q[5],image.getPixel(0,0))
    introcs.assert_equals(q[0],image.getPixel(2,1))
    image.swapPixels(0,0,2,1)
    introcs.assert_equals(q[0],image.getPixel(0,0))
    introcs.assert_equals(q[5],image.getPixel(2,1))
    image.swapPixels(0,1,2,0)
    introcs.assert_equals(q[4],image.getPixel(0,1))
    introcs.assert_equals(q[1],image.getPixel(2,0))
    image.swapPixels(0,1,2,0)
    introcs.assert_equals(q[1],image.getPixel(0,1))
    introcs.assert_equals(q[4],image.getPixel(2,0))
    image.swapPixels(0,0,0,0)
    introcs.assert_equals(q[0],image.getPixel(0,0))

    # Test enforcement
    introcs.assert_error(image.swapPixels, 'a', 1, 0, 0, message='swapPixels does not enforce the precondition on row type')
    introcs.assert_error(image.swapPixels, 8, 1, 0, 0,   message='swapPixels does not enforce the precondition on row value')
    introcs.assert_error(image.swapPixels, 0, 1, 'a', 0, message='swapPixels does not enforce the precondition on row type')
    introcs.assert_error(image.swapPixels, 0, 1, 8, 0,   message='swapPixels does not enforce the precondition on row value')
    introcs.assert_error(image.swapPixels, 0, 'a', 0, 0, message='swapPixels does not enforce the precondition on column type')
    introcs.assert_error(image.swapPixels, 0, 8, 0, 0,   message='swapPixels does not enforce the precondition on column value')
    introcs.assert_error(image.swapPixels, 0, 1, 0, 'a', message='swapPixels does not enforce the precondition on column type')
    introcs.assert_error(image.swapPixels, 0, 1, 0, 8,   message='swapPixels does not enforce the precondition on column value')

## All of these tests hava a familiar form

def compare_images(image1,image2,file1,file2):
    """
    Compares image1 and image2 via assert functions.

    If the images are the same, nothing happens. Otherwise this function
    produces an error and quits python.  We provide the file names to give
    use proper error messages

    Parameter image1: The first image to compare
    Precondition: image1 is an Image object

    Parameter image2: The second image to compare
    Precondition: image2 is an Image object

    Parameter file1: The file name of the first image
    Precondition: file1 is an Image object

    Parameter file2: The file name of the second image
    Precondition: file2 is an Image object
    """
    introcs.assert_equals(len(image2),len(image1),
                          file1+' and '+file2+' do not have the same pixel size')
    introcs.assert_equals(image2.getWidth(),image1.getWidth(),
                          file1+' and '+file2+' do not have the same width')
    introcs.assert_equals(image2.getHeight(),image1.getHeight(),
                          file1+' and '+file2+' do not have the same height')

    for col in range(image2.getWidth()):
        for row in range(image2.getHeight()):
            introcs.assert_equals(image2.getPixel(row,col),image1.getPixel(row,col),
                                  'Pixel mismatch between '+file1+' and '+file2+
                                  ' at ('+str(col)+','+str(row)+')')


def test_reflect_vert():
    """
    Tests the method reflectVert in class Filter
    """
    print('Testing method reflectVert')

    file1 = 'blocks'
    file2 = 'blocks-reflect-vertical'
    image1 = load_image(file1)
    image2 = load_image(file2)
    editor = a6filter.Filter(image1)

    editor.reflectVert()
    compare_images(editor.getCurrent(),image2,file1,file2)

    file1 = 'home'
    file2 = 'home-reflect-vertical'
    image1 = load_image(file1)
    image2 = load_image(file2)
    editor = a6filter.Filter(image1)

    editor.reflectVert()
    compare_images(editor.getCurrent(),image2,file1,file2)


def test_monochromify():
    """
    Tests the method monochromify in class Filter
    """
    print('Testing method monochromify (greyscale)')

    file1 = 'blocks'
    file2 = 'blocks-grey'
    image1 = load_image(file1)
    image2 = load_image(file2)
    editor = a6filter.Filter(image1)

    editor.monochromify(False)
    compare_images(editor.getCurrent(),image2,file1,file2)

    file1 = 'home'
    file2 = 'home-grey'
    image1 = load_image(file1)
    image2 = load_image(file2)
    editor = a6filter.Filter(image1)

    editor.monochromify(False)
    compare_images(editor.getCurrent(),image2,file1,file2)

    print('Testing method monochromify (sepia)')

    file1 = 'blocks'
    file2 = 'blocks-sepia'
    image1 = load_image(file1)
    image2 = load_image(file2)
    editor = a6filter.Filter(image1)

    editor.monochromify(True)
    compare_images(editor.getCurrent(),image2,file1,file2)

    file1 = 'home'
    file2 = 'home-sepia'
    image1 = load_image(file1)
    image2 = load_image(file2)
    editor = a6filter.Filter(image1)

    editor.monochromify(True)
    compare_images(editor.getCurrent(),image2,file1,file2)


def test_jail():
    """
    Tests the method jail in class Filter
    """
    print('Testing method jail')

    file1 = 'blocks'
    file2 = 'blocks-jail'
    image1 = load_image(file1)
    image2 = load_image(file2)
    editor = a6filter.Filter(image1)

    editor.jail()
    compare_images(editor.getCurrent(),image2,file1,file2)

    file1 = 'home'
    file2 = 'home-jail'
    image1 = load_image(file1)
    image2 = load_image(file2)
    editor = a6filter.Filter(image1)

    editor.jail()
    compare_images(editor.getCurrent(),image2,file1,file2)


def test_vignette():
    """
    Tests the method vignette in class Filter
    """
    print('Testing method vignette')

    file1 = 'blocks'
    file2 = 'blocks-vignette'
    image1 = load_image(file1)
    image2 = load_image(file2)
    editor = a6filter.Filter(image1)

    editor.vignette()
    compare_images(editor.getCurrent(),image2,file1,file2)

    file1 = 'home'
    file2 = 'home-vignette'
    image1 = load_image(file1)
    image2 = load_image(file2)
    editor = a6filter.Filter(image1)

    editor.vignette()
    compare_images(editor.getCurrent(),image2,file1,file2)


def test_pixellate():
    """
    Tests the method pixellate in class Filter
    """
    print('Testing method pixellate')

    file1 = 'blocks'
    file2 = 'blocks-pixellate-10'
    image1 = load_image(file1)
    image2 = load_image(file2)
    editor = a6filter.Filter(image1)

    editor.pixellate(10)
    compare_images(editor.getCurrent(),image2,file1,file2)

    file2 = 'blocks-pixellate-20'
    image1 = load_image(file1)
    image2 = load_image(file2)
    editor = a6filter.Filter(image1)

    editor.pixellate(20)
    compare_images(editor.getCurrent(),image2,file1,file2)

    file2 = 'blocks-pixellate-50'
    image1 = load_image(file1)
    image2 = load_image(file2)
    editor = a6filter.Filter(image1)

    editor.pixellate(50)
    compare_images(editor.getCurrent(),image2,file1,file2)

    file1 = 'home'
    file2 = 'home-pixellate-10'
    image1 = load_image(file1)
    image2 = load_image(file2)
    editor = a6filter.Filter(image1)

    editor.pixellate(10)
    compare_images(editor.getCurrent(),image2,file1,file2)

    file2 = 'home-pixellate-20'
    image1 = load_image(file1)
    image2 = load_image(file2)
    editor = a6filter.Filter(image1)

    editor.pixellate(20)
    compare_images(editor.getCurrent(),image2,file1,file2)

    file2 = 'home-pixellate-50'
    image1 = load_image(file1)
    image2 = load_image(file2)
    editor = a6filter.Filter(image1)

    editor.pixellate(50)
    compare_images(editor.getCurrent(),image2,file1,file2)


def test_all():
    """
    Execute all of the test cases.

    This function is called by __main__.py
    """
    test_pixel_list()
    print()

    print('Testing class Image')
    test_image_init()
    test_image_setters()
    test_image_operators()
    test_image_access()
    test_image_str()
    test_image_other()
    print('Class Image passed all tests.')
    print()

    print('Testing class Filter')
    test_reflect_vert()
    test_monochromify()
    test_jail()
    test_vignette()
    test_pixellate()
    print('Class Filter passed all tests.')
