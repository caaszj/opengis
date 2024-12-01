"""
Batch Reprojection Tool

This module provides functionality to reproject multiple geospatial images to match 
a reference image's projection and optionally its resolution.
"""

import os
from osgeo import gdal

# Enable GDAL exceptions for better error handling
gdal.UseExceptions()

def batch_reprojection(src_img_path, ref_img_path, output_dir, match_resolution=True, 
                   input_formats=('.tif','.tiff','.img','.dat','.hdf'),
                   output_format='GTiff'):
    """
    Batch reproject multiple images to match a reference image's projection system.

    Args:
        src_img_path (str): Directory containing source images to be reprojected
        ref_img_path (str): Path to the reference image
        output_dir (str): Directory where reprojected images will be saved
        match_resolution (bool): If True, output images will match reference image's resolution
        input_formats (tuple): Supported input file extensions
        output_format (str): Output format (e.g., 'GTiff', 'HFA', 'ENVI')

    Returns:
        None
    """
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Open reference image and get its projection and transformation parameters
    ref_ds = gdal.Open(ref_img_path)
    ref_proj = ref_ds.GetProjection()
    ref_geotrans = ref_ds.GetGeoTransform()
    
    # Extract pixel dimensions from reference image
    ref_pixelWidth = ref_geotrans[1]
    ref_pixelHeight = ref_geotrans[5]
    
    # Convert input formats to lowercase for case-insensitive comparison
    input_formats = tuple(fmt.lower() for fmt in input_formats)
    
    # Process each file in the source directory
    for filename in os.listdir(src_img_path):
        if filename.lower().endswith(input_formats):
            src_file = os.path.join(src_img_path, filename)
            
            # Determine output file extension based on format
            output_ext = {
                'GTiff': '.tif',
                'HFA': '.img',
                'ENVI': '.dat'
            }.get(output_format, '.tif')
            
            # Generate output filename
            base_name = os.path.splitext(filename)[0]
            output_file = os.path.join(output_dir, f"reprojected_{base_name}{output_ext}")
            
            try:
                # Open source image
                src_ds = gdal.Open(src_file)
                
                if src_ds is None:
                    print(f"Failed to open file: {filename}")
                    continue
                
                # Set up warping options for reprojection
                warp_options = gdal.WarpOptions(
                    dstSRS=ref_proj,
                    format=output_format,
                    xRes=ref_pixelWidth if match_resolution else None,
                    yRes=-ref_pixelHeight if match_resolution else None
                )
                
                # Perform the reprojection
                gdal.Warp(output_file, src_ds, options=warp_options)
                
                # Close the source dataset
                src_ds = None
                
                print(f"Processed: {filename}")
                
            except Exception as e:
                # Handle any exceptions that occur during processing
                print(f"Error processing file {filename}: {str(e)}")
                continue
    
    # Close the reference dataset
    ref_ds = None
    print("Batch reprojection completed!")