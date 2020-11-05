# Demonstration Notebooks

We demonstrate the RABASAR multitemporal denoising on ALOS-1 and UAVSAR Images.

## Outline

+ Download data according using instructions
+ Update `config.json`.
+ Run through notebooks 0 - 4.

### UAVSAR at Waxlake.

1. Follow the directions in the [uavsar_waxlake/readme.md](uavsar_waxlake/readme.md). Once completed, there should be `uavsar_waxlake/data_original_tiff` with the RTC images from UAVSAR. Check with QGIS or another GIS viewer.

2. Make sure `config.json` is properly configured.

3. Run the notebooks in order.

4. Inspect the products in `out/uavsar_waxlake_tv/` or `out/uavsar_waxlake_bm3d/` depending on the regularizer.

Note this could in theory be adapted at other sites at the [UAVSAR Data Portal](https://uavsar.jpl.nasa.gov/cgi-bin/data.pl) that have the newly added `*.rtc` file (this indicates the pixelwise multiplicative factor for the radiometric and terrain correction). However, note we had to manually download numerous files and organize them. This was quite time-intensive. Moreover, the UAVSAR data is not distributed with gdal-readable metadata so we needed to reformat these images so that we can use our GIS tools as usual.

### ALOS-1 at Waxlake.

1. Follow the directions in the [alos1_waxlake](alos1_waxlake/readme.md). Once completed, there should be `alos1_waxlake/data_original_tiff` with the RTC images from ALOS-1. Check with QGIS or another GIS viewer.

2. Make sure `config.json` is properly configured as below.

3. Run the notebooks in order.

4. Inspect the products in `out/alos1_waxlake_tv/` or `out/alos1_waxlake_bm3d/` depending on the regularizer.

Note this could more easily reproduced (relative to UAVSAR) because of the [asf search tool](https://search.asf.alaska.edu/) which produces a python script for downloading time series determined via this GUI.

### Example Config Files

#### TV

+ ALOS-1 @ the Waxlake
  
  ```
  {
    "sensor": "alos1",
    "site": "waxlake",
    "regularizer": "tv",
    "spatial_weight": 1.0,
    "temporal_average_spatial_weight": 1.0,
    "ratio_weight": 1.0
  }
  ```

+ UAVSAR @ the Waxlake

  ```
  {
    "sensor": "alos1",
    "site": "waxlake",
    "regularizer": "tv",
    "spatial_weight": 1.0,
    "temporal_average_spatial_weight": 1.0,
    "ratio_weight": 1.0
  }
  ```

#### BM3D

+ ALOS-1 @ the Waxlake
  
  ```
  {
    "sensor": "alos1",
    "site": "waxlake",
    "regularizer": "bm3d",
    "spatial_weight": 0.05,
    "temporal_average_spatial_weight": 0.005,
    "ratio_weight": 0.05
  }
  ```

+ UAVSAR @ the Waxlake

  ```
  {
    "sensor": "alos1",
    "site": "waxlake",
    "regularizer": "bm3d",
    "spatial_weight": 0.05,
    "temporal_average_spatial_weight": 0.005,
    "ratio_weight": 0.05
  }
  ```


### Remarks about BM3D 

The `bm3d` regularizer is quite complex and thus required many more computational resources. In the notebooks, we only apply the RABASAR with the `bm3d` regularizer to a `1000 x 1000` box otherwise such an application would likely require days to run using the current implementation. Moreover, we also note the weights across the different despeckling tasks (despeckling the ratio image vs. the temporally averaged reference) is also different. We suspect that `bm3d` is more sensitive to smoothness in the image that is de-speckled than `tv`. Fortunately, we were able to use the same parameters for both ALOS-1 and for UAVSAR.
