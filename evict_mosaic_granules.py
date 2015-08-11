import os,subprocess,sys
import re, datetime
import numpy as np
import netCDF4 as nc
import gdal, ogr, osr, numpy

import json

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
#gs_uploader = Client(url, _user, _password)

target_store = sys.argv[1]          # Name of the existing Mosaic in GeoServer e.g.: METOFFICE-GLO-SST-L4-NRT-OBS-SKIN-DIU_temperature
evict_time_threshold = sys.argv[2]  # UTC maximum time; Granules older than this will be deleted

store = gs_catalog.get_store(target_store)
coverages = gs_catalog.mosaic_coverages(store)
granules = gs_catalog.mosaic_granules(coverages['coverages']['coverage'][0]['name'], store, filter='time <= ' + evict_time_threshold) 

print granules["features"]

for feature in granules["features"]:
    print "Purging Granule @time [" + json.dumps(feature["properties"]["time"]) + "]"
    granule_id = feature["id"]
    gs_catalog.mosaic_delete_granule(coverages['coverages']['coverage'][0]['name'], store, granule_id)
    print "Deleting file [" + json.dumps(feature["properties"]["location"]) + "]"
    os.remove(feature["properties"]["location"])
