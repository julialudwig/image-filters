"""
GUI support widgets for the imager application

The GUI for this application is quite complex, with dialog boxes, text input, 
menus and the like. To simplify the code, we pulled a lot of smaller features
out into its own file.

Based on an original file by Dexter Kozen (dck10) and Walker White (wmw2)

Author: Walker M. White (wmw2)
Date:   October 29, 2019
"""
# These are the kivy parent classes
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.graphics.texture import Texture
from kivy.metrics import sp

from kivy.properties import *

from array import array             # Byte buffers
from io import StringIO             # Making complex strings
import traceback


# DIALOGS
class LoadDialog(BoxLayout):
    """
    A controller for a LoadDialog, a pop-up dialog to load a file.
    
    The View for this controller is defined in interface.kv. This class simply 
    contains the hooks for the view properties
    """
    # These fields are 'hooks' to connect to the interface.kv file
    # The point-and-click file navigator
    filechooser = ObjectProperty(None)
    # The text box (for the file name)
    textinput   = ObjectProperty(None)
    # The load button
    loadchoice  = ObjectProperty(None)
    # The cancel button
    exitchoice  = ObjectProperty(None)


class SaveDialog(BoxLayout):
    """
    A controller for a SaveDialog, a pop-up dialog to save a file.
    
    The View for this controller is defined in interface.kv. This class simply 
    contains the hooks for the view properties
    """
    # These fields are 'hooks' to connect to the interface.kv file
    # The point-and-click file navigator
    filechooser = ObjectProperty(None)
    # The text box (for the file name)
    textinput   = ObjectProperty(None)
    # The save button
    savechoice  = ObjectProperty(None)
    # The cancel button
    exitchoice  = ObjectProperty(None)


class ErrorDialog(BoxLayout):
    """
    A controller for an ErrorDialog, a pop-up to notify the user of an error.
    
    The View for this controller is defined in interface.kv. This class simply 
    contains the hooks for the view properties
    """
    # These fields are 'hooks' to connect to the interface.kv file
    # The error message
    message  = StringProperty('')
    # A confirmation button
    okchoice = ObjectProperty(None)


class WarningDialog(BoxLayout):
    """
    A controller for a WarningDialog, a pop-up dialog to warn the user.
    
    It differs from ErrorDialog in that it may be nested inside of another 
    pop-up dialog. The warning can be dismissed and ignored.
    
    The View for this controller is defined in interface.kv. This class simply 
    contains the hooks for the view properties
    """
    # These fields are 'hooks' to connect to the interface.kv file
    # The error message
    message = StringProperty('')
    # The data that caused the problem.
    payload = StringProperty('')
    # A confirmation button (to ignore the warning).
    okchoice   = ObjectProperty(None)
    # The cancel button
    exitchoice = ObjectProperty(None)


# MENUS
class MenuDropDown(DropDown):
    """
    The parent class for all drop-down menus.
    
    This class contains unified logic for all of the drop-down menus in this 
    application. This includes the code for opening and closing the menu.
    """
    # These fields are 'hooks' to connect to the interface.kv file
    # The possible choices from the drop down menu
    options = DictProperty({})
    # The size of the drop down menu (set dynamically)
    rowspan = NumericProperty(0)
    
    def __init__(self,**keywords):
        """
        Initializes a new drop-down menu
        
        Drop-down menus take the same keywords as other widgets.  However, 
        they have an important additional keyword: choices. This lists the 
        possible valid responses of this drop-down menu.
        
        In addition, each element of 'choices' is also a valid keyword of 
        this drop-down menu. This specifies the call function as a tuple.  
        The first element stores the function, while the remaining elements 
        are the arguments.
        
        Parameter keyword: The Kivy (and drop-down menu) keyword arguments
        Precondition: keyword is a dictionary with string keys
        """
        if 'choices' in keywords:
            for choice in keywords['choices']:
                if choice in keywords:
                    self.options[choice] = keywords[choice]
                    del keywords[choice] # Gobble
            del keywords['choices'] # Gobble
        super().__init__(**keywords)
        self.bind(on_select=self.dochoice)
    
    def dochoice(self,instance,value):
        """
        Performs a call-back (provided one exists) for the selected item.
        
        The extra parameter instance is an artifact of how Kivy does things.  
        It is not used at all since it is the same as self. 
        
        Parameter instance: A reference to this object
        Precondition: instance is the same as self
        
        Parameter value: The menu option chosen
        Precondition: value is a string
        """
        if value in self.options:
            callback = self.options[value]
            func = callback[0]
            func(*callback[1:])
    
    def open(self,widget):
        """
        Opens this drop-down, making the provided widget its parent.
        
        The drop-down will be arranged vertically, either up or down, 
        depending on the parent.
        
        Parameter widget: The parent widget to open the drop-down
        Precondition: widget is a Kivy Widget
        """
        self.rowspan = widget.height
        super().open(widget)


