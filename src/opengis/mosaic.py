import os
from osgeo import gdal

def mosaic(path_image, output_dir=None):
    """
    :param path_image: 需要镶嵌影像的路径
    :param output_dir: 输出路径,默认为None时输出到源文件夹
    :return: None
    """
    path = path_image
    # 只获取.tif文件
    path_lists = [f for f in os.listdir(path) if f.lower().endswith('.tif')]
    
    if len(path_lists) < 2:
        print(f"文件夹 {path} 中没有足够的tif影像进行镶嵌。")
        return
        
    print(f"正在处理 {len(path_lists)} 个tif影像......")

    # 首先读取所有影像
    images = [gdal.Open(os.path.join(path, img), gdal.GA_ReadOnly) for img in path_lists]

    # 获取第一个影像的投影信息
    input_proj = images[0].GetProjection()

    first_image_name = os.path.basename(path_lists[0])
    date_part = first_image_name.split('_')[0]

    # 设置gdal.Warp的选项
    options = gdal.WarpOptions(srcSRS=input_proj, dstSRS=input_proj, format='GTiff',
                             resampleAlg=gdal.GRA_NearestNeighbour)

    # 使用gdal.Warp一次性镶嵌所有影像
    output_filename = f"{date_part}_Mosaic.tif"
    
    # 如果指定了输出路径,则使用指定路径;否则使用源文件夹
    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = os.path.join(output_dir, output_filename)
    else:
        output_path = os.path.join(path, output_filename)
        
    gdal.Warp(output_path, images, options=options)

    # 释放影像资源
    for img in images:
        img = None
        del img

    print(f"镶嵌完成,共处理{len(path_lists)}个tif文件")
    print(f"输出文件为：{output_path}")

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
