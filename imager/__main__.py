"""
An application for processing images

This file is the main entry-point for the imager application.  When you 'run the folder',
this is the file that is executed. This file works as traffic cop that directs the 
application to the correct entry point.  It allows you to launch the GUI, or to do 
something simple from the command line.

Author: Walker M. White (wmw2)
Date:   October 29, 2019
"""
# To handle command line options
import argparse

# This is necessary to prevent conflicting command line arguments
import os
os.environ["KIVY_NO_ARGS"] = "1"


def parse():
    """
    Returns: the command line arguments
    
    This function uses argparse to handle the command line arguments.  The benefit of
    argparse is the built-in error checking and help menu.
    """
    parser = argparse.ArgumentParser(prog='imager',description='Application to process an image file.')
    parser.add_argument('image', type=str, nargs='?', help='the image file to process')
    parser.add_argument('-t','--test',   action='store_true',  help='run a unit test on Image and Editor')
    parser.add_argument('-g','--grade',   action='store_true', help='grade the assignment')
    return parser.parse_args()


def launch(image):
    """
    Launches the gui application with the given image and output (if specified)
    
    Parameter image: The image file to use immediately after launch
    Precondition: image is a filename string or None
    
    Parameter output: The output file for saving any changes
    Precondition: output is a filename string or None
    """
    from interface import launch
    launch(image)


def unittest():
    """
    Runs a unittest on the Image and Editor classes
    """
    from a6test import test_all
    test_all()


def grade(image):
    """
    Grades the assignment.
    
    Parameter output: The output file for storing feedback
    Precondition: output is a filename string or None
    """
    try:
        import grade
        grade.grade(image)
    except:
        print('The grading program is not currently installed.')


def execute():
    """
    Executes the application, according to the command line arguments specified.
    """
    args = parse()
    
    image = args.image
    
    # Switch on the options
    if args.test:
        unittest()
    elif args.grade:
        grade(image)
    else:
        launch(image)

# Do it
execute()