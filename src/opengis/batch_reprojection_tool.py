import os
from osgeo import gdal

gdal.UseExceptions()

def batch_reprojection(src_img_path, ref_img_path, output_dir, match_resolution=True, 
                   input_formats=('.tif','.tiff','.img','.dat','.hdf'),
                   output_format='GTiff'):
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    ref_ds = gdal.Open(ref_img_path)
    ref_proj = ref_ds.GetProjection()
    ref_geotrans = ref_ds.GetGeoTransform()
    
    ref_pixelWidth = ref_geotrans[1]
    ref_pixelHeight = ref_geotrans[5]
    
    input_formats = tuple(fmt.lower() for fmt in input_formats)
    
    for filename in os.listdir(src_img_path):
        if filename.lower().endswith(input_formats):
            src_file = os.path.join(src_img_path, filename)
            
            output_ext = {
                'GTiff': '.tif',
                'HFA': '.img',
                'ENVI': '.dat'
            }.get(output_format, '.tif')
            
            base_name = os.path.splitext(filename)[0]
            output_file = os.path.join(output_dir, f"reprojected_{base_name}{output_ext}")
            
            try:
                src_ds = gdal.Open(src_file)
                
                if src_ds is None:
                    print(f"Failed to open file: {filename}")
                    continue
                
                warp_options = gdal.WarpOptions(
                    dstSRS=ref_proj,
                    format=output_format,
                    xRes=ref_pixelWidth if match_resolution else None,
                    yRes=-ref_pixelHeight if match_resolution else None
                )
                
                gdal.Warp(output_file, src_ds, options=warp_options)
                
                src_ds = None
                
                print(f"Processed: {filename}")
                
            except Exception as e:
                print(f"Error processing file {filename}: {str(e)}")
                continue
    
    ref_ds = None
    print("Batch reprojection completed!")