class ImageDropDown(MenuDropDown):
    """
    A controller for the Image drop-down, with options for image loading and edits
    
    The View for this controller is defined in interface.kv. This class simply 
    contains the hooks for the view properties
    """
    # These fields are 'hooks' to connect to the interface.kv file
    # Load an image
    loadchoice = ObjectProperty(None)
    # Save an image
    savechoice = ObjectProperty(None)
    # Undo one edit step
    undochoice  = ObjectProperty(None)
    # Undo all edits
    clearchoice = ObjectProperty(None)


class TextDropDown(MenuDropDown):
    """
    A controller for the Test drop-down, with options for text encoding/decoding.
    
    The View for this controller is defined in interface.kv. This class simply 
    contains the hooks for the view properties
    """
    # These fields are 'hooks' to connect to the interface.kv file
    # Show the text panel
    showchoice = ObjectProperty(None)
    # Hide the text panel
    hidechoice = ObjectProperty(None)
    # Encode the text
    codechoice = ObjectProperty(None)
    # Load a text file
    loadchoice = ObjectProperty(None)
    # Save a text file
    savechoice = ObjectProperty(None)
    
    def disable(self,flag):
        """
        Disables or enables the text editting functionality.
        
        Text editting is only possible when the text panel is visible.
        
        Parameter flag: Whether to disable the editting functionality.
        Precondition: flag is a boolean
        """
        self.codechoice.disabled = flag
        self.loadchoice.disabled = flag
        self.savechoice.disabled = flag
     

class AxisDropDown(MenuDropDown):
    """
    A controller for anReflect drop-down, with a choice between image axes.
    
    The View for this controller is defined in interface.kv. This class simply 
    contains the hooks for the view properties
    """
    # These fields are 'hooks' to connect to the interface.kv file
    # Flip horizontally
    horichoice = ObjectProperty(None)
    # Flip vertically
    vertchoice = ObjectProperty(None)


class TurnDropDown(MenuDropDown):
    """
    A controller for a Rotate drop-down, with a choice of left or right
    
    The View for this controller is defined in interface.kv. This class simply 
    contains the hooks for the view properties
    """
    # These fields are 'hooks' to connect to the interface.kv file
    # Rotate left
    leftchoice = ObjectProperty(None)
    # Rotate right
    rghtchoice = ObjectProperty(None)
    # Transpose
    tranchoice = ObjectProperty(None)


class GreyDropDown(MenuDropDown):
    """
    A controller for a Mono drop-down, with a choice of monochromatic styles
    
    The View for this controller is defined in interface.kv. This class simply 
    contains the hooks for the view properties
    """
    # These fields are 'hooks' to connect to the interface.kv file
    # Make it traditional greyscale
    greychoice  = ObjectProperty(None)
    # Make it sepia tone
    sepiachoice = ObjectProperty(None)


class BlockDropDown(MenuDropDown):
    """
    A controller for a Pixellate drop-down, with options for the block size
    
    The View for this controller is defined in interface.kv. This class simply 
    contains the hooks for the view properties
    """
    # These fields are 'hooks' to connect to the interface.kv file
    # 10 pixel block
    choice10 = ObjectProperty(None)
    # 20 pixel block
    choice20 = ObjectProperty(None)
    # 50 pixel block
    choice50 = ObjectProperty(None)
    # 100 pixel block
    choice100 = ObjectProperty(None)
    # 200 pixel block
    choice200 = ObjectProperty(None)


