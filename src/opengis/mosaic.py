import os
from osgeo import gdal

def mosaic(path_image, output_dir=None):
    path = path_image
    path_lists = [f for f in os.listdir(path) if f.lower().endswith('.tif')]
    
    if len(path_lists) < 2:
        print(f"Not enough tif images in folder {path} for mosaic.")
        return
        
    print(f"Processing {len(path_lists)} tif images......")

    images = [gdal.Open(os.path.join(path, img), gdal.GA_ReadOnly) for img in path_lists]

    input_proj = images[0].GetProjection()

    first_image_name = os.path.basename(path_lists[0])
    date_part = first_image_name.split('_')[0]

    options = gdal.WarpOptions(srcSRS=input_proj, dstSRS=input_proj, format='GTiff',
                             resampleAlg=gdal.GRA_NearestNeighbour)

    output_filename = f"{date_part}_Mosaic.tif"
    
    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = os.path.join(output_dir, output_filename)
    else:
        output_path = os.path.join(path, output_filename)
        
    gdal.Warp(output_path, images, options=options)

    for img in images:
        img = None
        del img

    print(f"Mosaic completed, processed {len(path_lists)} tif files")
    print(f"Output file: {output_path}")

def get_subfolder_paths(folder_path):
    subfolder_paths = []
    for root, dirs, _ in os.walk(folder_path):
        for dir_name in dirs:
            subfolder_paths.append(os.path.join(root, dir_name))
    return subfolder_paths

def batch_mosaic(folder_path, out_path):
    subfolders = get_subfolder_paths(folder_path)
    for path in subfolders:
        mosaic(path, out_path)
