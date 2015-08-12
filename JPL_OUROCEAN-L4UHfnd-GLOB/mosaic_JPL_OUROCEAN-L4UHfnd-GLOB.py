import os,subprocess,sys
import re, datetime
import numpy as np
import netCDF4 as nc
import gdal, ogr, osr, numpy

from netCDF4 import Dataset
from gsimporter import Client
from owslib.wms import WebMapService

from geoserver.store import CoverageStore, DataStore, datastore_from_index,\
    coveragestore_from_index, wmsstore_from_index
from geoserver.workspace import Workspace
from geoserver.catalog import Catalog
from geoserver.catalog import FailedRequestError, UploadError
from geoserver.catalog import ConflictingDataError
from geoserver.resource import FeatureType, Coverage
from geoserver.support import DimensionInfo

# Gs Catalog and Importer
"""
    The following variables must contain a reachable and valid REST URL of the
    GeoServer where the mosaics have been configured.
    
    The GeoServer USERNAME and PASSWORD *are not* the ones configured on GeoNode.
    It is mandatory to create a GeoServer manager user (by default admin/geoserver)
    with WRITE (or ADMIN) rights and BASIC AUTH access enabled.
"""
url = "http://localhost:8080/geoserver/rest" # Notice that the URL *must* contain the '/rest' path
_user = "admin" # BASIC AUTH enabled GeoServer USER with WRITE or ADMIN rights
_password = "geoserver" 
# We are going to configure the GeoServer remote clients
gs_catalog = Catalog(url, _user, _password)
gs_uploader = Client(url, _user, _password)

# Input Variables
"""
    The following ones are the variables provided via the command line.
    
    e.g.:
    
    python mosaic_METOFFICE-GLO-SST-L4-NRT-OBS-SKIN-DIU.py METOFFICE-GLO-SST-L4-NRT-OBS-SKIN-DIU.nc temperature METOFFICE_GLO_SST_L4_NRT_OBS_SKIN_DIU
                                                           sys.argv[1]                              sys.argv[2] sys.argv[3] 
"""
file_nc = sys.argv[1]                                     # Filesystem path of the input NetCDF4 file e.g.: path_to_the_file/METOFFICE-GLO-SST-L4-NRT-OBS-SKIN-DIU.nc
vname = sys.argv[2]                                       # Name of the variable to extract e.g.: temperature
target_bbox = sys.argv[3] if len(sys.argv) > 3 else None  # Subset Area e.g.: -115.561581,-2.270676,-40.722711,36.750010
target_store = sys.argv[4] if len(sys.argv) > 4 else None # Name of the existing Mosaic in GeoServer e.g.: JPL_OUROCEAN-L4UHfnd-GLOB-v01-fv01_0-G1SST_temperature

# NetCDF 4
fid = nc.Dataset(file_nc, 'r', format='NETCDF4')

print 'Extracting Variable => %s...' % vname

"""
    Filling the spatio-temporal arrays with the NetCDF Variables values.
"""
print 'Extracting geolocation data...'
lat_nc = fid.variables['lat']
lats = np.asarray(lat_nc[:])
lon_nc = fid.variables['lon']
lons = np.asarray(lon_nc[:])
time_nc = fid.variables['time']
time_counter = np.asarray(time_nc[:])

fid.close()

"""
    We are going to use GDAL in order to Read the NetCDF file, extract
    the data for each band and dump it as single GeoTIFFs.
    
    Each GeoTIFF will contain the variable data on the selected region
    associated to a temporal instant. The GeoTIFFs will be used to populate
    the Mosaic as new granules.
"""
# GDAL DataSet
dataset=gdal.Open( file_nc, gdal.GA_ReadOnly )

# Create gtif
format = 'GTiff'
driver = gdal.GetDriverByName(format)
driver.Register()

"""
    We are making the assumption that the original data is distributed 
    on a regular geodetic grid.
"""
# set the reference info
prjWKT="WGS84"
srs = osr.SpatialReference()
srs.SetWellKnownGeogCS(prjWKT)
prjWKT=srs.ExportToWkt()

"""
    Global variables used to subset the data.
"""
trg_win_x0 = 0
trg_win_y0 = 0
trg_win_x1 = 0
trg_win_y1 = 0