# PANELS
class ImagePanel(Widget):
    """
    A controller for an ImagePanel, an widget to display an image on screen.
    
    An image panel displays an Image object for the user to see.  This GUI r
    equires that the student have completed the Image class.  However, it does 
    not require that the student have completed anything else.
    
    The view for this application is defined the interface.kv file. This class 
    simply contains the hooks for the view properties.  In addition, it has 
    several helpful methods for image processing.
    """
    # These fields are 'hooks' to connect to the imager.kv file
    # The image, represented as an Image object
    picture = ObjectProperty(None,allownone=True)
    # The image, represented as a Texture object
    texture = ObjectProperty(None,allownone=True)
    # The "interior" dimensions of this panel (ignoring the border)
    inside   = ListProperty((0,0))
    # The display size of the current image
    imagesize = ListProperty((0,0))
    # The position offset of the current image
    imageoff  = ListProperty((0,0))
    
    @classmethod
    def getResource(self,filename):
        """
        Returns the absolute pathname for a file stored in the imager folder.
        
        This is a class method that allows all objects of this class to load 
        any image file stored in the imager folder.  Without it, we have to 
        specify the full path to the file (which may vary depending on your 
        installation).
        
        Parameter filename: The relative name of the file
        Precondition: filename is a string
        """
        import os.path
        dir = os.path.split(__file__)[0]
        return os.path.join(dir,filename)
    
    def blit(self,picture):
        for pos in range(len(picture)):
            pixel = picture[pos]
            self._blitter[pos*3  ] = pixel[0]
            self._blitter[pos*3+1] = pixel[1]
            self._blitter[pos*3+2] = pixel[2]
        return self._blitter
    
    def setImage(self,picture):
        """
        Returns True if the image panel successfully displayed picture
        
        This method sets the given picture to be the image of this panel, 
        and returns True if it is successful.  If it fails, the texture is 
        erased and the method returns false.
        
        Parameter picture: The image to display
        Precondition: picture is an Image object or None
        """
        import a6image
        
        self.picture = None
        self.texture = None
        self.imagesize = self.inside
        self.imageoff[0] = (self.size[0]-self.imagesize[0])//2
        self.imageoff[1] = (self.size[1]-self.imagesize[1])//2
        if picture is None:
            return False
        
        try:
            self.picture  = picture
            self.texture  = Texture.create(size=(picture.getWidth(), picture.getHeight()), 
                                           colorfmt='rgb', bufferfmt='ubyte')
            self._blitter = array('B',[0]*len(picture)*3)
            self.texture.blit_buffer(self.blit(picture), colorfmt='rgb', bufferfmt='ubyte')
            self.texture.flip_vertical()
            
            if self.texture.width < self.texture.height:
                self.imagesize[0] = int(self.inside[0]*(self.texture.width/self.texture.height))
                self.imagesize[1] = self.inside[1]
            elif self.texture.width > self.texture.height:
                self.imagesize[0] = self.inside[0]
                self.imagesize[1] = int(self.inside[1]*(self.texture.height/self.texture.width))
            else:
                self.imagesize = self.inside
        
            self.imageoff[0] = (self.size[0]-self.imagesize[0])//2
            self.imageoff[1] = (self.size[1]-self.imagesize[1])//2
            return True
        except:
            traceback.print_exc()
            return False
    
    def update(self,picture):
        """
        Returns True if the image panel successfully displayed picture
        
        This method is slightly faster than setImage in the case where the 
        picture is a (dimension-preserving) modification of the current one.  
        Otherwise it calls setImage.
        
        Parameter picture: The image to display
        Precondition: picture is an Image object or None
        """
        try:
            assert picture.getWidth() == self.texture.width
            self.picture = picture
            self.texture.blit_buffer(self.blit(picture), colorfmt='rgb', bufferfmt='ubyte')
            return True
        except:
            pass
        print('REMAKING')
        return self.setImage(picture)
    
    def hide_widget(self, dohide=True):
        """
        Hides or shows this widget on screen.
        
        This method is what allows us to have one panel "behind" another, 
        moving it to the front or the back.
        
        Parameter dohide: Whether to hide or show the widget
        Precondition: dohide is a boolean (default True)
        """
        if hasattr(self, 'saved_attrs'):
            if not dohide:
                self.height, self.size_hint_y, self.opacity, self.disabled = self.saved_attrs
                del self.saved_attrs
        elif dohide:
            self.saved_attrs = self.height, self.size_hint_y, self.opacity, self.disabled
            self.height, self.size_hint_y, self.opacity, self.disabled = 0, None, 0, True


class MessagePanel(Widget):
    """
    A controller for a MessagePanel, an widget to display scrollable text.
    
    An message panel displays the hidden message for the steganography part of 
    the assignment. It does not require any student code to function.
    
    The View for this controller is defined in interface.kv. This class simply 
    contains the hooks for the view properties
    """
    # These fields are 'hooks' to connect to the interface.kv file
    # The text input field
    hidden = ObjectProperty(None)
    # The background color
    textclr = ListProperty([1, 1, .9, 1])
    # Whether a message is currently present
    active = BooleanProperty(False)
    
    @classmethod
    def getResource(self,filename):
        """
        Returns the absolute pathname for a file stored in the imager folder.
        
        This is a class method that allows all objects of this class to load 
        any text file stored in the imager folder.  Without it, we have to 
        specify the full path to the file (which may vary depending on your 
        installation).
        
        Parameter filename: The relative name of the file
        Precondition: filename is a string
        """
        import os.path
        dir = os.path.split(__file__)[0]
        return os.path.join(dir,filename)
    
    def select(self,flag):
        """
        Changes the background color to notify of uncommitted changes
        
        Parameter flag: True if there are uncommitted changes
        Precondition: flag is a boolean
        """
        self.active = True
        if flag:
            self.textclr = [.9, .9,  1,  1]
        else:
            self.textclr = [  1, 1, .9,  1]
    
    def hide_widget(self, dohide=True):
        """
        Hides or shows this widget on screen.
        
        This method is what allows us to have one panel "behind" another, 
        moving it to the front or the back.
        
        Parameter dohide: Whether to hide or show the widget
        Precondition: dohide is a boolean (default True)
        """
        if hasattr(self, 'saved_attrs'):
            if not dohide:
                self.height, self.size_hint_y, self.opacity, self.disabled = self.saved_attrs
                del self.saved_attrs
        elif dohide:
            self.saved_attrs = self.height, self.size_hint_y, self.opacity, self.disabled
            self.height, self.size_hint_y, self.opacity, self.disabled = 0, None, 0, True