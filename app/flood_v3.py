import os
import osgeo.gdal as gdal
import numpy as np
from osgeo import osr
import shutil

import time

# Get start time
start_time = time.time()

# --fix data--
dem = ""
slope = ""
veg = ""
water = ""
build = ""
forset = ""
pop = ""
flooded = ""
# --rain data--
datarain = ""
date = ""
asc = ""

new_date = ""
path = "./app"
path2 = "app/"

for file in os.listdir(path):
    if file.endswith(".tif"):
        if file[2] == "d":
            dem = gdal.Open(f"{path}/{file}")
        if file[2] == "s":
            slope = gdal.Open(f"{path}/{file}")
        if file[2] == "v":
            veg = gdal.Open(f"{path}/{file}")
        if file[2] == "w":
            water = gdal.Open(f"{path}/{file}")
        if file[2] == "b":
            build = gdal.Open(f"{path}/{file}")
        if file[2] == "f":
            forset = gdal.Open(f"{path}/{file}")
        if file[2] == "p":
            pop = gdal.Open(f"{path}/{file}")
        if file[2] == "r":
            flooded = gdal.Open(f"{path}/{file}")
    # ------ asc -------
    elif file.endswith(".asc"):
        date = os.path.splitext(str(file))[0]
        asc = str(f"{path}/{file}")
# print(date)

rain_file = "rain_" + date + ".tif"
res_rain_file = "res_rain_" + date + ".tif"
rc_rain_file = "rc_rain_" + date + ".tif"


# ------ new rain.tif --------
def asctotif(ascname):
    drv = gdal.GetDriverByName("GTiff")
    ds_in = gdal.Open(ascname)

    ds_out = drv.CreateCopy(rain_file, ds_in)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(32647)
    ds_out.SetProjection(srs.ExportToWkt())
    ds_in = None
    ds_out = None

print('asc', asc)

asctotif(asc)
# -------------------------------------

for root, dirs, files in os.walk("."):
    for name in files:
        if name.startswith("rain") and name.endswith(".tif"):
            # print(name)
            datarain = gdal.Open("" + name)

# ---- resize rain data----
width = water.RasterXSize
height = water.RasterYSize

gdal.Warp(res_rain_file, datarain, width=width, height=height)

re_rain = None
datarain = None

# ------reclassify rain data------
rc_rain = gdal.Open(res_rain_file)
rain_arr = rc_rain.ReadAsArray()
src_crs = rc_rain.GetProjection()

rain_arr[(rain_arr >= 0) & (rain_arr <= 90)] = 2
rain_arr[(rain_arr > 90) & (rain_arr <= 120)] = 4
rain_arr[(rain_arr > 120) & (rain_arr <= 999)] = 6


driver = gdal.GetDriverByName("GTiff")
dst_ds = driver.Create(
    rc_rain_file, rc_rain.RasterXSize, rc_rain.RasterYSize, 1, gdal.GDT_Int16
)

dst_ds.GetRasterBand(1).WriteArray(rain_arr)

rc_rain = None
dst_ds = None

# ----- cal data ------
rain = gdal.Open(rc_rain_file)

cols = water.RasterXSize
rows = water.RasterYSize

# ------------get band--------------
dem_band = dem.GetRasterBand(1).ReadAsArray()
slope_band = slope.GetRasterBand(1).ReadAsArray()
veg_band = veg.GetRasterBand(1).ReadAsArray()
water_band = water.GetRasterBand(1).ReadAsArray()
build_band = build.GetRasterBand(1).ReadAsArray()
forset_band = forset.GetRasterBand(1).ReadAsArray()
pop_band = pop.GetRasterBand(1).ReadAsArray()
floodband = flooded.GetRasterBand(1).ReadAsArray()
rain_band = rain.GetRasterBand(1).ReadAsArray()

geoTrans = water.GetGeoTransform()

x0 = geoTrans[0]
y0 = geoTrans[3]
x_res = geoTrans[1]
y_res = geoTrans[5]


# =================== cal data =========================
print("start cal")

new = np.zeros((rows, cols), dtype=np.float32)
t = 0
for row in range(rows):
    print("write_data", "\r", (t / (rows)) * 100, end="")
    for col in range(cols):
        new[row, col] = (
            (0.458 * (rain_band[row, col]))
            + (0.123 * (slope_band[row, col]))
            + (0.096 * (dem_band[row, col]))
            + (0.295* floodband[row, col])
            + (
                0.026
                * (
                    water_band[row, col]
                    + veg_band[row, col]
                    + build_band[row, col]
                    + pop_band[row, col]
                    + forset_band[row, col]
                )
            )
        )

    t = t + 1

output_file = "test_f_" + date
driver = gdal.GetDriverByName("GTiff")
outt = driver.Create(output_file, cols, rows, 1, gdal.GDT_Float32)
out_bnd = outt.GetRasterBand(1).WriteArray(new)

print("sett.....")
outt.SetGeoTransform(geoTrans)
proj = water.GetProjection()
outt.SetProjection(proj)

rain = None
dem = None
slope = None
veg = None
water = None
build = None
forset = None
pop = None
flooded = None

outt = None
output_file = None

# ======== clear -9999 ==========
file = gdal.Open("test_f_" + date)

src_array = file.ReadAsArray()
src_array[src_array < 0] = -9999

driver = gdal.GetDriverByName("GTiff")
dst_ds = driver.Create(
    "flood_result_" + date + ".tif",
    file.RasterXSize,
    file.RasterYSize,
    file.RasterCount,
    file.GetRasterBand(1).DataType,
)
dst_ds.SetGeoTransform(file.GetGeoTransform())
dst_ds.SetProjection(file.GetProjection())
dst_ds.GetRasterBand(1).WriteArray(src_array)


file = None
dst_ds = None

print('\n\n\n\n')
# ------ new data folder --------
def new_folder(fname):
    new_date = fname
    if not os.path.exists(fname):
        os.makedirs(fname)

    else:
        i = 1
        while True:
            new_date = f"{fname}_{i}"
            if not os.path.exists(new_date):
                os.makedirs(new_date)
                break
            i += 1
    return new_date

new_date = new_folder(date)
print('date', new_date)

print('\n\n\n\n')
# -------------------------------------

roor_directory = os.getcwd()
current_directory = f"{roor_directory}/{new_date}/"
print("current_directory", current_directory)

raintif = ""
rainresize = ""
rainreclass = ""
rain1 = ""
result = ""

for root, dirs, files in os.walk("."):
    for name in files:
        if "rain_" in name and name.endswith(".tif"):
            raintif = "" + name
        if "res_rain_" in name:
            rainresize = "" + name
        if "rc_rain_" in name:
            rainreclass = "" + name
        if "test_f_" in name:
            rain1 = "" + name
        if "flood_result_" in name and name.endswith(".tif"):
            result = "" + name



# f_name = current_directory + "/" + new_date

unused_file = [raintif, rainresize, rainreclass, rain1]

for file in unused_file:
    if file:
        if os.path.exists(current_directory  + file):
            os.remove(current_directory + file)

shutil.move(f"{roor_directory}/{result}", current_directory + result)
shutil.move(f"{roor_directory}/{asc}", current_directory + asc)

# Get end time
end_time = time.time()

running_time = end_time - start_time
print("Running time:", running_time, "seconds")
