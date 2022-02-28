"""
The base class for modifying an image in the imager application.

When we work with an image, we like to have an edit history. An edit history 
keeps track of all modifications of an original image.  It allows for 
(step-by-step) undos of any changes.  The class in this module provides an
edit history. The filter functions are in a subclass of this class so that 
they can take advantage of the edit history.

Based on an original file by Dexter Kozen (dck10) and Walker White (wmw2)

Author: Walker White (wmw2)
Date:   October 29, 2019
"""
# THIS FILE IS COMPLETE.  DO NOT MODIFY THIS FILE AT ALL
import a6image


class Editor(object):
    """
    A class that keeps track of edits from an original image.
    
    This class is what allows us to implement the Undo functionality in our 
    application. It separates the image into the original (saved) image and 
    the current modification. It also keeps track of all edits in-between
    (up to a maximum of MAX_HISTORY edits) in order. It can undo any of
    these edits, rolling the current image back.
    
    If the number of edits exceeds MAX_HISTORY, the oldest edit will be
    deleted.  
    
    Attribute MAX_HISTORY: A CLASS ATTRIBUTE for the maximum number of edits
    Invariant: MAX_HISTORY is an int > 0
    """
    # IMMUTABLE ATTRIBUTES (Fixed after initialization)
    # Attribute _original: The original image 
    # Invariant: _original is an Image object
    #
    # Attribute _history: The edit history
    # Invariant: _history is a non-empty list of Image objects. In addition, 
    #the length of _history should never be longer than MAX_HISTORY.
    
    # The number of edits that we are allowed to keep track of.
    # (THIS GOES IN CLASS FOLDER)
    MAX_HISTORY = 20
    
    # GETTERS
    def getOriginal(self):
        """
        Returns the original image
        """
        return self._original
    
    def getCurrent(self):
        """
        Returns the most recent edit
        """
        return self._history[-1]
    
    # INITIALIZER
    def __init__(self,original):
        """
        Initializes an edit history for the given image.
        
        The edit history starts with exactly one element, which is an 
        (uneditted) copy of the original image.
        
        Parameter original: The image to edit
        Precondition: original is an Image object
        """
        assert isinstance(original,a6image.Image), repr(original)+' is not an image'
        self._original = original
        self._history  = [original.copy()]
    
    # EDIT METHODS
    def undo(self):
        """
        Returns True if the latest edit can be undone, False otherwise.
        
        This method attempts to undo the latest element by removing the last 
        element of the edit history.  However, the edit history can never
        be empty.  If this method is called on an edit history of one element,
        this method returns False instead.
        """
        if len(self._history) > 1:
            self._history.pop()
            return True
        return False
    
    def clear(self):
        """
        Deletes the entire edit history, retoring the original image.
        
        When this method completes, the object should have the same values that 
        it did once it was first initialized.
        """
        self._history = [self._original.copy()]
    
    def increment(self):
        """
        Adds a new copy of the image to the edit history.
        
        This method copies the current most recent edit and adds it to the 
        end of the history.  If this causes the history to grow to larger 
        (greater than MAX_HISTORY), this method deletes the oldest edit.
        """
        self._history.append(self.getCurrent().copy())
        if len(self._history) > self.MAX_HISTORY:
            self._history.pop(0)

