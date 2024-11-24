import os
from osgeo import gdal

# 启用异常处理
gdal.UseExceptions()

def batch_reprojection(src_img_path, ref_img_path, output_dir, match_resolution=True, 
                   input_formats=('.tif','.tiff','.img','.dat','.hdf'),
                   output_format='GTiff'):
    """
    批量转投影函数
    
    Parameters:
    src_img_path: 需要转投影的源图像文件夹路径
    ref_img_path: 参考图像路径(用于获取目标投影)
    output_dir: 输出文件夹路径
    match_resolution: 是否匹配参考图像的分辨率
    input_formats: 支持的输入文件格式元组
    output_format: 输出文件格式(默认GTiff)
                  支持的格式包括:'GTiff','HFA'(Erdas Imagine),'ENVI'等
    """
    
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 读取参考图像
    ref_ds = gdal.Open(ref_img_path)
    ref_proj = ref_ds.GetProjection()
    ref_geotrans = ref_ds.GetGeoTransform()
    
    # 获取参考图像的分辨率
    ref_pixelWidth = ref_geotrans[1]
    ref_pixelHeight = ref_geotrans[5]
    
    # 将所有支持的格式转换为小写，方便后续比较
    input_formats = tuple(fmt.lower() for fmt in input_formats)
    
    # 遍历源文件夹中的所有支持格式的文件
    for filename in os.listdir(src_img_path):
        # 检查文件扩展名(不区分大小写)
        if filename.lower().endswith(input_formats):
            src_file = os.path.join(src_img_path, filename)
            
            # 根据输出格式设置输出文件扩展名
            output_ext = {
                'GTiff': '.tif',
                'HFA': '.img',
                'ENVI': '.dat'
            }.get(output_format, '.tif')
            
            # 设置输出文件名(更改扩展名)
            base_name = os.path.splitext(filename)[0]
            output_file = os.path.join(output_dir, f"reprojected_{base_name}{output_ext}")
            
            try:
                # 读取源图像
                src_ds = gdal.Open(src_file)
                
                if src_ds is None:
                    print(f"无法打开文件: {filename}")
                    continue
                
                # 设置重投影参数
                warp_options = gdal.WarpOptions(
                    dstSRS=ref_proj,
                    format=output_format,
                    xRes=ref_pixelWidth if match_resolution else None,
                    yRes=-ref_pixelHeight if match_resolution else None
                )
                
                # 执行重投影
                gdal.Warp(output_file, src_ds, options=warp_options)
                
                # 关闭数据集
                src_ds = None
                
                print(f"已处理: {filename}")
                
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {str(e)}")
                continue
    
    ref_ds = None
    print("批量转投影完成!")

# # 使用示例
# src_folder = r"C:\data\MCD15_NM_20244_fill"  # 源图像文件夹
# ref_image = r"G:\2024\2024-01-01\2024-01-01_Mosaic.tif"   # 参考图像
# out_folder = r"C:\Users\RS\Pictures\test"         # 输出文件夹

# # 转投影更改分辨率
# batch_reprojection(
#     src_folder, 
#     ref_image, 
#     out_folder
# )

# # 转投影不更改分辨率
# batch_reprojection(
#     src_folder, 
#     ref_image, 
#     out_folder, 
#     match_resolution=False
# )

# # 自定义输入格式和输出格式，转投影更改分辨率
# batch_reprojection(
#     src_folder, 
#     ref_image, 
#     out_folder,
#     input_formats=('.img', '.tif', '.dat'),  # 指定输入格式
#     output_format='HFA'  # 指定输出格式
# )

# # 自定义输入格式和输出格式，转投影不更改分辨率
# batch_reprojection(
#     src_folder, 
#     ref_image, 
#     out_folder,
#     match_resolution=False,
#     input_formats=('.img'),  # 指定输入格式
#     output_format='GTiff'    # 指定输出格式
# )