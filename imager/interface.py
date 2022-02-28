"""
The primary GUI interface for the imager filter application

The default application corresponds to the class InterfaeApp. This class is
the root controller for each of the View components defined in interface.kv.  
The View (filter.kv) and this Controller module (filter.py) have the same name 
because they are so tightly interconnected.

Based on an original file by Dexter Kozen (dck10) and Walker White (wmw2)

Author: Walker M. White (wmw2)
Date:   October 29, 2019
"""
# We have to configure the window before everything else
from kivy.config import Config
#Config.set('kivy', 'log_level', 'error')
Config.set('graphics', 'width', '1056')
Config.set('graphics', 'height', '557')
Config.set('graphics', 'resizable', '0') # make not resizable

from kivy.clock import Clock, mainthread
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import *
from kivy.app import App
from kivy.metrics import sp

from widgets import *
import traceback

class InterfacePanel(BoxLayout):
    """
    This class is a controller for the imager filter application.
    
    This controller manages all of the buttons and text fields of the 
    application. It supports all parts of the assignment, and may be used \
    for additional (eyeball) testing beyond the provided test script
    
    The view for this application is defined the interface.kv file.
    """
    # These fields are 'hooks' to connect to the .kv file
    # The source file for the initial image
    source = StringProperty(ImagePanel.getResource('im_walker.png'))
    # The Image object for the loaded file
    picture   = ObjectProperty(None,allownone=True)
    # The workspace object for working on the file
    workspace = ObjectProperty(None,allownone=True)
    
    # The most recent file edit
    workimage = ObjectProperty(None,allownone=True)
    # The original image file (this will never change)
    origimage = ObjectProperty(None,allownone=True)
    
    # The menu bar
    menubar   = ObjectProperty(None)
    # The progress monitor
    progress  = ObjectProperty(None)
    
    # The file drop-down menu
    imagedrop = ObjectProperty(None)
    # The reflect drop-down menu
    axisdrop  = ObjectProperty(None)
    # The monochromify drop-down menu
    greydrop  = ObjectProperty(None)
    # The rotate drop-down menu
    turndrop  = ObjectProperty(None)
    # The pixellate drop-down menu
    blockdrop = ObjectProperty(None)
    
    # For handling the "progress" monitor
    processing = BooleanProperty(False)
    
    def config(self):
        """
        Configures the application at start-up.
        
        Controllers are responsible for initializing the application and creating all of 
        the other objects. This method does just that. It loads the currently selected 
        image file, and creates an editor for that file (if possible).
        """
        # For working with pop-ups (Hidden since not .kv aware)
        self._popup = None
        self.place_image('',self.source)
        self.imagedrop = ImageDropDown(choices=['load','save','undo','reset'], 
                                       save=[self.save_image], load=[self.load_image],
                                       undo=[self.undo], reset=[self.clear])
        self.axisdrop  = AxisDropDown( choices=['horizontal','vertical'],
                                       horizontal=[self.do_async,'reflectHori'], 
                                       vertical=[self.do_async,'reflectVert'])
        self.greydrop  = GreyDropDown( choices=['greyscale','sepia'],
                                       greyscale=[self.do_async,'monochromify',False], 
                                       sepia=[self.do_async,'monochromify',True])
        self.turndrop  = TurnDropDown( choices=['left','right','transpose'],
                                       left= [self.do_async,'rotateLeft'],
                                       right=[self.do_async,'rotateRight'],
                                       transpose=[self.do_async,'transpose'])
        self.blockdrop = BlockDropDown(choices=['p10','p20','p50','p100', 'p200'],
                                       p10=[self.do_async,'pixellate',10],
                                       p20=[self.do_async,'pixellate',20],
                                       p50=[self.do_async,'pixellate',50],
                                       p100=[self.do_async,'pixellate',100],
                                       p200=[self.do_async,'pixellate',200])
        self.async_action = None
        self.async_thread = None
    
    # DIALOG BOXES
    def error(self, msg):
        """
        Opens a dialog to report an error to the user
        
        The dialog will take up most of the Window, and last until the user 
        dismisses it.
        
        Parameter msg: the error message
        Precondition: msg is a string
        """
        assert type(msg) == str, repr(msg)+' is not a string'
        content = ErrorDialog(message=msg, okchoice=self.dismiss_popup)
        self._popup = Popup(title='Error', content=content, 
                            size_hint=(0.4, 0.4), 
                            pos_hint={'center_x':0.5, 'center_y':0.5})
        self._popup.open()
    
    def warn(self, msg, data=None, callback=None):
        """
        Alerts the user of an issue when trying to load or save a file
        
        The dialog will take up most of the Window, and last until the user 
        dismisses it.
        
        Parameter msg: the error message
        Precondition: msg is a string
        
        Parameter data: the problematic file
        Precondition: data is a string
        
        Parameter callback: The callback to invoke on ok
        Precondition: callback is callable
        """
        if callback:
            content = WarningDialog(message=msg, payload=data, 
                                    okchoice=callback, 
                                    exitchoice=self.dismiss_popup)
            self._popup = Popup(title='Warning', content=content, 
                                size_hint=(0.4, 0.4), 
                                pos_hint={'center_x':0.5, 'center_y':0.5})
        elif data:
            print(data)
            content = ErrorDialog(message=msg, okchoice=self.dismiss_popup)
            self._popup = Popup(title='Warning', content=content, **data)
        else:
            content = ErrorDialog(message=msg, okchoice=self.dismiss_popup)
            self._popup = Popup(title='Warning', content=content, 
                                size_hint=(0.4, 0.4), 
                                pos_hint={'center_x':0.5, 'center_y':0.5})
        self._popup.open()
    
    def load(self,title,callback, filters=None):
        """
        Opens a dialog to load a file.
        
        The dialog will take up most of the Window, and last until the user 
        dismisses it.
        
        Parameter title: The title to display
        Precondition: title is a string
        
        Parameter callback: The callback to invoke on load
        Precondition: callback is callable
        """
        content = LoadDialog(loadchoice=callback, exitchoice=self.dismiss_popup)
        if filters:
            content.filechooser.filters = filters
        self._popup = Popup(title=title, content=content,
                            size_hint=(0.8,0.9), 
                            pos_hint={'center_x':0.5, 'center_y':0.5})
        self._popup.open()

    def save(self,title,callback,filters=None):
        """
        Opens a dialog to save a file.
        
        The dialog will take up most of the Window, and last until the user 
        dismisses it.
        
        Parameter title: The title to display
        Precondition: title is a string
        
        Parameter callback: The callback to invoke on save
        Precondition: callback is callable
        """
        content = SaveDialog(savechoice=callback, exitchoice=self.dismiss_popup)
        if filters:
            content.filechooser.filters = filters
        self._popup = Popup(title=title, content=content,
                            size_hint=(0.8,0.9), 
                            pos_hint={'center_x':0.5, 'center_y':0.5})
        self._popup.open()
    
    def dismiss_popup(self):
        """
        Dismisses the currently active pop-up
        """
        if self._popup:
            self._popup.dismiss()
            self._popup = None
    
    # FILE HANDLING
    def read_image(self, file):
        """
        Returns an Image object for the give file.
        
        If it cannot read the image (either Image is not defined or the file 
        is not an image file), this method returns None.
        
        Parameter file: An absolute path to an image file
        Precondition: file is a string
        """
        import a6image
        from PIL import Image as CoreImage
        
        try:
            image = CoreImage.open(file)
            image = image.convert("RGB")
            buffer = list(image.getdata())
            size  = image.size[0]*image.size[1]
            width = image.size[0]
        except:
            traceback.print_exc()
            self.error('Could not load the image file')
            buffer = None
        
        result = None
        if not buffer is None:
            try:
                result = a6image.Image(buffer,width)
            except:
                traceback.print_exc()
                result = None
        return result
    
    def check_save_png(self, path, filename):
        """
        Saves the current image to a file, checking that the format is PNG
        
        If user uses another extension, or no extension at all, this method 
        forces the file to be a .png
        
        Parameter path: The base path to the file
        Precondition: path is a string
        
        Parameter filename: An absolute or relative filename
        Precondition: filename is a string
        """
        import os.path
        self.dismiss_popup()
        
        if os.path.isabs(filename):
            file = filename
        else:
            file = os.path.join(path,filename)
        
        if file.lower().endswith('.png'):
            self.save_png(file)
        else:
            file = os.path.splitext(file)[0]+'.png'
            msg = 'File will be saved as {} in .png format.\nProceed?'
            self.warn(msg.format(os.path.split(file)[1]), file, self.save_png)
    
    def save_png(self, filename):
        """
        Saves the current image to a file, checking first if the file exists.
        
        If the file exist, this will display a warning.
        
        Parameter filename: An absolute filename
        Precondition: filename is a string
        """
        import os.path
        assert filename.lower().endswith('.png')
        self.dismiss_popup()
        if os.path.isfile(filename):
            msg = 'File {} exists.\nOverwrite?'
            self.warn(msg.format(os.path.split(filename)[1]), filename, self.force_png)
        else:
            self.force_png(filename)
    
    def force_png(self, filename):
        """
        Saves the current image, without user confirmation.
        
        Parameter filename: An absolute filename
        Precondition: filename is a string
        """
        import os.path
        import traceback
        self.dismiss_popup()
        
        # prepare image for saving
        from PIL import Image as CoreImage

        # This worked (Unlike Kivy)!  But is slow.
        current = self.workspace.getCurrent()
        try:
            im = CoreImage.new('RGBA',(current.getWidth(),current.getHeight()))
            im.putdata(tuple(current.getData()))
            im.save(filename,'PNG')
        except:
            traceback.print_exc()
            self.error('Cannot save image file ' + os.path.split(filename)[1])
                # These fields are 'hooks' to connect to the imager.kv file
    
    def place_image(self, path, filename):
        """
        Loads the image from file and stores the result in the image panel(s)
        
        If it cannot read the image (either Image is not defined or the file 
        is not an image file), this method does nothing.
        
        Parameter path: The base path to the file
        Precondition: path is a string
        
        Parameter filename: An absolute or relative filename
        Precondition: filename is a string
        """
        import os.path
        self.dismiss_popup()
        
        if os.path.isabs(filename):
            file = filename
        else:
            file = os.path.join(path,filename)
        
        import a6filter
        self.picture = self.read_image(file)
        try:
            self.workspace = a6filter.Filter(self.picture)
            self.workimage.setImage(self.workspace.getCurrent())
            self.origimage.setImage(self.workspace.getOriginal())
        except:
            traceback.print_exc()
            self.workspace = None
            self.workimage.setImage(None)
            self.origimage.setImage(self.picture)
            quit()
        self.canvas.ask_update()
    
    def check_save_txt(self, path, filename):
        """
        Saves the current image to a file, checking that the format is TXT
        
        If user uses another extension, or no extension at all, this method 
        forces the file to be a .txt
        
        Parameter path: The base path to the file
        Precondition: path is a string
        
        Parameter filename: An absolute or relative filename
        Precondition: filename is a string
        """
        import os.path
        self.dismiss_popup()
        
        if os.path.isabs(filename):
            file = filename
        else:
            file = os.path.join(path,filename)
        
        if file.lower().endswith('.txt'):
            self.save_txt(file)
        else:
            file = os.path.splitext(file)[0]+'.txt'
            msg = 'File will be saved as {} in .txt format.\nProceed?'
            self.warn(msg.format(os.path.split(file)[1]), file, self.save_txt)
    
    def save_txt(self, filename):
        """
        Saves the current message text to a file, checking if the file exists.
        
        If the file exist, this will display a warning.
        
        Parameter filename: An absolute filename
        Precondition: filename is a string
        """
        import os.path
        assert filename.lower().endswith('.txt')
        self.dismiss_popup()
        if os.path.isfile(filename):
            msg = 'File {} exists.\nOverwrite?'
            self.warn(msg.format(os.path.split(filename)[1]), filename, self.force_txt)
        else:
            self.force_txt(filename)
    
    def force_txt(self, filename):
        """
        Saves the current message text, without user confirmation.
        
        Parameter filename: An absolute filename
        Precondition: filename is a string
        """
        import os.path
        self.dismiss_popup()
        
        # prepare image for saving
        text = self.textpanel.hidden.text
        try:
            file = open(filename,'w',encoding="utf-8")
            file.write(text)
            file.close()
        except:
            self.error('Cannot save text file ' + os.path.split(filename)[1])
    
    def place_text(self, path, filename):
        """
        Loads the text from file and stores the result in the text editor
        
        If it cannot read the text, this method does nothing.
        
        Parameter path: The base path to the file
        Precondition: path is a string
        
        Parameter filename: An absolute or relative filename
        Precondition: filename is a string
        """
        from kivy.metrics import sp
        
        import os.path
        self.dismiss_popup()
        
        if os.path.isabs(filename):
            file = filename
        else:
            file = os.path.join(path,filename)
        
        try:
            handle = open(file,encoding="utf-8")
            text = handle.read()
            handle.close()
        except:
            traceback.print_exc()
            self.error('Could not load the text file')
            text = ''
        
        height = max((text.count('\n')+1)*20*sp(1),self.textpanel.height)
        
        self.textpanel.active = True
        self.textpanel.hidden.text = text
        self.textpanel.hidden.height = height
        self.textpanel.select(True)
    
    # MENU OPERATIONS
    def load_image(self):
        """
        Opens a dialog to load an image file.
        
        The dialog will take up most of the Window, and last until the user 
        dismisses it.  Open dismissal it will read the file and display it
        in the window if successful.
        """
        self.load('Load image',self.place_image)
    
    def save_image(self):
        """
        Opens a dialog to save an image file.
        
        The dialog will take up most of the Window, and last until the user 
        dismisses it. Open dismissal it will write the current image to a file.
        """
        self.save('Save image',self.check_save_png)
    
    def undo(self):
        """
        Undos the last edit to the image.
        
        This method will undo the last edit to the image.
        """
        try:
            self.workspace.undo()
            self.workimage.update(self.workspace.getCurrent())
            self.canvas.ask_update()
        except:
            traceback.print_exc()
            self.error('An error occurred when trying to undo')
        
    def clear(self):
        """
        Clears all edits to the image.
        
        This method will remove all edits to the image.
        """
        try:
            self.workspace.clear()
            self.workimage.update(self.workspace.getCurrent())
            self.canvas.ask_update()
        except:
            traceback.print_exc()
            self.error('An error occurred when trying to clear edits')
    
    def load_text(self):
        """
        Opens a dialog to load an text file.
        
        The dialog will take up most of the Window, and last until the user 
        dismisses it.  Upon dismissal, it will load the text into the
        text window, but not encode it.
        """
        self.load('Load message',self.place_text,['*.txt','*.py'])
    
    def save_text(self):
        """
        Opens a dialog to save an text file.
        
        The dialog will take up most of the Window, and last until the user 
        dismisses it. Upon dismissal, it will save the current text to
        a text file.
        """
        self.save('Save message',self.check_save_txt,['*.txt'])
    
    def do_async(self,*action):
        """
        Launchs the given action in an asynchronous thread
        
        The action parameters are an expanded list where the first element is 
        a callable and any other elements are parameters to the callable.
        
        The thread progress is monitored by async_monitor.  When the thread 
        is done, it will call async_complete in the main event thread.
        
        Parameter(s) *action: An expanded list defining the action
        Precondition: The first element of action is callable
        """
        import threading
        self.menubar.disabled = True
        self.processing = True
        self.async_thread = threading.Thread(target=self.async_work,args=action)
        self.async_thread.start()

    def async_work(self,*action):
        """
        Performs the given action asynchronously.
        
        The action parameters are an expanded list where the first element is 
        a callable and any other elements are parameters to the callable.
        
        This is the function that is launched in a separate thread.  Even if 
        the action fails, it is guaranteed to call async_complete for clean-up
        
        Parameter(s) *action: An expanded list defining the action
        Precondition: The first element of action is callable
        """
        try:
            self.workspace.increment()
            getattr(self.workspace,action[0])(*action[1:])
        except:
            traceback.print_exc()
            self.error('Action '+action[0]+' could not be completed')
        self.async_complete()
     
    @mainthread
    def async_complete(self):
        """
        Cleans up an asynchronous thread after completion.
        """
        self.workimage.update(self.workspace.getCurrent())
        self.async_thread.join()
        Clock.unschedule(self.async_action)
        self.async_thread = None
        self.async_action = None
        self.menubar.disabled = False
        self.processing = False
        #self.progress.canvas.ask_update()
        self.canvas.ask_update()


class InterfaceApp(App):
    """
    This class is the imager filter application.
    
    This class corresponds to the Kivy window and is charge of processing 
    the primary event loop. It is the root class for the application.
    """
    
    def __init__(self,file):
        """
        Initializes a new application window.
        
        It will start with the given image file. If file is None or cannot be
        read, it will use the default application image (the instructor).
        
        Parameter file: The location of the initial image file.
        Precondition: file is a string or None.
        """
        super().__init__()
        self.source = file
    
    def build(self):
        """
        Reads the kivy file and performs any initial layout
        """
        panel = InterfacePanel()
        if self.source:
            panel.source = self.source
        return panel

    def on_start(self):
        """
        Starts up the app and initializes values
        """
        super().on_start()
        self.root.config()


def launch(image):
    """
    Launches the application with the given image file.
    
    It will start with the given image file. If file is None or cannot be
    read, it will use the default application image (the instructor).
    
    Parameter file: The location of the initial image file.
    Precondition: file is a string or None.
    """
    InterfaceApp(image).run()
