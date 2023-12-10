import datetime
import os
import os.path
import ctypes
from ctypes import *
from ctypes import windll
import tkinter.messagebox as messagebox
import imageio
import sys

# Define your conditions
USE_UNICODE = True
USE_64_BIT = False

# Conditional imports based on the conditions
if USE_UNICODE:
    if USE_64_BIT:
        from dtwain_x64_unicode import dtwain
        dtwain_dll = "./dtwain64u.dll"
        dtwain_lib = "./dtwain64u.lib"
        dtwain_pdb = "./dtwain64u.pdb"
        dtwain_ini = "./dtwain64u.ini"
        twain_info = "./twaininfo.txt"
        twain_language = "./twainlanguage.txt"
        twain_resource_strings = "./twainresourcestrings_english.txt"
    else:
        from dtwain_x86_unicode import dtwain
        dtwain_dll = "./dtwain32u.dll"
        dtwain_lib = "./dtwain32u.lib"
        dtwain_pdb = "./dtwain32u.pdb"
        dtwain_ini = "./dtwain32u.ini"
        twain_info = "./twaininfo.txt"
        twain_language = "./twainlanguage.txt"
        twain_resource_strings = "./twainresourcestrings_english.txt"
else:
    if USE_64_BIT:
        from dtwain_x64 import dtwain
        dtwain_dll = "./dtwain64.dll"
        dtwain_lib = "./dtwain64.lib"
        dtwain_pdb = "./dtwain64.pdb"
        dtwain_ini = "./dtwain64.ini"
        twain_info = "./twaininfo.txt"
        twain_language = "./twainlanguage.txt"
        twain_resource_strings = "./twainresourcestrings_english.txt"
    else:
        from dtwain_x86 import dtwain
        dtwain_dll = "./dtwain32.dll"
        dtwain_lib = "./dtwain32.lib"
        dtwain_pdb = "./dtwain32.pdb"
        dtwain_ini = "./dtwain32.ini"
        twain_info = "./twaininfo.txt"
        twain_language = "./twainlanguage.txt"
        twain_resource_strings = "./twainresourcestrings_english.txt"

# Now, you can use the dtwain module in your code, and it will refer to the correct version
# dtwain.some_function()

def convert_bmp_to_jpeg(directory, quality=100):
    for filename in os.listdir(directory):
        if filename.endswith(".bmp"):
            bmp_path = os.path.join(directory, filename)
            jpeg_path = os.path.join(directory, os.path.splitext(filename)[0])# + ".jpg")

            # Read the BMP image using imageio
            img = imageio.imread(bmp_path)

            # Save the image as JPEG with specified quality
            imageio.imwrite(jpeg_path, img, format="JPEG", quality=quality)

            # Delete the original BMP file
            os.remove(bmp_path)

def get_formatted_datetime():
    now = datetime.datetime.now()
    formatted_date = now.strftime("%m%d%Y-%H%M%S-")
    print(formatted_date)
    return formatted_date

def generate_filename(tags_list, name):
    # name = app.Entry2.get() # get our name from the input field | if there was a gui this is what we would use
    print("Name: " + name) # display to console
    formatted_tags = '-'.join(tags_list) # Join the tags
    current_time = get_formatted_datetime() # get current time | to stamp filename
    file_name = f"{current_time}{name}-{formatted_tags}.jpg" if name else f"{current_time}{formatted_tags}.jpg"
    print("Filename: " + file_name)
    return file_name

def show_twain_error_message():
    messagebox.showerror("Twain Device Error: No TWAIN Device Found!", "No Twain Devices Found. \nContact your system administrator to install a Twain driver.")

# This function will be responsible for acquiring the image from the twain device
def acquire_image(tags_list=None, name=None):
    if tags_list is None:
        tags_list = ['TestTag1', 'TestTag2']
    if name is None:
        name = 'TestName'
    print("Getting current working directory.")
    # Get our current working directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    twain_output_directory = current_dir
    print("Generating filename.")
    # run our generate_filename function
    file_name = generate_filename(tags_list, name)
    print(file_name)
    # set the path of where to save images
    print("Setting the path of where to save images.")
    file_path = os.path.join(current_dir, file_name)
    print("File path: " + file_path)
    print("Attempting to Acquire the image...")

    # Check if TWAIN is installed
    print("Checking if TWAIN is installed.")
    mydll = windll.LoadLibrary(os.path.join(current_dir, dtwain_dll))
    isAvail = mydll.DTWAIN_IsTwainAvailable()

    if isAvail:
        print("TWAIN is available.")
        # Initialize the DTWAIN Dynamic Link Library
        print("Initializing DTWAIN...")
        mydll.DTWAIN_SysInitialize()

        # Select a Source
        print("Selecting TWAIN Source...")
        TwainSource = mydll.DTWAIN_SelectSource()

        if TwainSource:
            print("TWAIN Source selected.")
            print("Acquiring image...")
            # Change the current working directory to the script's directory
            os.chdir(twain_output_directory)   
            mydll.DTWAIN_AcquireFile(TwainSource, file_name + ".bmp", dtwain.DTWAIN_BMP, dtwain.DTWAIN_USELONGNAME, dtwain.DTWAIN_PT_DEFAULT, 1, 0, 1, 0)
            print("Image acquisition complete.")
            print("Image saved as", file_name)
            convert_bmp_to_jpeg(twain_output_directory)
            # Shut down any open TWAIN Source and DTWAIN itself
            print("Destroying TWAIN Source and DTWAIN...")
            mydll.DTWAIN_SysDestroy()

    else:
        print("TWAIN is not available.")
        print("This is likely because you don't have a TWAIN device installed.")
        show_twain_error_message()
    
# Old Function which we will reuse
def handle_image(app):
    print("Attempting to Acquire Image...")
    script_dir = os.path.dirname(os.path.abspath("backend.py"))

    my_file = generate_filename(app)
    twain_output_directory = app.Entry1.get()
    twain_output_directory = os.path.abspath(twain_output_directory)  # Convert to absolute path
    file_path = os.path.join(script_dir, my_file)
    print("File path:", file_path)
    # Check if TWAIN is available
    print("Checking if TWAIN is available...")
    mydll = ctypes.WinDLL(os.path.join(script_dir, "dtwain32.dll"))
    isAvail = mydll.DTWAIN_IsTwainAvailable()

    if isAvail:
        print("TWAIN is available.")
        # Initialize the DTWAIN Dynamic Link Library
        print("Initializing DTWAIN...")
        mydll.DTWAIN_SysInitialize()

        # Select a Source
        print("Selecting TWAIN Source...")
        TwainSource = mydll.DTWAIN_SelectSource()

        if TwainSource:
            print("TWAIN Source selected.")
            print("Acquiring image...")
            # Change the current working directory to the script's directory
            os.chdir(twain_output_directory)   
            mydll.DTWAIN_AcquireFile(TwainSource, my_file + ".bmp", dtwain.DTWAIN_BMP, dtwain.DTWAIN_USELONGNAME, dtwain.DTWAIN_PT_DEFAULT, 1, 0, 1, 0)
            print("Image acquisition complete.")
            print("Image saved as", my_file)
            convert_bmp_to_jpeg(twain_output_directory)
            # Shut down any open TWAIN Source and DTWAIN itself
            print("Destroying TWAIN Source and DTWAIN...")
            mydll.DTWAIN_SysDestroy()

    else:
        print("TWAIN is not available.")
        print("This is likely because you don't have a TWAIN device installed.")
        show_twain_error_message()