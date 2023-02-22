#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Common Helper Functions by JDHatten
'''

import pathlib
import re

re_number_pattern = re.compile('\d*\.?\d*', re.IGNORECASE)


### Create directories starting from an existing root path. Return False if root does not exist.
###     (root) A root path that already exists.
###     (directories) A directory string or a list of directories to create.
###     --> Returns a [Boolean] or [Path]
def MakeDirectories(root, directories):
    if not pathlib.Path(root).exists():
        return False
    # Split a string that is repersenting a path.
    if type(directories) == str:
        if directories.find('\\\\') > -1:
            directories = directories.split('\\\\')
        elif directories.find('\\') > -1:
            directories = directories.split('\\')
        elif directories.find('/') > -1:
            directories = directories.split('/')
    directories = MakeList(directories)
    for sub_dir in directories:
        if sub_dir != '.':
            root = pathlib.Path(pathlib.PurePath().joinpath(root, sub_dir))
            root.mkdir(mode=0o777, parents=False, exist_ok=True)
    return root


### Make any variable a list if not already a list (or tuple, pathlib._PathParents) for looping purposes.
###     (variable) A variable of any kind.
###     --> Returns a [List] or [Tuple]
def MakeList(variable):
    if variable == None:
        variable = []
    elif type(variable) != list and type(variable) != tuple and type(variable) != pathlib._PathParents:
        variable = [variable]
    return variable


### Modify the size/shape of an image.
###     (org_image_shape) The height and width of the orginal image. ( Width, Height )
###     (image_size_modifications) How to modify the height and width of the orginal image. [ ( Modifier, Width ), ( Modifier, Height ) ]
###     (keep_aspect_ratio) True or False
###     --> Returns a [Tuple] (Height, Width)
def ModifyImageSize(org_image_shape, image_size_modifications, keep_aspect_ratio = True):
    
    # Image Dimensions
    WIDTH = 0
    HEIGHT = 1

    # Image Modifiers
    MODIFIER = 0
    NUMBER = 1
    NO_CHANGE = 0
    CHANGE_TO = 1
    MODIFY_BY_PIXELS = 2
    MODIFY_BY_PERCENT = 3
    UPSCALE = 4
    DOWNSCALE = 5
    
    # Width
    if type(image_size_modifications[WIDTH]) is tuple:
        
        if image_size_modifications[WIDTH][MODIFIER] == NO_CHANGE:
            new_width = org_image_shape[WIDTH]
        
        if image_size_modifications[WIDTH][MODIFIER] == CHANGE_TO:
            new_width = image_size_modifications[WIDTH][NUMBER]
        
        if image_size_modifications[WIDTH][MODIFIER] == MODIFY_BY_PERCENT:
            if type(image_size_modifications[WIDTH][NUMBER]) == str:
                percent_number = re_number_pattern.search(image_size_modifications[WIDTH][NUMBER])
                if percent_number:
                    multipler = float(percent_number).group().strip() / 100
                    new_width = org_image_shape[WIDTH] * multipler
                else:
                    print(f'Error: Can\'t decipher what kind of number this is: {image_size_modifications[WIDTH]}')
                    new_width = org_image_shape[WIDTH]
            else:
                multipler = image_size_modifications[WIDTH][NUMBER] / 100
                new_width = org_image_shape[WIDTH] * multipler
        
        if image_size_modifications[WIDTH][MODIFIER] == MODIFY_BY_PIXELS:
            new_width = org_image_shape[WIDTH] + image_size_modifications[WIDTH][NUMBER]
        
        if image_size_modifications[WIDTH][MODIFIER] == UPSCALE:
            if org_image_shape[WIDTH] < image_size_modifications[WIDTH][NUMBER]:
                new_height = image_size_modifications[WIDTH][NUMBER]
            else:
                new_height = org_image_shape[WIDTH]
        
        if image_size_modifications[WIDTH][MODIFIER] == DOWNSCALE:
            if org_image_shape[WIDTH] > image_size_modifications[WIDTH][NUMBER]:
                new_height = image_size_modifications[WIDTH][NUMBER]
            else:
                new_height = org_image_shape[WIDTH]
    
    elif image_size_modifications[WIDTH] != NO_CHANGE:
        new_width = image_size_modifications[WIDTH]
    
    else:
        new_width = org_image_shape[WIDTH]
    
    # Height
    if type(image_size_modifications[HEIGHT]) is tuple:
        
        if image_size_modifications[HEIGHT][MODIFIER] == NO_CHANGE:
            new_height = org_image_shape[HEIGHT]
        
        if image_size_modifications[HEIGHT][MODIFIER] == CHANGE_TO:
            new_height = image_size_modifications[HEIGHT][NUMBER]
        
        if image_size_modifications[HEIGHT][MODIFIER] == MODIFY_BY_PERCENT:
            if type(image_size_modifications[HEIGHT][NUMBER]) == str:
                percent_number = re_number_pattern.search(image_size_modifications[HEIGHT][NUMBER])
                if percent_number:
                    multipler = float(percent_number.group().strip()) / 100
                    new_height = org_image_shape[HEIGHT] * multipler
                else:
                    print(f'Error: Can\'t decipher what kind of number this is: {image_size_modifications[HEIGHT]}')
                    new_height = org_image_shape[HEIGHT]
            else:
                multipler = image_size_modifications[HEIGHT][NUMBER] / 100
                new_height = org_image_shape[HEIGHT] * multipler
        
        if image_size_modifications[HEIGHT][MODIFIER] == MODIFY_BY_PIXELS:
            new_height = org_image_shape[HEIGHT] + image_size_modifications[HEIGHT][NUMBER]
        
        if image_size_modifications[HEIGHT][MODIFIER] == UPSCALE:
            if org_image_shape[HEIGHT] < image_size_modifications[HEIGHT][NUMBER]:
                new_height = image_size_modifications[HEIGHT][NUMBER]
            else:
                new_height = org_image_shape[HEIGHT]
        
        if image_size_modifications[HEIGHT][MODIFIER] == DOWNSCALE:
            if org_image_shape[HEIGHT] > image_size_modifications[HEIGHT][NUMBER]:
                new_height = image_size_modifications[HEIGHT][NUMBER]
            else:
                new_height = org_image_shape[HEIGHT]
    
    elif image_size_modifications[HEIGHT] != NO_CHANGE:
        new_height = image_size_modifications[HEIGHT]
    
    else:
        new_height = org_image_shape[HEIGHT]
    
    # Aspect Ratio
    if keep_aspect_ratio and image_size_modifications[WIDTH] == NO_CHANGE and image_size_modifications[HEIGHT] != NO_CHANGE :
        factor_w = org_image_shape[WIDTH] / org_image_shape[HEIGHT]
        new_width = org_image_shape[WIDTH] - (org_image_shape[HEIGHT] - new_height) * factor_w
    
    elif keep_aspect_ratio and image_size_modifications[HEIGHT] == NO_CHANGE and image_size_modifications[WIDTH] != NO_CHANGE:
        factor_h = org_image_shape[HEIGHT] / org_image_shape[WIDTH]
        new_height = org_image_shape[HEIGHT] - (org_image_shape[WIDTH] - new_width) * factor_h
    
    new_width = round(new_width)
    new_height = round(new_height)
    #print(f'Width: [{new_width}]  X  Height: [{new_height}]')
    
    return new_width, new_height


### Custom Sort function using file meta data.
###     (file) A Tuple with the full file path and various meta data.
###     (index) The index of which meta data to sort by.
###     --> Returns a [String] or [Integer]
def SortFiles(file, index):
    meta_data = file[index] if file[index] else -9999999999999
    if index == 0: # File Path, Sort By Name Only.
        meta_data = meta_data.name
    return meta_data
