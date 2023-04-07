#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Auto Page Extract, Edit, Save for CBR Files
 by JDHatten
    
    Extract any or all pages of a CBR file, edit them and save them as images. Multiple options
    like resizing images, changing the format, renaming the extracted files, etc. etc.

How To Use:
    Either drag one or more files or directories onto this script or run the script in your
    root directory with CBR files.

Requirements:
    Pillow is an imaging library that must be installed in order to modify pages which are images.
    - pip install Pillow
    - https://pypi.org/project/Pillow/
    
    Rarfile is an archive reading module that must be installed to extract and save pages/images.
    - pip install rarfile
    - https://pypi.org/project/rarfile/
    
    Patool is an alternative archive reading module in case Rarfile fails.
    - pip install patool
    - https://pypi.org/project/patool/
    
    It is also important to know after installing "rarfile" you must also have UnRAR on your system
    with the "UnRAR.dll" and the correct environment path set for your operating system.
    - https://stackoverflow.com/questions/55574212/how-to-set-path-to-unrar-library-in-python/55577032#55577032
    
    OR you can download the "UnRAR.exe" (included in this package) and place it in the same
    directory as this script.
    - https://www.rarlab.com/rar_add.htm
    - - http://www.rarlab.com/rar/UnRARDLL.exe
    - - https://www.rarlab.com/rar/unrarw32.exe (will extract UnRAR.exe for Windows systems)

TODO:
    [X] Create log file.
        [] Record completion times
    [] Support for other comic book file types (CBZ,CB7,CBC,etc - Many of these use the .cbr extension even though they are not using RAR compression)
    [] Add more image editing options that make sense for pages of book/magazine/etc.
        [X] Combine two pages vertically or horizontal.
        [X] Rotate pages/images.
        [] Combine up to 4 pages and add a BOX layout. OR stick with multiple stacked combines? (2,3 + 4,5 + 2,4 = 2,3,4,5)
    [] GUI
    [X] Write better error messages. Add errors to log file.
    [X] Incrementing numbers for page file names.
    [] Extra image format parameters. Optimization, Quality, Subsampling, etc.
    [] Ask before overwriting files.
    
