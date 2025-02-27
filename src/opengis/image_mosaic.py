"""
This module provides functionality for mosaicking multiple GeoTIFF images.
It uses GDAL (Geospatial Data Abstraction Library) for processing geospatial data.
"""

import os
from osgeo import gdal

def mosaic(input_dir, output_dir=None):
    """
    Create a mosaic from multiple GeoTIFF images in a directory.
    
    Args:
        input_dir (str): Directory path containing the input GeoTIFF files
        output_dir (str, optional): Directory path for the output mosaic. If None, 
                                  the mosaic will be saved in the input directory
    
    Returns:
        None
    """
    path = input_dir
    # Get all TIFF files from the directory (case-insensitive)
    tiff_extensions = ('.tif', '.tiff')
    path_lists = [f for f in os.listdir(path) if f.lower().endswith(tiff_extensions)]
    
    if len(path_lists) < 2:
        print(f"Not enough tif images in folder {path} for mosaic.")
        return
        
    print(f"Processing {len(path_lists)} tif images......")

    # Open all images using GDAL
    images = [gdal.Open(os.path.join(path, img), gdal.GA_ReadOnly) for img in path_lists]

    # Check projections before proceeding
    projections_match, ref_proj = check_projections(images)
    if not projections_match:
        print("Error: Not all images have the same coordinate system!")
        print("Please ensure all images are in the same coordinate system before mosaicking.")
        # Clean up
        for img in images:
            img = None
            del img
        return

    # Get projection from the first image
    input_proj = images[0].GetProjection()

    # Use folder name for output filename
    folder_name = os.path.basename(os.path.normpath(path))
    output_filename = f"{folder_name}_Mosaic.tif"

    # Configure GDAL warp options for the mosaic
    options = gdal.WarpOptions(srcSRS=input_proj, dstSRS=input_proj, format='GTiff',
                             resampleAlg=gdal.GRA_NearestNeighbour)

    # Set up output path, create directory if it doesn't exist
    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = os.path.join(output_dir, output_filename)
    else:
        output_path = os.path.join(path, output_filename)
        
    # Create the mosaic using GDAL Warp
    gdal.Warp(output_path, images, options=options)

    # Clean up by closing all images
    for img in images:
        img = None
        del img

    print(f"Mosaic completed, processed {len(path_lists)} tif files")
    print(f"Output file: {output_path}")

def check_projections(images):
    """
    Check if all images have the same projection/coordinate system.
    
    Args:
        images (list): List of GDAL dataset objects
    
    Returns:
        bool: True if all projections match, False otherwise
        str: Reference projection string for comparison
    """
    if not images:
        return False, None
        
    reference_proj = images[0].GetProjection()
    
    for img in images[1:]:
        current_proj = img.GetProjection()
        if current_proj != reference_proj:
            return False, reference_proj
            
    return True, reference_proj

def get_subfolder_paths(folder_path):
    return [os.path.join(folder_path, d) for d in os.listdir(folder_path) 
            if os.path.isdir(os.path.join(folder_path, d))]

def batch_mosaic(folder_path, out_path):
    """
    Perform mosaic operation on all subfolders in the given directory.
    
    Args:
        folder_path (str): Path to the parent directory containing subfolders with GeoTIFF files
        out_path (str): Output directory path for all mosaics
    
    Returns:
        None
    """
    subfolders = get_subfolder_paths(folder_path)
    for path in subfolders:
        mosaic(path, out_path)

# Usage Examples
if __name__ == "__main__":
    # Example 1: Create a mosaic from a single directory of GeoTIFF files
    input_directory = r"C:\Data\Landsat_Images"
    output_directory = r"C:\Data\Mosaics"
    mosaic(input_directory, output_directory)
    
    # Example 2: Batch mosaic processing for multiple subfolders
    parent_directory = r"C:\Data\Multiple_Landsat_Sets"
    output_directory = r"C:\Data\Batch_Mosaics"
    batch_mosaic(parent_directory, output_directory)