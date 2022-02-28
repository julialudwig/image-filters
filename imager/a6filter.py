"""
Image processing methods for the imager application.

This module provides all of the image processing operations that are called
whenever you press a button. Some of these are provided for you and others you
are expected to write on your own.

Note that this class is a subclass of Editor. This allows you to make use
of the undo functionality. You do not have to do anything special to take
advantage of this.  Just make sure you use getCurrent() to access the most
recent version of the image.

Based on an original file by Dexter Kozen (dck10) and Walker White (wmw2)

Julia Ludwig (jal545)
11/14/20
"""
import a6editor
import math # Just in case


class Filter(a6editor.Editor):
    """
    A class that contains a collection of image processing methods

    This class is a subclass of a6editor. That means it inherits all of the
    methods and attributes of that class too. We do that (1) to put all of the
    image processing methods in one easy to read place and (2) because we might
    want to change how we implement the undo functionality later.

    This class is broken into three parts (1) implemented non-hidden methods,
    (2) non-implemented non-hidden methods and (3) hidden methods. The
    non-hidden methods each correspond to a button press in the main
    application.  The hidden methods are all helper functions.

    Each one of the non-hidden functions should edit the most recent image
    in the edit history (which is inherited from Editor).
    """

    # PROVIDED ACTIONS (STUDY THESE)
    def invert(self):
        """
        Inverts the current image, replacing each element with its color complement
        """
        current = self.getCurrent()
        for pos in range(len(current)): # We can do this because of __len__
            rgb = current[pos]          # We can do this because of __getitem__
            red   = 255 - rgb[0]
            green = 255 - rgb[1]
            blue  = 255 - rgb[2]
            rgb = (red,green,blue)      # New pixel value
            current[pos] = rgb          # We can do this because of __setitem__

    def transpose(self):
        """
        Transposes the current image

        Transposing is tricky, as it is hard to remember which values have been
        changed and which have not.  To simplify the process, we copy the
        current image and use that as a reference.  So we change the current
        image with setPixel, but read (with getPixel) from the copy.
        """
        current  = self.getCurrent()
        original = current.copy()
        current.setWidth(current.getHeight())

        for row in range(current.getHeight()):      # Loop over the rows
            for col in range(current.getWidth()):   # Loop over the columnns
                current.setPixel(row,col,original.getPixel(col,row))

    def reflectHori(self):
        """
        Reflects the current image around the horizontal middle.
        """
        current = self.getCurrent()
        for h in range(current.getWidth()//2):      # Loop over the columnns
            for row in range(current.getHeight()):  # Loop over the rows
                k = current.getWidth()-1-h
                current.swapPixels(row,h,row,k)

    def rotateRight(self):
        """
        Rotates the current image right by 90 degrees.

        Technically, we can implement this via a transpose followed by a
        horizontal reflection. However, this is slow, so we use the faster
        strategy below.
        """
        current  = self.getCurrent()
        original = current.copy()
        current.setWidth(current.getHeight())

        for row in range(current.getHeight()):      # Loop over the rows
            for col in range(current.getWidth()):   # Loop over the columnns
                current.setPixel(row,col,original.getPixel(original.getHeight()-col-1,row))

    def rotateLeft(self):
        """
        Rotates the current image left by 90 degrees.

        Technically, we can implement this via a transpose followed by a
        vertical reflection. However, this is slow, so we use the faster
        strategy below.
        """
        current  = self.getCurrent()
        original = current.copy()
        current.setWidth(current.getHeight())

        for row in range(current.getHeight()):      # Loop over the rows
            for col in range(current.getWidth()):   # Loop over the columnns
                current.setPixel(row,col,original.getPixel(col,original.getWidth()-row-1))

    # ASSIGNMENT METHODS (IMPLEMENT THESE)
    def reflectVert(self):
        """
        Reflects the current image around the vertical middle.
        """
        current = self.getCurrent()
        for col in range(current.getWidth()):
            for row in range(current.getHeight()//2):
                row_to_swap = current.getHeight()-1-row
                current.swapPixels(row,col,row_to_swap,col)

    def monochromify(self, sepia):
        """
        Converts the current image to monochrome (greyscale or sepia tone).

        If `sepia` is False, then this function uses greyscale. It removes all
        color from the image by setting the three color components of each
        pixel to that pixel's overall brightness, defined as

            brightness = 0.3 * red + 0.6 * green + 0.1 * blue.

        If sepia is True, it makes the same computations as before but sets
        green to 0.6 * brightness and blue to 0.4 * brightness (red is same as
        for greyscale).

        Parameter sepia: Whether to use sepia tone instead of greyscale.
        Precondition: sepia is a bool
        """
        assert type(sepia)==bool, repr(sepia)+' is not a bool.'

        current=self.getCurrent()
        if not sepia:
            for x in range(len(current)):
                brightness=0.3*current[x][0]+0.6*current[x][1]+0.1*current[x][2]
                current[x]=(int(brightness),int(brightness),int(brightness))
        else:
            for x in range(len(current)):
                brightness=0.3*current[x][0]+0.6*current[x][1]+0.1*current[x][2]
                current[x]=(
                int(brightness),int(0.6*brightness),int(0.4*brightness))

    def jail(self):
        """
        Puts jail bars on the current image

        The jail should be built as follows:
        * Put 3-pixel-wide horizontal bars across top and bottom,
        * Put 4-pixel vertical bars down left and right, and
        * Put n 4-pixel vertical bars inside, where n is
          (number of columns - 8) // 50.

        Note that the formula for the number of interior bars is explicitly
        not counting the two bars on the outside.

        The n+2 vertical bars should be as evenly spaced as possible.
        """
        pixel = (255,0,0)
        current = self.getCurrent()

        self._drawHBar(0,pixel)
        self._drawHBar(current.getHeight()-3,pixel)

        n=(current.getWidth()-8)//50
        space=(current.getWidth()-(4*(n+2)))/(n+1)

        col=0
        for x in range(n+2):
            self._drawVBar(int(col),pixel)
            col = col + 4 + space

    def vignette(self):
        """
        Modifies the current image to simulates vignetting (corner darkening).

        Vignetting is a characteristic of antique lenses. This plus sepia tone
        helps give a photo an antique feel.

        To vignette, darken each pixel in the image by the factor

            1 - (d / hfD)^2

        where d is the distance from the pixel to the center of the image and
        hfD (for half diagonal) is the distance from the center of the image
        to any of the corners.

        The values d and hfD should be left as floats and not converted to ints.
        Furthermore, when the final color value is calculated for each pixel,
        the result should be converted to int, but not rounded.
        """
        current=self.getCurrent()
        hfD=0.5*math.sqrt((current.getWidth()**2+current.getHeight()**2))

        for row in range(current.getHeight()):
            for col in range(current.getWidth()):
                d = math.sqrt(
                (row-current.getHeight()/2)**2+(col-current.getWidth()/2)**2)
                v=1 - (d / hfD)**2
                pixel=current.getPixel(row,col)
                red=pixel[0]
                green=pixel[1]
                blue=pixel[2]
                new_red=v*red
                new_green=v*green
                new_blue=v*blue
                new_pixel=(int(new_red),int(new_green),int(new_blue))
                current.setPixel(row,col,new_pixel)

    def pixellate(self,step):
        """
        Pixellates the current image to give it a blocky feel.

        To pixellate an image, start with the top left corner (e.g. the first
        row and column).  Average the colors of the step x step block to the
        right and down from this corner (if there are less than step rows or
        step columns, go to the edge of the image). Then assign that average
        to ALL of the pixels in that block.

        When you are done, skip over step rows and step columns to go to the
        next corner pixel.  Repeat this process again.  The result will be a
        pixellated image.

        When the final color value is calculated for each pixel, the result
        should be converted to int, but not rounded.

        Parameter step: The number of pixels in a pixellated block
        Precondition: step is an int > 0
        """
        assert type(step)==int, repr(step)+' is not an int.'
        assert step>0, repr(step)+' is not > 0.'

        current=self.getCurrent()
        num_x_blocks=math.ceil(current.getWidth()/step)
        num_y_blocks=math.ceil(current.getHeight()/step)
        for x_block in range(num_x_blocks):
            for y_block in range(num_y_blocks):
                red=0
                green=0
                blue=0
                pixels=0
                for x in range(step):
                    for y in range(step):
                        x_location=x+x_block*step
                        y_location=y+y_block*step
                        if x_location < current.getWidth() and
                        \y_location < current.getHeight():
                            pixel=current.getPixel(y_location,x_location)
                            red+=pixel[0]
                            green+=pixel[1]
                            blue+=pixel[2]
                            pixels+=1
                red=red//pixels
                green=green//pixels
                blue=blue//pixels
                avg_pixel=(red,green,blue)
                for x in range(step):
                    for y in range(step):
                        x_location=x+x_block*step
                        y_location=y+y_block*step
                        if x_location < current.getWidth() and \
                        y_location < current.getHeight():
                            current.setPixel(y_location,x_location,avg_pixel)


    # HELPER METHODS
    def _drawHBar(self, row, pixel):
        """
        Draws a horizontal bar on the current image at the given row.

        This method draws a horizontal 3-pixel-wide bar at the given row
        of the current image. This means that the bar includes the pixels
        row, row+1, and row+2. The bar uses the color given by the pixel
        value.

        Parameter row: The start of the row to draw the bar
        Precondition: row is an int, 0 <= row  &&  row+2 < image height

        Parameter pixel: The pixel color to use
        Precondition: pixel is a 3-element tuple (r,g,b) of ints in 0..255
        """
        current = self.getCurrent()
        for col in range(current.getWidth()):
            current.setPixel(row,   col, pixel)
            current.setPixel(row+1, col, pixel)
            current.setPixel(row+2, col, pixel)

    def _drawVBar(self, col, pixel):
        """
        Draws a vertical bar on the current image at the given row.

        This method draws a vertical 4-pixel-wide bar at the given col
        of the current image. This means that the bar includes the pixels
        col, col+1, and col+2. The bar uses the color given by the pixel
        value.

        Parameter col: The start of the col to draw the bar
        Precondition: col is an int, 0 <= col  &&  col+3 < image width

        Parameter pixel: The pixel color to use
        Precondition: pixel is a 3-element tuple (r,g,b) of ints in 0..255
        """
        current = self.getCurrent()
        for row in range(current.getHeight()):
            current.setPixel(row, col, pixel)
            current.setPixel(row, col+1, pixel)
            current.setPixel(row, col+2, pixel)
            current.setPixel(row, col+3, pixel)