for subdataset in dataset.GetSubDatasets():
    # Looking for the "variable" specified by the user among the NetCDF SubDatasets
    if re.match('\[.*\] .*'+vname+'.* \(.*\)', subdataset[1]):
        
        print "Fetching SubDataset -> "+subdataset[1]
        
        lc_data = gdal.Open ( subdataset[0] )
        
        """
            The following steps are necessary since sometimes the GeoTransform is not
            correctly set (or handled by GDAL) in the original DataSet.
            
            Therefore we are going to compute the GeoTransform accordingly to the 
            assumptions we did before.
        """
        # Computing the full raster resolution
        cols = lc_data.RasterXSize
        rows = lc_data.RasterYSize

        ypixsize= abs(lats[rows-1]-lats[0])/rows
        xpixsize= abs(lons[cols-1]-lons[0])/cols
        
        # Computing the real Upper-Left bound coordinates
        if target_bbox:
            # Getting the target bbox coordinates assuming ['minx', 'miny', 'maxx', 'maxy']
            trg_win_bbox = target_bbox.split(',')
            
            # Computing the number of rows anc cols of the subset area
            rows = int(abs(float(trg_win_bbox[3])-float(trg_win_bbox[1]))/ypixsize)
            cols = int(abs(float(trg_win_bbox[2])-float(trg_win_bbox[0]))/xpixsize)
            
            # Rescaled Upper-Left bounds
            north= float(trg_win_bbox[1])+(ypixsize*rows)-ypixsize/2
            west= float(trg_win_bbox[0])+xpixsize/2

            # Computing the origin of the subset area in the raster space
            y_offset = abs(lats[0]+float(trg_win_bbox[3])+abs(lats[rows-1]-lats[rows-2])/2)/ypixsize # The array is written upside-down
            x_offset = abs(lons[0]-float(trg_win_bbox[0])-abs(lons[1]-lons[0])/2)/xpixsize
            
            # Finally setting the target window in order to subset the data array in the raster space
            trg_win_x0 = int(round(x_offset,0))
            trg_win_y0 = int(round(y_offset,0))
            trg_win_x1 = int(round(cols,0))
            trg_win_y1 = int(round(rows,0))
        else:
            north= lats[0]+(ypixsize*rows)-ypixsize/2
            west= lons[0]+xpixsize/2

            # Getting the full coverage
            trg_win_x0 = 0
            trg_win_y0 = 0
            trg_win_x1 = cols
            trg_win_y1 = rows
        
        # Shift the coordinates in order to remain inside the world [-180,-90,180,90]
        if west > 180 or west < -180:
            west = west - 360
        
        # Computing the real Lower-Right bound coordinates
        south = north - (ypixsize*rows)
        east =  west + (xpixsize*cols)
        
        # Finally setting the target data GeoTransform
        lc_data.SetGeoTransform([ west, xpixsize, 0.0, north, 0.0, -ypixsize ])
    
        print "BBOX: [" + str(west)+" "+str(south)+","+str(east)+" "+str(north) + "]"

        """
            At this point we will dump the raster bands for each time-instant into separate GeoTIFFs
            which will be imported as Mosaic Granules into GeoServer.
        """
        t_index = -1
        rasters = lc_data.RasterCount+1
        for i in range(1, rasters):
            band = lc_data.GetRasterBand(i)
            
            t_index = t_index+1
            time=time_counter[t_index]
            
            #print lc_data.GetMetadata()
            
            time_units = lc_data.GetMetadata()["time#units"] # Trying to extract the time origin from the metadata
            m = re.search('(\d{4}-\d{2}-\d{2})', time_units)
            seconds_since = '1950-01-01' # Assuming '1950-01-01' as default
            if m:
                seconds_since = m.group(1)
            
            """
                Computing the Granule Time Position (assuming ZULU time)
            """
            start_time = seconds_since.split('-')
            st=datetime.datetime(year=int(start_time[0]), month=int(start_time[1]), day=int(start_time[2]), hour=0) + datetime.timedelta(seconds=int(time))
            
            dataType = band.DataType
            nan=band.GetNoDataValue()
            scale=band.GetScale()
            offset=band.GetOffset()
            
            print "NoDATA: [" + str(nan) + "]"
            print "Scale-Factor: [" + str(scale) + "]"
            print "Offset: [" + str(offset) + "]"
            
            """
                Starting the GeoTIFF dump and ingest into GeoServer.
                
                *WARNING*: The time format "%Y%m%dT%H%M%SZ" *must* be the same of the targer Mosaic Layer.
            """
            dst_filename = "./"+vname+"_"+st.strftime("%Y%m%dT%H%M%SZ")+".tif"
            try:
                print "-------------------------------------------------------------\nWriting file : " + dst_filename
                
                dst_ds = driver.Create(dst_filename, cols, rows, 1, gdal.GDT_Float32)

                # top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution
                dst_ds.SetGeoTransform( lc_data.GetGeoTransform() )
                dst_ds.SetProjection( prjWKT )

                # Write data to band 1
                data = band.ReadAsArray(trg_win_x0, trg_win_y0, trg_win_x1, trg_win_y1)
                #data = np.flipud(data)
                
                # Mask zone of raster
                datamask = data-nan
                zoneraster = numpy.ma.masked_array(data, numpy.logical_not(datamask))
                
                dst_ds.GetRasterBand(1).SetNoDataValue(nan)
                """
                    Notice that the data *must* be rescaled and shifted accordingly to the original DataSet Metadata
                """
                dst_ds.GetRasterBand(1).WriteArray(zoneraster*scale+offset)

                # Updating the MetaData for the final GeoTIFF file
                metadata = band.GetMetadata()
                metadata["add_offset"] = '0.0'
                metadata["scale_factor"] = '1.0'
                metadata["_FillValue"] = str(nan)
                
                print metadata
                
                dst_ds.GetRasterBand(1).SetMetadata(metadata)

                # Computing the GDAL Statistics 
                # - optional unless the Mosaic has been forced to take the statistics too; this is usually
                #   done when enabling the GeoServer Dynamic Dimensions
                stats=dst_ds.GetRasterBand(1).GetStatistics(0,1)
                hist =dst_ds.GetRasterBand(1).GetDefaultHistogram( force=1 )
                dst_ds = None
                
                """
                    We are now going to use the GDAL utilities through the command line in order to add internal tiling and overviews to the GeoTIFF
                """
                src_geotiff_file_path = os.path.abspath(dst_filename)
                src_geotiff_filename, src_geotiff_file_extension = os.path.splitext(os.path.abspath(dst_filename))
                trg_geotiff_file_path = src_geotiff_filename + "_cl" + src_geotiff_file_extension

                # gdal_translate allows us to add internal 512x512 tiling to the GeoTIFF; we need to save the result on another file...
                convCommand='gdal_translate -co "TILED=YES" -co "BLOCKXSIZE=512" -co "BLOCKYSIZE=512" ' + '"' + src_geotiff_file_path + '" "' + trg_geotiff_file_path + '" '
                os.system(convCommand)
                
                # gdaladdo allows us to add the overviews to the GeoTIFF
                convCommand='gdaladdo -r average ' + '"' + trg_geotiff_file_path + "'" + ' 2 4 8 16 32'
                os.system(convCommand)
                
                # finally let replace the old GeoTIFF with the new one
                os.remove(src_geotiff_file_path)
                os.rename(trg_geotiff_file_path, src_geotiff_file_path)
                
                """
                    If a target Mosaic Layer has been specified (NOTICE that the Layer *must* exist),
                    we will proceed with the ingestion of the new Granule through the GeoServer Importer.
                """
                if target_store:
                    print "Moving forward with a regular Importer session ..."
                    
                    """
                        First of all we need to compute the new Importer Session ID.
                        
                        In order to do that, we will ask to GeoServer a shortened summary
                        of all the COMPLETED, FAILED or PENDING available Importer Sessions;
                        then we will get the ID of the latest one and increment it by 1 in 
                        order to obtain the new Session ID.
                        
                        In any case this is just a suggestion; GeoServer will automatically
                        assign a new Session ID to the Task if alredy taken.
                        We are doing this small computation since we should be consistent
                        with GeoNode.
                    """
                    importer_sessions = gs_uploader.get_sessions()
                    last_importer_session = importer_sessions[len(importer_sessions)-1]
                    next_id = last_importer_session.id+1
                    
                    import_session = gs_uploader.upload_files(
                        [os.path.abspath(dst_filename)],
                        use_url=False,
                        import_id=next_id,
                        target_store=target_store)
                    
                    #print import_session
                    
                    # Run the import.
                    task = import_session.tasks[0]
                    
                    #print str(task)

                    if import_session.state == 'INCOMPLETE':
                        if task.state != 'ERROR':
                            raise Exception('unknown item state: %s' % task.state)
                    elif import_session.state == 'PENDING':
                        if task.state == 'READY':
                            import_session.commit(False)
                else:
                    print "Skipping Import of the Granules since the 'target_store' has not been specified"
                    
            except Exception as e:
                print "Could not write the GeoTIFF Granule: " + str(e)
                
                import traceback
                traceback.print_exc()
                
                lc_data=None
                dataset=None
                sys.exit(-1)

        """
            It is important to release the locks when the computation has finished.
        """
        lc_data=None
        
"""
    It is important to release the locks when the computation has finished.
"""
dataset=None