'''

# This script will continue to run allowing the dropping of additional files or directories.
# Set this to False and this script will run once, do it's thing, and close
loop_script = True

# Create a log file that will record all the details of each playlist created, which includes
# the full file paths of the playlists and the disc image files recorded within.
# Note: Log file creation is always overwritten, not appended too.
create_log_file = True


# Preset Options
DESCRIPTION = 20
PAGES_TO_EXTRACT = 0
SORT_PAGES_BY = 1
CHANGE_WIDTH = 2
CHANGE_HEIGHT = 3
KEEP_ASPECT_RATIO = 4
ROTATE_PAGES = 5
COMBINE_PAGES = 6
RESAMPLING_FILTER = 7
CHANGE_IMAGE_FORMAT = 10
IMAGE_FORMAT_PARAMS = 11
SEARCH_SUB_DIRS = 12
OVERWRITE_FILES = 13
MODIFY_FILE_NAMES = 14
SAVE_DIR_PATH = 15
KEEP_FILE_PATHS_INTACT = 16

# Page Sort Modifiers
ALPHA = 0         # Sort alphabetically where digits are sorted individually (100 < 99). [Default]
ALPHA_NUMBER = 1  # Sort alphabetically with digits represented as whole numbers (100 > 99).
NUMBERS_ONLY = 2  # Sort with numbers only, letters are ignored.
ASCENDING = 0
DESCENDING = 1

# Editing Pages
ALL_PAGES = 9997999

# Image Modifier
NO_CHANGE = 0
CHANGE_TO = 1
MODIFY_BY_PIXELS = 2
MODIFY_BY_PERCENT = 3
UPSCALE = 4
DOWNSCALE = 5

# Layout
HORIZONTAL = 0
VERTICAL = 1
#BOX = 2

# File Name Modifiers
INSERT_FILE_NAME = 0    # File name of CBR file.
INSERT_PAGE_NAME = 1    # File name of archived image/page in CRB file.
INSERT_PAGE_NUMBER = 2  # Page number of archived image/page extracted in CRB file.
INSERT_COUNTER = 3      # Incrementing number starting from first file saved (1,2,3...).

# Image Formats
BMP = ('Windows Bitmaps', '.bmp')
GIF = ('Graphics Interchange Format', '.gif', 'gifv')
ICO = ('Windows Icon', '.ico')  # Available Sizes: 16x16, 24x24, 32x32*, 48x48, 64x64, 128x128, 256x256**, *Default, **Maximum
JPG = ('JPEG', '.jpg', '.jpeg', '.jpe')
JP2 = ('JPEG 2000', '.jp2')
PBM = ('Portable Image Format', '.pbm', '.pgm', '.ppm', '.pxm', '.pnm')
PNG = ('Portable Network Graphics', '.png')
RAS = ('Sun Rasters', '.ras', '.ras', '.sun', '.sr')
TIF = ('TIFF', '.tif', '.tiff')
WEB = ('Web Picture', '.webp')
SUPPORTED_IMAGE_FORMATS = [BMP, GIF, ICO, JPG, JP2, PBM, PNG, RAS, TIF, WEB]

## TODO:
# Extra Image Saving Parameters
QUALITY = 0       # Quality settings are equivalent to the Photoshop settings with possible values between 0-100. (JPEG, TIFF, WEBP Only)
QUANT_TABLES = 1  # Quantization Tables - Note: specific values are not supported here, only preset values accepted. (JPEG Only)
SUBSAMPLING = 2   # Possible subsampling values are 0, 1 and 2 that correspond to 4:4:4, 4:2:2 and 4:2:0, respectively. (JPEG Only)
OPTIMIZE = 3      # Possible optimization values are True or False. (GIF, JPEG, PNG Only)
PROGRESSIVE = 4   # Possible progressive values are True or False. (JPEG Only)
COMPRESSION = 5   # Possible compress levels are between 1-9, default 6, and auto-set to 9 if OPTIMIZE is set to True. (BMP, PNG Only)
                  # - Note: BMP only allows values between 1-2 (1 = 256 Colors, 2 = 16 Colors)
# The following JPEG presets are available by default:
# 'web_low', 'web_medium', 'web_high', 'web_very_high', 'web_maximum', 'low', 'medium', 'high', 'maximum'.
# To apply a preset use   IMAGE_FORMAT_PARAMS : { QUALITY : 'preset_name' }
# To apply 'only' the quantization table use    { QUANT_TABLES : 'preset_name' }
# To apply 'only' the subsampling setting use   { SUBSAMPLING : 'preset_name' }

# Resampling Filters
NEAREST = 0
BILINEAR = 1
BICUBIC = 2

# CBR/RAR File Meta Data
META_FILE_PATH = 0
META_FILE_NAME = 1
META_FILE_SIZE = 2
META_COMPRESS_SIZE = 3
META_COMPRESS_TYPE = 4
META_DATE_TIME = 5
META_CRC = 6
META_HOST_OS = 7

# RAR File Meta Data Constants
# Compression Type
RAR_M0 = 48  # No Compression.
RAR_M1 = 49  # Compression Level -m1 - Fastest Compression.
RAR_M2 = 50  # Compression Level -m2
RAR_M3 = 51  # Compression Level -m3
RAR_M4 = 52  # Compression Level -m4
RAR_M5 = 53  # Compression Level -m5 - Maximum Compression.

# Host OS Type
RAR_OS_WIN32 = 2  # Windows
RAR_OS_UNIX = 3   # UNIX
RAR_OS_MACOS = 4  # MacOS (only in RAR3)
RAR_OS_BEOS = 5   # BeOS (only in RAR3)
RAR_OS_OS2 = 1    # OS2 (only in RAR3)
RAR_OS_MSDOS = 0  # MSDOS (only in RAR3)


### Select the default preset to use here. ###
selected_preset = 4

preset0 = { #           : Defaults          # If option omitted, the default value will be used.
  DESCRIPTION           : '',               # Description of this preset.
  PAGES_TO_EXTRACT      : (1,-1),           # (1,-1) = All Pages. Examples: Range of Pages = ('Starting Page','Ending Page') or Specific Pages = [1,3,6,-1] or One Page = 3
                                            # - Negative numbers start from the last page and count backwards. Example: If 50 total pages, -1 = 50 and -7 = 43.
                                            # - Ranged numbers outside the bounds of the total pages will be forced inbounds and specific out-of-bound numbers will be ignored.
  SORT_PAGES_BY         :(ALPHA, ASCENDING),# Before extracting, sort pages in alphabetically, alphabetically with whole numbers, or only using numbers.
                                            # - Sort Modifiers: ALPHA, ALPHA_NUMBER, NUMBERS_ONLY, ASCENDING, DESCENDING
  CHANGE_WIDTH          : NO_CHANGE,        # Modify the width or height of all extracted pages. Numbers can be + or -, and percents = 50 or (in qoutes) '50%'.
  CHANGE_HEIGHT         : NO_CHANGE,        # - Example: (Modifier, Number)  Modifiers: NO_CHANGE, CHANGE_TO, MODIFY_BY_PIXELS, MODIFY_BY_PERCENT, UPSCALE, DOWNSCALE
  KEEP_ASPECT_RATIO     : True,             # Keep aspect ratio only if one size, width or height, has changed.
  ROTATE_PAGES          : None,             # Rotate angle in degrees counter clockwise any or all pages from PAGES_TO_EXTRACT.
                                            # - Example: All Pages = Degrees or Specific Pages = {1:90, 2:180,...}
  COMBINE_PAGES         : None,             # Combine two pages from PAGES_TO_EXTRACT. Example: [(VERTICAL,1,2),(HORIZONTAL,3,4),...]
  RESAMPLING_FILTER     : NEAREST,          # When editing a page/image use this resampling filter. Examples: NEAREST, BILINEAR, BICUBIC
  CHANGE_IMAGE_FORMAT   : NO_CHANGE,        # Change the image format of a page too... BMP, GIF, ICO, JPG, JP2, PBM, PNG, RAS, TIF, WEB
  IMAGE_FORMAT_PARAMS   : None,             ## TODO: Extra JPEG Image Format Parameters: QUALITY, QUANT_TABLES, SUBSAMPLING, OPTIMIZE, PROGRESSIVE, COMPRESSION
                                            ## - Examples: {QUALITY : 90, QUANT_TABLES : 'high', SUBSAMPLING : 1, OPTIMIZE : True, PROGRESSIVE : False, COMPRESSION : 7}
  SEARCH_SUB_DIRS       : False,            # After searching a directory also search it's sub-directories if True.
  OVERWRITE_FILES       : False,            # If file with the same name and path already exists overwrite it if True.
  MODIFY_FILE_NAMES     : None,             # Rename each extracted image/page with a modified file name.
                                            # - File Name Modifier: INSERT_FILE_NAME, INSERT_PAGE_NAME, INSERT_PAGE_NUMBER, INSERT_COUNTER
                                            # - Example: [ 'From-(', INSERT_FILE_NAME,')-Page-(',INSERT_PAGE_NAME ] = 'From-(FileName)-Page-(F001).jpg'
  SAVE_DIR_PATH         : None,             # Absolute or relative paths accepted. Default: this script's root directory + '/{CBR file name}'
                                            # - Use a List to change save directory path on each page. Example: ['path/to/dir1', 'path/to/dir2',...]
                                            # - The save paths index will repeat if the amount of pages is greater than this list size.
                                            # - Extracted page file names can be the same if each is saved in a different directory.
  KEEP_FILE_PATHS_INTACT: True,             # When extracting pages/files they may be in one or more folders. So when saving, stick with the same file structure.
                                            # If False, all extracted pages/files will be placed directly in the SAVE_DIR_PATH and there may be file name conflicts.
}                                           # Note: Any 'pages numbers' that are 'strings' are considered disabled, ignored. Example: 5 -> '5'
                                            #       This is mainly for use in the app. Page numbers are used in: PAGES_TO_EXTRACT, ROTATE_PAGES, COMBINE_PAGES
##TODO: Some preset options:
#                         "Thumbnail" first page,
#                         "Preview" get first 3-5 pages,
#                         "Extract All Pages As Is",
#                         "Extract All Pages Saved As...",
#                         "Extract All Pages Resized To...",
preset1 = {             # Example Preset 1
  DESCRIPTION           : 'Create thumbnail images of first page (160p).',
  PAGES_TO_EXTRACT      : 1,
  CHANGE_HEIGHT         : (CHANGE_TO, 160),
  CHANGE_HEIGHT         : 160,
  KEEP_ASPECT_RATIO     : True,
  OVERWRITE_FILES       : True
}
preset2 = {             # Example Preset 2
  DESCRIPTION           : 'Combine first and last pages horizontally.',
  PAGES_TO_EXTRACT      : [1, -1],
  COMBINE_PAGES         : [(HORIZONTAL, 1, -1)],
  OVERWRITE_FILES       : True
}
preset3 = {             # Example Preset 3
  DESCRIPTION           : ('Extract pages 1-7 and downscale height to 1080p. '+
                           'Combine fourth, fifth, sixth and seventh pages in a box layout. '+
                           'Save each file with the page number as a PNG.'),
  PAGES_TO_EXTRACT      : (1,7),
  CHANGE_WIDTH          : NO_CHANGE,
  CHANGE_HEIGHT         : (DOWNSCALE, 1080),
  KEEP_ASPECT_RATIO     : True,
  COMBINE_PAGES         : [(HORIZONTAL, 4, 5),(HORIZONTAL, 6, 7),(VERTICAL, 4, 6)], # Box Layout
  RESAMPLING_FILTER     : BICUBIC,
  CHANGE_IMAGE_FORMAT   : PNG,
  OVERWRITE_FILES       : True,
  MODIFY_FILE_NAMES     : [INSERT_FILE_NAME,'-Page-',INSERT_PAGE_NUMBER],
  KEEP_FILE_PATHS_INTACT: False
}
preset4 = {             # TESTING
  DESCRIPTION           : ('Get first, fourth, fifth, and last pages. '+
                           'Downscaled height to 1080p. '+
                           'Combine fourth and fifth pages horizontally. '+
                           'Save each page in a different directory.'),
  #PAGES_TO_EXTRACT      : (-1,-10),
  #PAGES_TO_EXTRACT      : (1,-1),
  #PAGES_TO_EXTRACT      : (1,5),
  #PAGES_TO_EXTRACT      : (-10, -1),
  #PAGES_TO_EXTRACT      : (10),
  #PAGES_TO_EXTRACT      : (10, -1),
  #PAGES_TO_EXTRACT      : (100, -1),
  #PAGES_TO_EXTRACT      : [1,4,5,-1,203,0,97,-100,-122,-133,-169],
  #PAGES_TO_EXTRACT      : [1,4,5,-1],
  PAGES_TO_EXTRACT      : [1,4,5,-2,-1],
  #PAGES_TO_EXTRACT      : [10],
  SORT_PAGES_BY         :(ALPHA_NUMBER, ASCENDING),
  CHANGE_WIDTH          : NO_CHANGE,
  CHANGE_HEIGHT         : (DOWNSCALE, 1080),
  #CHANGE_HEIGHT         : (MODIFY_BY_PERCENT, 50),
  KEEP_ASPECT_RATIO     : True,
  #ROTATE_PAGES          : 180,
  #ROTATE_PAGES          : {1:90, 4:180, 5:90, -1:180},
  #ROTATE_PAGES          : {4:180, 5:90},
  #ROTATE_PAGES          : {1:90, ALL_PAGES': 180},
  #COMBINE_PAGES         : [(VERTICAL, 1, -1), (HORIZONTAL, 4, 5)],
  #COMBINE_PAGES         : [(HORIZONTAL, 4, 5)], ## TODO: do not delete 2nd image after combine and allow multiple same page combines??
  COMBINE_PAGES         : [(HORIZONTAL, 4, 5), (HORIZONTAL, -1, 1)],
  #COMBINE_PAGES         : [(HORIZONTAL, 2, 3),(HORIZONTAL, 4, 5),(VERTICAL, 2, 4)],
  RESAMPLING_FILTER     : BICUBIC,
  #CHANGE_IMAGE_FORMAT   : PNG,
  OVERWRITE_FILES       : True,
  #MODIFY_FILE_NAMES     : (INSERT_FILE_NAME,'-01', ' (', INSERT_PAGE_NAME, ')'),
  MODIFY_FILE_NAMES     : [INSERT_FILE_NAME,'-01','--',INSERT_PAGE_NUMBER],
  SAVE_DIR_PATH         : r'test\dir',
  #SAVE_DIR_PATH         : [r'test\dir1',r'test\dir2',r'test\dir3'],
  #SAVE_DIR_PATH         : {1 : r'test\dir1', 4 : r'test\dir2', -1 : r'test\dir3', ALL_PAGES : r'test\dir' }, ##TODO:
  KEEP_FILE_PATHS_INTACT: False
}

# Add any newly created presets to this preset_options List.
preset_options = [preset0,preset1,preset2,preset3,preset4]



####### Don't Edit Below This Line (unless you know what your doing) #######


debug = True ## TODO

from common_functions import MakeDirectories, ModifyImageSize, MakeList, SortFiles
from pathlib import Path, PurePath
import patoolib
from PIL import Image, UnidentifiedImageError
from os import startfile as OpenFile, walk as Search
import rarfile
import re
import sys
import tempfile

ROOT_DIR = Path(__file__).parent

# If the UnRAR Tool is not located in below path or properly installed on this machine,
# then this script won't work.
unrar_app_path = Path(PurePath().joinpath(ROOT_DIR, 'UnRAR.exe'))
if unrar_app_path.exists():
    rarfile.UNRAR_TOOL = unrar_app_path

# Log data for internal use.
LOG_DATA = 1137
CBR_FILE_PATHS =      0
IMAGE_EXTENSIONS =    1
PAGE_DATA =           2
PAGE_INDEXES =         20
PAGE_META_DATA =       21
PAGE_EDITS_MADE =      22
PAGE_SAVE_PATHS =      23
PAGE_SAVE_DETAILS =     24
NOT_SAVED =              240
#SAVE_ERROR =             241
NEW_SAVE =               241
OVERWRITTEN =            242
PAGE_EXTRACT_ERRORS =  25
PAGE_EDIT_ERRORS =     26

TEMP_DIR =            3
IMAGE_DATA = 7777

WIDTH = 0
HEIGHT = 1


### Change the preset in use, retaining any log data.
###     (preset) A preset that holds the user options on how to extract, edit, and save images/pages from a CBR file.
###     (all_the_data) A Dictionary of all the details on how to handle CBR files and logs of everthing done so far.
###     --> Returns a [Dictionary]
def changePreset(preset, all_the_data = {}):
    
    log_data = all_the_data.get(LOG_DATA, {}).copy()
    
    #print(log_data)
    
    if not log_data:
        all_the_data = preset
        all_the_data[LOG_DATA] = {}
        all_the_data[LOG_DATA][CBR_FILE_PATHS] = []
        all_the_data[LOG_DATA][IMAGE_EXTENSIONS] = []
        all_the_data[LOG_DATA][PAGE_DATA] = {}
        all_the_data[LOG_DATA][TEMP_DIR] = None
        
        for image_formats in SUPPORTED_IMAGE_FORMATS:
            for i in range(0, len(image_formats)):
                if i == 0: continue
                all_the_data[LOG_DATA][IMAGE_EXTENSIONS].append(image_formats[i])
    
    else:
        all_the_data = preset
        all_the_data[LOG_DATA] = log_data
    
    #print(all_the_data)
    
    return all_the_data


### Find CBR files and prepare all the page meta data inside each CBR.
###     (path) Path to a file or directory.
###     (all_the_data) A Dictionary of all the details on how to handle CBR files and logs of everthing done so far.
###     --> Returns a [Dictionary]
def findCBRFiles(path, all_the_data):
    search_sub_dirs = all_the_data.get(SEARCH_SUB_DIRS, False)
    paths = MakeList(path)
    
    for path in paths:
        
        if not Path(path).exists():
            print(f'Does Not Exist: {path}')
            continue
        
        if Path(path).is_file():
            
            file_path = Path(path)
            
            if file_path.suffix == '.cbr':
                print(f'CBR File Found: {file_path}')
                all_the_data = preparePageData(file_path, all_the_data)
        
        elif Path(path).is_dir():
            
            for root, dirs, files in Search(path):
                
                for file in files:
                    file_path = Path(PurePath().joinpath(root, file))
                    
                    if file_path.suffix == '.cbr':
                        print(f'CBR File Found: {file_path}')
                        all_the_data = preparePageData(file_path, all_the_data)
                
                if not search_sub_dirs:
                    break
    
    return all_the_data


### Prepare all data needed to start extracting images from a CBR/RAR file.
###     (cbr_file_path) Path to a CBR file.
###     (all_the_data) A Dictionary of all the details on how to handle CBR files and logs of everthing done so far.
###     --> Returns a [Dictionary]
def preparePageData(cbr_file_path, all_the_data):
    cbrar = rarfile.RarFile(cbr_file_path)
    #print(cbrar.namelist())
    #print(cbrar.RarExtFile)
    
    if cbr_file_path not in all_the_data[LOG_DATA][CBR_FILE_PATHS]:
        all_the_data[LOG_DATA][CBR_FILE_PATHS].append(cbr_file_path)
    else:
        print('This CBR file has already been added.')
        return all_the_data
    
    all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path] = {
        PAGE_META_DATA : [],
        PAGE_INDEXES : [],
        PAGE_EDITS_MADE : {
            CHANGE_HEIGHT : {},
            CHANGE_WIDTH : {},
            ROTATE_PAGES : {},
            COMBINE_PAGES : {}
        },
        PAGE_EXTRACT_ERRORS : {},
        PAGE_EDIT_ERRORS : {},
        PAGE_SAVE_PATHS : {},
        PAGE_SAVE_DETAILS : {}
    }
    
    # Get meta data of archived files.
    for rar_archived_file in cbrar.infolist():
        #print(rar_archived_file.filename, rar_archived_file.file_size, rar_archived_file.compress_size, rar_archived_file.compress_type,
        #      rar_archived_file.date_time, rar_archived_file.CRC, rar_archived_file.host_os, rar_archived_file.mode, rar_archived_file.mtime,
        #      rar_archived_file.ctime, rar_archived_file.atime, rar_archived_file.file_redir)
        if rar_archived_file.is_file():
            file_path = Path(rar_archived_file.filename)
            
            # Images files only and ignore MacOSX resource fork files.
            if file_path.suffix in all_the_data[LOG_DATA][IMAGE_EXTENSIONS] and file_path.stem[:1] != '.':
                all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_META_DATA].append(
                    (
                        file_path,
                        rar_archived_file.filename,
                        #rar_archived_file.file_size,
                        #rar_archived_file.compress_size,
                        #rar_archived_file.compress_type,
                        #rar_archived_file.date_time,
                        #rar_archived_file.CRC,
                        #rar_archived_file.host_os
                    )
                )
        #if rar_archived_file.is_dir():
    
    # Sort page/image files.
    sort_method, sort_order = all_the_data.get(SORT_PAGES_BY, (ALPHA,ASCENDING))
    alpha_number = True if sort_method == ALPHA_NUMBER else False
    numbers_only = True if sort_method == NUMBERS_ONLY else False
    all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_META_DATA].sort(
        reverse = True if sort_order else False,
        key = lambda page: SortFiles(page, META_FILE_PATH, alpha_number, numbers_only)
    )
    
    all_the_data = convertPageNumbersToIndexes(all_the_data, cbr_file_path)
    
    return all_the_data


### Create page indexes from page numbers in PAGES_TO_EXTRACT.
###     (all_the_data) A Dictionary of all the details on how to handle CBR files and logs of everthing done so far.
###     (cbr_file_path) Path to a CBR file.
###     --> Returns a [Dictionary]
def convertPageNumbersToIndexes(all_the_data, cbr_file_path):
    pages_to_extract = all_the_data.get(PAGES_TO_EXTRACT)
    total_pages = len(all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_META_DATA])
    page_indexes = []
    
    if pages_to_extract:
        
        if type(pages_to_extract) == tuple: # Range of Pages
            page_indexes = getAllPageIndexesFromRange(total_pages, pages_to_extract[0], pages_to_extract[1])
        
        elif type(pages_to_extract) == list: # Specific Pages
            for page_number in pages_to_extract:
                if type(page_number) == int and page_number != 0 and page_number <= total_pages and page_number >= -total_pages:
                    page_index = getPageIndex(total_pages, page_number)
                    page_indexes.append(page_index)
                else:
                    print(f'Specific page #{page_number} is out of bounds and will be disregarded.')
        
        elif type(pages_to_extract) == int: # Single Page
            page_indexes = getAllPageIndexesFromRange(total_pages, None, pages_to_extract)
        
        else:
            print(f'ERROR: "PAGES_TO_EXTRACT : {pages_to_extract}" are not proper page numbers.')
            return None
    
    else: # All Pages
        page_indexes = getAllPageIndexesFromRange(total_pages)
    
    all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_INDEXES] = page_indexes
    print(f'Page Indexes (to extract): {page_indexes}')
    
    return all_the_data


### After finding CBR files and reocrding thier file paths, run all three Extract, Edit, And Save functions back-to-back.
###     (all_the_data) A Dictionary of all the details on how to handle CBR files and logs of everthing done so far.
###     --> Returns a [Dictionary]
def extractEditSavePages(all_the_data):
    cbr_file_paths = all_the_data[LOG_DATA][CBR_FILE_PATHS]
    
    for cbr_file_path in cbr_file_paths:
        # Extract
        all_the_data = extractPages(all_the_data, cbr_file_path)
        # Edit
        all_the_data = modifyPages(all_the_data, cbr_file_path)
        # Save
        all_the_data = savePages(all_the_data, cbr_file_path)
        
        # Clean up memory used and no longer needed.
        all_the_data[IMAGE_DATA].clear()
        if all_the_data[LOG_DATA].get(TEMP_DIR):
            all_the_data[LOG_DATA][TEMP_DIR].cleanup()
            all_the_data[LOG_DATA][TEMP_DIR] = None
    
    return all_the_data


### Extract pages from a CBR file / images from a RAR archive.
###     (all_the_data) A Dictionary of all the details on how to handle CBR files and logs of everthing done so far.
###     (cbr_file_path) A Path to a CBR file.
###     --> Returns a [Dictionary]
def extractPages(all_the_data, cbr_file_path):
    page_indexes = all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_INDEXES]
    cbrar_file = rarfile.RarFile(cbr_file_path)
    page_meta_data = all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_META_DATA]
    
    if all_the_data.get(IMAGE_DATA):
        all_the_data[IMAGE_DATA].clear()
    else:
        all_the_data[IMAGE_DATA] = {}
    
    for page_index in page_indexes:
        
        try:
            if all_the_data[LOG_DATA].get(TEMP_DIR):
                # All files already extracted, continue on with Extraction Method Two.
                temp_dir = all_the_data[LOG_DATA][TEMP_DIR]
                archived_file_path = page_meta_data[page_index][META_FILE_PATH]
                archived_img = Path(PurePath().joinpath(temp_dir.name, archived_file_path))
            else:
                # Extraction Method One
                archived_img = cbrar_file.open(page_meta_data[page_index][META_FILE_NAME], mode='r', pwd=None)
                archived_img = cbrar_file.open(page_meta_data[page_index][META_FILE_NAME], mode='r', pwd=None)
            
            all_the_data[IMAGE_DATA][page_index] = Image.open(archived_img)
        
        except (rarfile.Error, FileNotFoundError, UnidentifiedImageError, ValueError, TypeError) as err:
            print(err)
            
            # Log Errors
            if all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EXTRACT_ERRORS].get(page_index):
                all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EXTRACT_ERRORS][page_index].append(err)
            else:
                all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EXTRACT_ERRORS][page_index] = [err]
        
        if all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EXTRACT_ERRORS].get(page_index):
            try:
                print(f'Failed to extract page {page_index+1} from archive, so extracting all files to a temporary directory...')
                
                # Attempt to extract file with another tool. This will extract all files in the CBR file temporarily.
                if all_the_data[LOG_DATA].get(TEMP_DIR):
                    temp_dir = all_the_data[LOG_DATA][TEMP_DIR]
                else:
                    temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
                    all_the_data[LOG_DATA][TEMP_DIR] = temp_dir
                    # Extraction Method Two
                    patoolib.extract_archive(cbr_file_path, outdir=temp_dir.name)
                    #patoolib.extract_archive(r'c:/file/does/not/extist.rar', outdir=temp_dir.name) # Force an error
                    #cbrar_file.extractall(path=temp_dir.name, members=None, pwd=None) # Will still throw an error
                
                archived_file_path = page_meta_data[page_index][META_FILE_PATH]
                extracted_file_path = Path(PurePath().joinpath(temp_dir.name, archived_file_path))
                all_the_data[IMAGE_DATA][page_index] = Image.open(extracted_file_path)
                
                print(f'Successfully extracted and opened needed page {page_index+1}.')
                
            except (patoolib.util.PatoolError, FileNotFoundError, UnidentifiedImageError, ValueError, TypeError) as err:
                print(err)
                
                # Log Errors
                if all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EXTRACT_ERRORS].get(page_index):
                    all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EXTRACT_ERRORS][page_index].append(err)
                else:
                    all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EXTRACT_ERRORS][page_index] = [err]
    
    return all_the_data


### Make edits to pages.
###     (all_the_data) A Dictionary of all the details on how to handle CBR files and logs of everthing done so far.
###     (cbr_file_path) A Path to a CBR file.
###     --> Returns a [Dictionary]
def modifyPages(all_the_data, cbr_file_path):
    page_indexes = all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_INDEXES]
    page_meta_data = all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_META_DATA]
    
    width_change = all_the_data.get(CHANGE_WIDTH)
    height_change = all_the_data.get(CHANGE_HEIGHT)
    keep_aspect_ratio = all_the_data.get(KEEP_ASPECT_RATIO, True)
    
    rotate_pages = all_the_data.get(ROTATE_PAGES)
    combine_pages = all_the_data.get(COMBINE_PAGES)
    resample = all_the_data.get(RESAMPLING_FILTER, NEAREST)
    
    page_images = all_the_data.get(IMAGE_DATA, {})
    total_pages = len(page_meta_data)
    
    if width_change or height_change:
        
        for page_index, image in page_images.items():
            
            print(f'Org Image Size: {image.width} x {image.height}')
            
            try:
                resized_image = resizeImage(image, width_change, height_change, keep_aspect_ratio)
                print(f'New Image Size: {resized_image.width} x {resized_image.height}')
                error = None
            except Exception as err: ## TODO: what errors can happen? stop and 'continue' on error?
                error = f'Image Resize Failed: {err}'
                if width_change:
                    error_code = CHANGE_WIDTH
                else:
                    error_code = CHANGE_HEIGHT
                print(error)
                all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EDIT_ERRORS][page_index] = {error_code : error}
            
            if error:
                continue
            else:
                page_images[page_index] = resized_image
                all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EDITS_MADE][CHANGE_WIDTH][page_index] = (image.width, resized_image.width)
                all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EDITS_MADE][CHANGE_HEIGHT][page_index] = (image.height, resized_image.height)
                
                #print(f'Width: {image.width}->{resized_image.width}')
                #input(f'Height: {image.height}->{resized_image.height}')
    
    if rotate_pages:
        
        # Rotate All Pages
        '''if type(rotate_pages) == int:
            degrees = rotate_pages
            rotate_pages = {}
            page_index_done = True
            for page in page_indexes:
                rotate_pages[page] = degrees
        
        else:
            page_index_done = False'''
        
        # Expand ALL_PAGES to indexes and convert specific pages to indexes.
        rotate_pages_to_indexes = {}
        rotate_all_degrees = 0
        if type(rotate_pages) == dict:
            for page, degrees in rotate_pages.items():
                # Pages numbers that are strings are considered disabled, ignored.
                if type(page) != str:
                    if page != ALL_PAGES:
                        rotate_pages_to_indexes[getPageIndex(total_pages, page)] = degrees
                    else:
                        rotate_all_degrees = degrees
        else:
            rotate_all_degrees = rotate_pages
        
        rotate_indexes = {}
        for page in page_indexes:
            if page in rotate_pages_to_indexes:
                rotate_indexes[page] = rotate_pages_to_indexes[page]
            elif rotate_all_degrees:
                rotate_indexes[page] = rotate_all_degrees
        
        for page_index, degrees in rotate_indexes.items():
            
            # Skip if page failed extraction.
            if all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EXTRACT_ERRORS].get(page_index):
                if len(all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EXTRACT_ERRORS][page_index]) > 1:
                    continue
            
            '''if page_index_done:
                page_index = page
            else:
                page_index = getPageIndex(total_pages, page)'''
            
            print(f'Rotate Page: {page_index+1} {degrees} Degress')
            
            error = None
            rotated_image = None
            
            if page_index in page_indexes:
                
                # If a previous edit has failed/errored on this page, skip it.
                if all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EDIT_ERRORS].get(page_index):
                    continue
                
                try:
                    rotated_image = rotatePage(
                        all_the_data[IMAGE_DATA][page_index],
                        angle = degrees,
                        resample = resample
                    )
                except Exception as err:
                    error = f'Image Rotation Failed: {err}'
                    print(error)
                    all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EDIT_ERRORS][page_index] = {ROTATE_PAGES : error}
            
            else:
                error = f'Image Rotation Failed: Page not found in PAGES_TO_EXTRACT'
                print(error)
                all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EDIT_ERRORS][page_index] = {ROTATE_PAGES : error}
            
            if error:
                continue
            elif rotated_image:
                all_the_data[IMAGE_DATA][page_index] = rotated_image
                all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EDITS_MADE][ROTATE_PAGES][page_index] = degrees
    
    if combine_pages:
        for pages_to_combine in combine_pages:
            
            # Pages numbers that are strings are considered disabled, ignored.
            if type(pages_to_combine[1]) != str and type(pages_to_combine[2]) != str:
                
                layout_direction = pages_to_combine[0]
                
                page_index_one = getPageIndex(total_pages, pages_to_combine[1], False)
                page_index_two = getPageIndex(total_pages, pages_to_combine[2], False)
                
                # Only skip editing if both pages failed extraction (no error recording necessary),
                # else if just one page failed extraction, get the obvious error incoming.
                if (all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EXTRACT_ERRORS].get(page_index_one) and
                    all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EXTRACT_ERRORS].get(page_index_two)):
                        if (len(all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EXTRACT_ERRORS][page_index_one]) > 1 and
                            len(all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EXTRACT_ERRORS][page_index_two]) > 1):
                                continue
                
                print(f'Combine: {"Horizontally" if layout_direction==HORIZONTAL else "Vertically"} Page: {page_index_one+1} and {page_index_two+1}')
                
                error = None
                combined_image = None
                
                if page_index_one in page_indexes and page_index_two in page_indexes:
                    
                    # If a previous edit has failed/errored on these pages, skip.
                    if (all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EDIT_ERRORS].get(page_index_one) or
                        all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EDIT_ERRORS].get(page_index_two)):
                            continue
                    
                    try:
                        combined_image = combinePages(
                            all_the_data[IMAGE_DATA][page_index_one],
                            all_the_data[IMAGE_DATA][page_index_two],
                            layout = layout_direction,
                            resample = resample,
                            resize_big_image = True
                        )
                    except KeyError as error_index:
                        page_error = int(str(error_index)) + 1
                        error = f'Image Combining Error: Page {page_error} not found'
                    except Exception as err:
                        error = f'Image Combining Error: {err}'
                
                else:
                    missing_pages = ''
                    if page_index_one not in page_indexes:
                        missing_pages += f'{page_index_one+1}'
                    if page_index_one not in page_indexes and page_index_two not in page_indexes:
                        missing_pages += ' and '
                    if page_index_two not in page_indexes:
                        missing_pages += f'{page_index_two+1}'
                    error = f'Image Combining Failed: Page {missing_pages} not found in PAGES_TO_EXTRACT'
                
                if error:
                    print(error)
                    all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EDIT_ERRORS][page_index_one] = {COMBINE_PAGES : error}
                    all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EDIT_ERRORS][page_index_two] = {COMBINE_PAGES : error}
                    continue
                
                elif combined_image:
                    all_the_data[IMAGE_DATA][page_index_one] = combined_image
                    
                    #all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EDITS_MADE][COMBINE_PAGES][page_index_one] = page_index_two
                    
                    # Log each combined page and how they were combined and if they have been combined with other pages already combined.
                    combine_log = all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EDITS_MADE][COMBINE_PAGES]
                    combine_first_page_log = combine_log.get(page_index_one)
                    combine_second_page_log = combine_log.get(page_index_two)
                    
                    if combine_first_page_log:
                        if combine_second_page_log:
                            combine_first_page_log.append( ({page_index_two : combine_second_page_log.copy()}, layout_direction) )
                            #combine_log[page_index_two] = page_index_one
                            #combine_log.pop(page_index_two)
                        else:
                            combine_first_page_log.append((page_index_two, layout_direction))
                    else:
                        if combine_second_page_log:
                            combine_log[page_index_one] = [({page_index_two : combine_second_page_log.copy()}, layout_direction)]
                            #combine_log[page_index_two] = page_index_one
                            #combine_log.pop(page_index_two)
                        else:
                            combine_log[page_index_one] = [(page_index_two, layout_direction)]
                    
                    combine_log[page_index_two] = page_index_one
                    
                    # Second image should no longer exists now so remove it from the image and log data.
                    all_the_data[IMAGE_DATA].pop(page_index_two)
                    #all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EDIT_ERRORS].pop(page_index_two)
                    #all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_SAVE_PATHS].pop(page_index_two)
    
    return all_the_data


### Start saving all the pages already extracted and edited as image files.
###     (all_the_data) A Dictionary of all the details on how to handle CBR files and logs of everthing done so far.
###     (cbr_file_path) A Path to a CBR file.
###     --> Returns a [Dictionary]
def savePages(all_the_data, cbr_file_path):
    page_meta_data = all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_META_DATA]
    overwrite_files = all_the_data.get(OVERWRITE_FILES, False)
    keep_file_paths_intact = all_the_data.get(KEEP_FILE_PATHS_INTACT, True)
    page_images = all_the_data.get(IMAGE_DATA)
    
    next_dir = 0
    counter = 1
    for page_index, image in page_images.items():
        #print(f'{page_index} : {image}')
        
        ## TODO: Check if file has been saved already or errored
        ##       def savePage() for single page saves, retry saves for individual file overwriting
        ##       if file re-edited, mark not saved
        
        archived_file_path = page_meta_data[page_index][META_FILE_PATH]
        if not keep_file_paths_intact:
            archived_file_path = Path(archived_file_path.name)
        
        # Get directory path to save files in and create any directories that don't already exist
        default_save_dir = ROOT_DIR
        save_dir_paths = all_the_data.get(SAVE_DIR_PATH, default_save_dir)
        if save_dir_paths == '':
            save_dir_paths = ROOT_DIR
        save_dir_paths = MakeList(save_dir_paths)
        
        save_dir_path = save_dir_paths[next_dir]
        if next_dir < len(save_dir_paths)-1:
            next_dir += 1
        else:
            next_dir = 0
        
        if save_dir_path:
            save_to_directory_path = Path(save_dir_path)
            if not Path.exists(save_to_directory_path):
                save_to_directory_path = MakeDirectories(default_save_dir, save_dir_path)
        else:
            save_to_directory_path = MakeDirectories(default_save_dir, cbr_file.stem)
        
        ## TODO: insert page number of all combined pages?
        save_file_path = createFilePathFrom(all_the_data, cbr_file_path, archived_file_path, save_to_directory_path, page_index+1, counter)
        counter += 1
        
        all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_SAVE_PATHS][page_index] = save_file_path
        
        print(f'Saving Page: {save_file_path}')
        
        if overwrite_files and save_file_path.exists():
            try:
                save_file_path.unlink(missing_ok=True) # Delete
            except OSError as err:
                print(err)
            #all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_SAVE_PATHS][page_index] = [save_file_path, OVERWRITTEN]
            all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_SAVE_DETAILS][page_index] = OVERWRITTEN
        elif not overwrite_files and save_file_path.exists():
            #all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_SAVE_PATHS][page_index] = [save_file_path, NOT_SAVED]
            all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_SAVE_DETAILS][page_index] = NOT_SAVED
        else:
            #all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_SAVE_PATHS][page_index] = [save_file_path, NEW_SAVE]
            all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_SAVE_DETAILS][page_index] = NEW_SAVE
        
        try:
            image.save(save_file_path)
            error = None
        except (OSError, ValueError) as err:
            error = f'Failed To Save Page/Image: {err}'
            print(error)
            #all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_SAVE_PATHS][page_index][1] = SAVE_ERROR
            all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_SAVE_DETAILS][page_index] = error
        
        #all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_SAVE_DETAILS][page_index] = error
    
    return all_the_data


### Create a full file Path from an extracted page/image file. Format change are made here as well as
### creating new directories along new Path.
###     (all_the_data) A Dictionary of all the details on how to handle CBR files and logs of everthing done so far.
###     (cbr_file_path) A Path to a CBR file.
###     (archived_file_path) The local file path within the archive file.
###     (root_save_path) The full root Path to where the file is to be saved.
###     (page_number) Page Number.
###     (counter) Incrementing number counter.
###     --> Returns a [Path]
def createFilePathFrom(all_the_data, cbr_file_path, archived_file_path, root_save_path, page_number, counter = 0):
    format_change = all_the_data.get(CHANGE_IMAGE_FORMAT)
    modify_file_names = all_the_data.get(MODIFY_FILE_NAMES)
    
    if modify_file_names:
        file_name = ''
        for text in modify_file_names:
            if type(text) == str:
                file_name += text
            elif type(text) == int:
                if text == INSERT_FILE_NAME:
                    file_name += cbr_file_path.stem
                elif text == INSERT_PAGE_NAME:
                    file_name += archived_file_path.stem
                elif text == INSERT_PAGE_NUMBER:
                    file_name += f'{page_number}'
                elif text == INSERT_COUNTER:
                    file_name += f'{counter}'
    else:
        file_name = archived_file_path.stem
    
    if format_change:
        file_ext = format_change[1]
    else:
        file_ext = archived_file_path.suffix
    
    # Create file path and make sub-directories if necessary.
    root_save_path = MakeDirectories(root_save_path, archived_file_path.parents)
    save_file_path = Path(PurePath().joinpath(root_save_path, f'{file_name}{file_ext}'))
    
    return save_file_path


### Return a List of all page numbers from a range of numbers or just one number. If any numbers falls
### outside of the total range of pages (total_pages) they will be forced in bounds. If both page_start
### and page_end are left blank then all pages will be returned.
###     (total_pages) Total number of pages in a CBR.
###     (page_start) First page to start from, 0 = 1. If None, will only extract the page_end (a single page).
###     (page_end) Last page to end on. If None or 0, it will be the last page.
###     --> Returns a [List]
def getAllPageIndexesFromRange(total_pages, page_start = None, page_end = None):
    page_indexes = []
    
    if ((page_start == None or type(page_start) == str) # All Pages
        and (page_end == None or type(page_start) == str)):
            page_start = 0
            page_end = total_pages - 1
    
    else:
        if not page_start or type(page_start) == str:
            page_start = getPageIndex(total_pages, page_end)
        else:
            page_start = getPageIndex(total_pages, page_start)
        
        if not page_end or type(page_end) == str:
            page_end = total_pages - 1
        else:
            page_end = getPageIndex(total_pages, page_end)
    
    if page_start < page_end:
        current_page = page_start
        last_page = page_end
    else:
        current_page = page_end
        last_page = page_start
    
    while current_page <= last_page:
        page_indexes.append(current_page)
        current_page += 1
    
    return page_indexes


### Take a page number, which may be a negative number, and change it into an index number
### that is between 0 and the total number of CBR pages.
###     (total_pages) Total number of pages in a CBR.
###     (page_number) A positive or negative page number.
###     (keep_inbounds) Keep page number to index within the total page count.
###     --> Returns a [Integer]
def getPageIndex(total_pages, page_number, keep_inbounds = True):
    if page_number >= total_pages and keep_inbounds:
        page_index = total_pages - 1 # last page
    elif page_number <= -total_pages and keep_inbounds:
        page_index = 0
    elif page_number < 0:
        page_index = total_pages + page_number
    elif page_number == 0 and keep_inbounds:
        page_index = 0
        #print(f'Page #{page_number} is out of bounds and will be disregarded.')
    else:
        page_index = page_number - 1
    
    return page_index


### Resize an image.
###     (image) An Image that is to be resized.
###     (width_change) A Tuple with specific data on how to modify the width of an image.
###     (height_change) A Tuple with specific data on how to modify the height of an image.
###     (keep_aspect_ratio) Keep aspect ratio only if one size, width or height, has changed.
###     (resample) Resampling filter to use while modifying an Image.
###     --> Returns a [Image]
def resizeImage(image, width_change, height_change, keep_aspect_ratio = True, resample = NEAREST):
    if resample == BILINEAR:  resample = Image.Resampling.BILINEAR
    elif resample == BICUBIC: resample = Image.Resampling.BICUBIC
    else:                     resample = Image.Resampling.NEAREST
    
    if width_change or height_change:
        new_width, new_height = ModifyImageSize((image.width, image.height), (width_change, height_change), keep_aspect_ratio)
        image = image.resize((new_width, new_height), resample=resample, box=None, reducing_gap=None)
    
    return image


### Combine two images together either horizontal or vertically.
###     (img1) First Image that is to be combined.
###     (img2) Second Image that is to be combined.
###     (layout) Layout images either HORIZONTAL or VERTICAL before combining.
###     (resample) Resampling filter to use while modifying an Image.
###     (resize_big_image) Decrease the size of the larger image to match the smaller Image.
###     --> Returns a [Image]
def combinePages(img1, img2, layout = HORIZONTAL, resample = NEAREST, resize_big_image = True): ## TODO: Combine up to 4 images? new BOX layout
    if resample == BILINEAR:  resample = Image.Resampling.BILINEAR
    elif resample == BICUBIC: resample = Image.Resampling.BICUBIC
    else:                     resample = Image.Resampling.NEAREST
    
    if layout == HORIZONTAL:
        if img1.height == img2.height:
            _img1 = img1
            _img2 = img2
        elif (((img1.height > img2.height) and resize_big_image) or
              ((img1.height < img2.height) and not resize_big_image)):
            _img1 = img1.resize((int(img1.width * img2.height / img1.height), img2.height), resample=resample)
            _img2 = img2
        else:
            _img1 = img1
            _img2 = img2.resize((int(img2.width * img1.height / img2.height), img1.height), resample=resample)
        combined_image = Image.new('RGB', (_img1.width + _img2.width, _img1.height))
        combined_image.paste(_img1, (0, 0))
        combined_image.paste(_img2, (_img1.width, 0))
    
    elif layout == VERTICAL:
        if img1.width == img2.width:
            _img1 = img1
            _img2 = img2
        elif (((img1.width > img2.width) and resize_big_image) or
              ((img1.width < img2.width) and not resize_big_image)):
            _img1 = img1.resize((img2.width, int(img1.height * img2.width / img1.width)), resample=resample)
            _img2 = img2
        else:
            _img1 = img1
            _img2 = img2.resize((img1.width, int(img2.height * img1.width / img2.width)), resample=resample)
        combined_image = Image.new('RGB', (_img1.width, _img1.height + _img2.height))
        combined_image.paste(_img1, (0, 0))
        combined_image.paste(_img2, (0, _img1.height))
    
    return combined_image


### Rotate an Image.
###     (img1) Image that is to be roated.
###     (angle) The angle of degrees to rotate.
###     (resample) Resampling filter to use while modifying an Image.
###     --> Returns a [Image]
def rotatePage(image, angle = 0, resample = NEAREST):
    if resample == BILINEAR:  resample = Image.Resampling.BILINEAR
    elif resample == BICUBIC: resample = Image.Resampling.BICUBIC
    else:                     resample = Image.Resampling.NEAREST
    
    image = image.rotate(angle, resample, expand=True, center=None, translate=None, fillcolor=None)
    
    return image


### Create log file for all CBR page/images created.
###     (all_the_data) A Dictionary of all the details on how to handle CBR files and logs of everthing done so far.
###     (log_file_path) Path of a log file.
###     --> Returns a [Boolean]
def createLogFile(all_the_data, log_file_path = None):
    log_file_created = False
    log_data = all_the_data.get(LOG_DATA)
    save_msg = {NOT_SAVED:'Not Saved', NEW_SAVE : 'New Save', OVERWRITTEN : 'Overwritten'}
    
    if log_data:
        page_files_extracted, page_extract_errors, page_files_saved, page_edit_errors, page_save_errors = getLogNumbers(all_the_data)
    else:
        print('\nNo CBR page log data found.')
        return False
    
    # Print general details of CBR page created
    text_lines = []
    text_lines.append('=================================')
    text_lines.append('= Auto Page Extract, Edit, Save =')
    text_lines.append('=  for CBR Files     - Log File =')
    text_lines.append('=================================')
    text_lines.append(f'- Total Pages Extracted: {page_files_extracted}')
    if page_extract_errors:
        text_lines.append(f'- Total Pages Failed To Extract: {page_extract_errors}')
    text_lines.append(f'- Total Pages Saved: {page_files_saved-page_save_errors}')
    if page_save_errors:
        text_lines.append(f'- Total Pages Not Saved Due To Errors: {page_save_errors}')
    if page_edit_errors:
        text_lines.append(f'- Total Pages That Failed Editing*: {page_edit_errors}')
        text_lines.append('*If an error happens while editing a page, it still keeps it\'s previous edits and can still be saved.')
    
    print_text_lines = text_lines.copy()
    print('\n'+'\n'.join(print_text_lines))
    
    # Only create a log file when pages are saved or errors happened.
    if page_files_saved + page_edit_errors == 0:
        return False
    
    if create_log_file:
        
        if not log_file_path:
            log_file_name = f'{Path(__file__).stem}__log.txt'
            log_file_path = Path(PurePath().joinpath(ROOT_DIR, log_file_name))
        
        desc = all_the_data.get(DESCRIPTION)
        if desc and desc != '':
            text_lines.append('\nDescription of the preset used to extract, edit, and save page files:')
            text_lines.append(f'  {desc}')
        
        base_arrow = '----> '
        
        for cbr_file_path, page_data in log_data[PAGE_DATA].items():
            #text_lines.append('\nCBR File Path')
            #text_lines.append(f'  {cbr_file_path}')
            text_lines.append(f'\nCBR File --> {cbr_file_path}')
            
            page_extract_errors = page_data.get(PAGE_EXTRACT_ERRORS, {})
            page_save_paths = page_data.get(PAGE_SAVE_PATHS, {})
            page_edit_errors = page_data.get(PAGE_EDIT_ERRORS, {})
            page_save_details = page_data.get(PAGE_SAVE_DETAILS, {})
            page_edits_made = page_data.get(PAGE_EDITS_MADE, {})
            
            pages_resized_width = page_edits_made.get(CHANGE_WIDTH, {})
            pages_resized_height = page_edits_made.get(CHANGE_HEIGHT, {})
            pages_rotated = page_edits_made.get(ROTATE_PAGES, {})
            pages_combined = page_edits_made.get(COMBINE_PAGES, {})
            
            for page_index in page_data[PAGE_INDEXES]:
                
                #arrow = base_arrow[len(str(page_index)):]
                page_str = f'{page_index+1}'
                arrow = base_arrow[len(page_str):]
                indentation = '          '
                indentation += '    '[:len(str(page_index))]
                #indentation += '---'
                edit_errors = page_edit_errors.get(page_index, {})
                
                # Check For Extract Page Errors
                # Note: There are 2 extraction methods, both must fail to be considered an "error".
                pee = page_extract_errors.get(page_index, [])
                if len(pee) > 1:
                    text_lines.append(f'    Page {page_str} {arrow}[EXTRACTION ERRORS] {" | ".join([str(e) for e in pee])}')
                    continue
                
                # Page Number and File Path
                if type(page_save_details.get(page_index, 0)) != int:
                    # Error, Not Saved
                    text_lines.append(f'    Page {page_str} {arrow}[ERROR] {page_save_details[page_index]}')
                
                else:
                    # Saved
                    if page_index in page_save_paths:
                        page_save_details_str = save_msg[page_save_details[page_index]]
                        text_lines.append(f'    Page {page_str} {arrow}[{page_save_details_str}] {page_save_paths[page_index]}')
                    else:
                        final_page_combined = page_index
                        final_page_combined_str = ''
                        if page_index in pages_combined:
                            final_page_combined_index = pages_combined[page_index]
                            while type(final_page_combined_index) == int:
                                final_page_combined = final_page_combined_index
                                final_page_combined_index = pages_combined[final_page_combined_index]
                            final_page_combined_str = f'(Page {final_page_combined+1}) '
                        
                        # Save Path points to final page combined with.
                        final_page = page_save_paths.get(final_page_combined, 'File Path Missing')
                        text_lines.append(f'    Page {page_str} {arrow}{final_page_combined_str}{final_page}')
                
                # Page Resize
                if CHANGE_WIDTH not in edit_errors or CHANGE_HEIGHT not in edit_errors:
                    if page_index in pages_resized_width or page_index in pages_resized_height:
                        org_size = f'{pages_resized_width[page_index][0]} x {pages_resized_height[page_index][0]}'
                        new_size = f'{pages_resized_width[page_index][1]} x {pages_resized_height[page_index][1]}'
                        text_lines.append(f'{indentation}{arrow}   Page Size Changed From: [ {org_size} -to- {new_size} ]')
                else:
                    error_data = edit_errors.get(CHANGE_WIDTH)
                    error_data = error_data if error_data else edit_errors.get(CHANGE_HEIGHT)
                    text_lines.append(f'{indentation}{arrow}   ERROR: {error_data}')
                
                # Page Rotation
                if ROTATE_PAGES not in edit_errors:
                    if page_index in pages_rotated:
                        degrees = pages_rotated[page_index]
                        text_lines.append(f'{indentation}{arrow}   Page Rotated: [ {degrees} Degrees ]')
                else:
                    text_lines.append(f'{indentation}{arrow}   ERROR: {edit_errors[ROTATE_PAGES]}')
                
                # Page Combines
                if COMBINE_PAGES not in edit_errors:
                    if page_index in pages_combined:
                        other_page_index = pages_combined[page_index]
                        if type(other_page_index) == int:
                            pages_combined_str = f'[ Page {other_page_index+1} & {page_str} ]'
                        else:
                            pages_combined_str = f'[ Page {page_str} & '
                            all_pages_combined_with_this_page_index = pages_combined.get(page_index, [])
                            pages_combined_str = getAllPagesCombined(all_pages_combined_with_this_page_index, pages_combined_str)
                        
                        text_lines.append(f'{indentation}{arrow}   Pages Combined: {pages_combined_str}')
                else:
                    text_lines.append(f'{indentation}{arrow}   ERROR: {edit_errors[COMBINE_PAGES]}')
        
        # Write Log File
        try:
            log_file_path.write_text('\n'.join(text_lines), encoding='utf-8', errors='strict')
            log_file_created = log_file_path # return log file path
        except (OSError, UnicodeError, ValueError) as error:
            print(f'\nCouldn\'t save log file due to {type(error).__name__}: {type(error).__doc__}')
            print(f'{error}\n')
    
    else:
        print('Log file creation turned off.')
    
    return log_file_created


### Create string showing all pages combined for use in log file.
###     (all_pages_combined_list) List of pages combined and the layout direction.
###     (pages_combined_str) String added to log file that shows all pages combined.
###     --> Returns a [String]
def getAllPagesCombined(all_pages_combined_list, pages_combined_str):
    for combined_page in all_pages_combined_list:
        direction = 'Horizontally' if combined_page[1] == HORIZONTAL else 'Vertically'
        if type(combined_page[0]) == int:
            pages_combined_str += f'{combined_page[0]+1} {direction} ]'
        else:
            for next_page_combined, additional_pages in combined_page[0].items():
                pages_combined_str += f'-[ {direction} ]-[ Page {next_page_combined+1} & '
                pages_combined_str = getAllPagesCombined(additional_pages, pages_combined_str)
    
    return pages_combined_str


### Get the overall log numbers on how many pages have been extracted, edited, and saved as well as any errors.
###     (all_the_data) A Dictionary of all the details on how to handle CBR files and logs of everthing done so far.
###     --> Returns a [Integer] x 5
def getLogNumbers(all_the_data):
    page_files_extracted = 0
    page_extract_errors = 0
    page_files_saved = 0
    page_edit_errors = 0
    page_save_errors = 0
    for cbr_file_path in cbr_file_paths:
        page_files_extracted += len(all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_INDEXES])
        page_files_saved += len(all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_SAVE_PATHS])
        for details in all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_SAVE_DETAILS].values():
            page_save_errors += 1 if type(details) != int else 0
        for error in all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EDIT_ERRORS].values():
            page_edit_errors += 1 if error else 0 ## TODO: each COMBINE_PAGES error gets added twice. fix?
        for error in all_the_data[LOG_DATA][PAGE_DATA][cbr_file_path][PAGE_EXTRACT_ERRORS].values():
            page_extract_errors += 1 if len(error) > 1 else 0
    
    return page_files_extracted, page_extract_errors, page_files_saved, page_edit_errors, page_save_errors


### Open a log file for viewing.
###     (log_file_path) Path to a log file.
###     --> Returns a [None]
def openLogFile(log_file_path):
    OpenFile(log_file_path)
    return None


### Script Starts Here
if __name__ == '__main__':
    print(sys.version)
    print('=================================')
    print('= Auto Page Extract, Edit, Save =')
    print('=  for CBR Files    by JDHatten =')
    print('=================================')
    MIN_VERSION = (3,8,0)
    MIN_VERSION_STR = '.'.join([str(n) for n in MIN_VERSION])
    assert sys.version_info >= MIN_VERSION, f'This Script Requires Python v{MIN_VERSION_STR} or Newer'
    
    paths = sys.argv[1:]
    if not paths:
        paths = [ROOT_DIR]
    
    all_the_data = changePreset(preset_options[selected_preset])
    
    loop = True
    while loop:
        
        for path in paths:
            all_the_data = findCBRFiles(path, all_the_data)
        
        cbr_file_paths = all_the_data[LOG_DATA][CBR_FILE_PATHS]
        cbr_count = len(cbr_file_paths)
        if cbr_count:
            input(f'CBR files found: {cbr_count}, start extracting?')
            all_the_data = extractEditSavePages(all_the_data)
        else:
            print('\nNo CBR files found.')
        
        page_files_extracted, page_extract_errors, page_files_saved, page_edit_errors, page_save_errors = getLogNumbers(all_the_data)
        
        print(f'\nTotal Pages Extracted: {page_files_extracted}')
        print(f'Total Pages Failed To Extract: {page_extract_errors}')
        print(f'Total Pages Saved: {page_files_saved-page_save_errors}')
        print(f'Total Pages Not Saved Due To Errors: {page_save_errors}')
        print(f'Total Pages That Failed Editing*: {page_edit_errors}')
        print('*If an error happens while editing a page, it still keeps it\'s previous edits and can still be saved.')
        
        try_again = loop_script
        loop = loop_script
        while try_again:
            drop = input('\nDrop another CBR file or directory here or leave blank and press [Enter] to create a log file now: ')
            drop = drop.replace('"', '')
            path = Path(drop)
            if drop == '':
                loop = False
                try_again = False
            elif path.exists():
                paths = [path]
                try_again = False
            else:
                print(f'This is not an existing file or directory path: "{drop}"')
    
    log_file_created = createLogFile(all_the_data)
    if log_file_created:
        print('--> Check log for more details.')
        openLogFile(log_file_created)
    else:
        print('No log file necessary.')
