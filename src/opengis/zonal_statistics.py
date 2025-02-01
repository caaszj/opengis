import geopandas as gpd
from rasterstats import zonal_stats

def calculate_zonal_statistics(vector_path, raster_path, stats_list, output_path):
    """
    Calculate zonal statistics for raster data within polygon regions and save the results.

    Parameters:
        vector_path (str): Vector data file path (e.g., Shapefile).
        raster_path (str): Raster data file path (e.g., GeoTIFF).
        stats_list (list): List of statistical metrics to calculate (e.g., ['mean', 'max', 'min', 'sum', 'std']).
        output_path (str): Output file path for saving results (e.g., Shapefile path).

    Returns:
        gpd.GeoDataFrame: GeoDataFrame containing statistical results and geometry information.
    """
    # 1. Load vector data
    gdf = gpd.read_file(vector_path)

    # 2. Calculate zonal statistics
    results = zonal_stats(
        vectors=gdf,          # Input polygon data
        raster=raster_path,   # Input raster data
        stats=stats_list,     # Statistical metrics to calculate
        geojson_out=True      # Include geometry information in results
    )

    # 3. Convert results to GeoDataFrame
    results_gdf = gpd.GeoDataFrame.from_features(results)

    # 4. Save results
    results_gdf.to_file(output_path)
    print(f"Results saved to: {output_path}")

    return results_gdf

if __name__ == "__main__":
    # Usage example
    vector_path = "data/watersheds.shp"  # Path to your vector file (e.g., watershed boundaries)
    raster_path = "data/precipitation.tif"  # Path to your raster file (e.g., precipitation data)
    output_path = "data/watershed_stats.shp"  # Path for saving results
    
    # Define statistics to calculate
    stats_list = ['mean', 'max', 'min', 'sum', 'std']
    
    # Calculate zonal statistics
    result = calculate_zonal_statistics(
        vector_path=vector_path,
        raster_path=raster_path,
        stats_list=stats_list,
        output_path=output_path
    )
    
    # Print the first few rows of results
    print("\nFirst few rows of the results:")
    print(result.head())