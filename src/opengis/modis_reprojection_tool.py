import os
from osgeo import gdal
from osgeo import osr
from glob import glob

def modis_to_tif_batch(input_dir, output_dir, target_epsg=None, selected_bands=None, 
                       target_resolution=None, file_pattern="*.hdf"):
    """
    批量处理MODIS HDF文件并转换为GeoTIFF格式
    
    参数:
    input_dir: 输入文件夹路径
    output_dir: 输出文件夹路径
    target_epsg: 目标投影的EPSG代码(可选)
    selected_bands: 需要提取的波段列表(可选)
    target_resolution: 目标分辨率，格式为(x_res, y_res)(可选)
    file_pattern: 文件匹配模式，默认为"*.hdf"
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    hdf_files = glob(os.path.join(input_dir, file_pattern))
    
    if not hdf_files:
        print(f"在 {input_dir} 中没有找到匹配的HDF文件")
        return
    
    total_files = len(hdf_files)
    print(f"找到 {total_files} 个HDF文件待处理")
    
    for index, hdf_file in enumerate(hdf_files, 1):
        try:
            print(f"正在处理文件 {index}/{total_files}: {os.path.basename(hdf_file)}")
            
            base_name = os.path.splitext(os.path.basename(hdf_file))[0]
            hdf_ds = gdal.Open(hdf_file)
            
            if hdf_ds is None:
                print(f"无法打开文件: {hdf_file}")
                continue
            
            subdatasets = hdf_ds.GetSubDatasets()
            
            if selected_bands is None:
                selected_bands = range(len(subdatasets))
            
            for band_index in selected_bands:
                if band_index >= len(subdatasets):
                    print(f"波段 {band_index} 超出范围")
                    continue
                
                subdataset = gdal.Open(subdatasets[band_index][0])
                proj = subdataset.GetProjection()
                geotransform = subdataset.GetGeoTransform()
                data = subdataset.ReadAsArray()
                
                output_file = os.path.join(output_dir, f"{base_name}_band_{band_index}.tif")
                
                driver = gdal.GetDriverByName('GTiff')
                out_ds = driver.Create(output_file, 
                                     subdataset.RasterXSize, 
                                     subdataset.RasterYSize, 
                                     1, 
                                     gdal.GDT_Float32)
                
                out_ds.SetProjection(proj)
                out_ds.SetGeoTransform(geotransform)
                out_ds.GetRasterBand(1).WriteArray(data)
                
                # 如果需要重投影或重采样
                if target_epsg or target_resolution:
                    temp_file = os.path.join(output_dir, f"{base_name}_temp.tif")
                    warp_options = gdal.WarpOptions(
                        resampleAlg=gdal.GRA_Bilinear,
                        xRes=target_resolution[0] if target_resolution else None,
                        yRes=target_resolution[1] if target_resolution else None
                    )
                    
                    if target_epsg:
                        target_srs = osr.SpatialReference()
                        target_srs.ImportFromEPSG(target_epsg)
                        warp_options = gdal.WarpOptions(
                            resampleAlg=gdal.GRA_Bilinear,
                            dstSRS=target_srs.ExportToWkt(),
                            xRes=target_resolution[0] if target_resolution else None,
                            yRes=target_resolution[1] if target_resolution else None
                        )
                    
                    gdal.Warp(temp_file, out_ds, options=warp_options)
                    
                    out_ds = None
                    os.remove(output_file)
                    os.rename(temp_file, output_file)
                
                out_ds = None
                subdataset = None
            
            hdf_ds = None
            print(f"完成文件 {index}/{total_files}")
            
        except Exception as e:
            print(f"处理文件 {hdf_file} 时出错: {str(e)}")
            continue
    
    print("所有文件处理完成！")

def modis_batch_projection(input_dir, output_dir, target_epsg=None, selected_bands=None, 
                              target_resolution=None):
    """
    带有错误处理的处理函数封装
    """
    try:
        if not os.path.exists(input_dir):
            raise ValueError(f"输入目录不存在: {input_dir}")
        
        if not os.path.isdir(input_dir):
            raise ValueError(f"输入路径不是目录: {input_dir}")
        
        modis_to_tif_batch(input_dir, output_dir, target_epsg, selected_bands, target_resolution)
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        raise

# 使用示例
# input_directory = r"C:\Users\data\File\2024-11\New folder"
# output_directory = r"C:\Users\RS\Pictures\test"

# 示例1：基本批量转换
# modis_batch_projection(input_directory, output_directory, selected_bands=[1])

# 示例2：转换为UTM投影，设置分辨率为500米，并只处理特定波段
# modis_batch_projection(
#     input_directory, 
#     output_directory,
#     target_epsg=32649,
#     selected_bands=[1],
#     target_resolution=(500, 500)  # x方向和y方向的分辨率都设为500米
# )