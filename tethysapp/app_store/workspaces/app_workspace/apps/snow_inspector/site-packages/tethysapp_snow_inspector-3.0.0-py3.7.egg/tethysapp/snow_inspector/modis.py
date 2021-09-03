import math
import datetime
import png
import urllib.request
import urllib.error
import urllib.parse

from django.http import JsonResponse
from django.shortcuts import render_to_response

"""
Convert (lat, lon) to the proper tile number
Taken from http://wiki.openstreetmap.org/wiki/Tilenames#Lon..2Flat._to_tile_numbers_2
"""


def deg2num(lat_deg, lon_deg, zoom):
    tileSize = 256
    #zoom = 8
    lat_rad = math.radians(float(lat_deg))
    n = 2.0 ** zoom
    xtilef = (float(lon_deg) + 180.0) / 360.0 * n
    xtile = int(xtilef)
    xpixel = int((xtilef - float(xtile)) * tileSize)
    ytilef = (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n
    ytile = int(ytilef)
    ypixel = int((ytilef - float(ytile)) * tileSize)

    return (xtile, ytile, xpixel, ypixel)


def getTileURL(xtile, ytile, date, zoom, layer, level):
    baseURL = 'http://map1.vis.earthdata.nasa.gov/wmts/epsg3857/best/' + \
              '{0}/default/{1}/{2}{3}/{4}/{5}/{6}.png'
    if layer is None:
        layer = 'MODIS_Terra_NDSI_Snow_Cover'
    tileMatrix = 'GoogleMapsCompatible_Level'
    if level is None:
        level = '8'
    time = date.strftime("%Y-%m-%d")
    #zoom = 8
    return baseURL.format(layer, time, tileMatrix, level, zoom, ytile, xtile)


def getTileURL2(xtile, ytile, date, zoom, layer):
    # need layer, time, tileMatrix, zoom, ytile, xtile
    baseURL = 'http://map1.vis.earthdata.nasa.gov/wmts/epsg4326/best/' + \
              '{0}/default/{1}/{2}/{3}/{4}/{5}.png'
    if layer is None:
        layer = 'MODIS_Terra_NDSI_Snow_Cover'
    time = date.strftime("%Y-%m-%d")
    tileMatrix = '500m'
    return baseURL.format(layer, time, tileMatrix, zoom, ytile, xtile)


def getTileURLTemplate(xtile, ytile, zoom, layer):
    # I need the tileMatrix, correct zoom, xtile and ytile
    baseURL = 'http://map1.vis.earthdata.nasa.gov/wmts/epsg4326/best/' + \
              '{0}/default/{1}/{2}/{3}/{4}/{5}.png'
    #layer = 'MODIS_Terra_NDSI_Snow_Cover'
    #tileMatrix = 'GoogleMapsCompatible_Level'
    tileMatrix = '500m'
    time = 'DATE_PLACEHOLDER'
    #zoom = 7
    return baseURL.format(layer, time, tileMatrix, zoom, ytile, xtile)


def getTimeSeries(lat, lon, beginDate, endDate, zoom, layer=None, level=None):
    nDays = (endDate - beginDate).days
    datelist = [beginDate + datetime.timedelta(days=x) for x in range(0, nDays)]
    #zoom = 7
    xtile, ytile, xpixel, ypixel = deg2num(lat, lon, zoom)
    ts = []
    for d in datelist:
        url = getTileURL(xtile, ytile, d, zoom, layer, level)
        pixel_val = getImage(url, ypixel, xpixel)
        snow_val = pixelValueToSnowPercent(pixel_val, layer)
        ts.append(snow_val)
    print(ts)
    return ts


def getTimeSeries2(lat, lon, beginDate, endDate, zoom, layer):
    nDays = (endDate - beginDate).days
    datelist = [beginDate + datetime.timedelta(days=x) for x in range(0, nDays)]
    xtile, ytile, xpixel, ypixel = deg2num(lat, lon, zoom)
    ts = []
    for d in datelist:
        url = getTileURL(xtile, ytile, d, zoom)
        pixel_val = getImage(url, ypixel, xpixel)
        snow_percent = pixelValueToSnowPercent(pixel_val, layer)
        ts.append(snow_percent)
    return ts


def pixelValueToSnowPercent(pixel_val, layer_name):  # image_date used to be a parameter
    # the GIBS imagery service uses an "indexed image" png format.
    # each pixel has an index (between 0 and 255)
    # the built-in PNG color table is then used to convert each index to
    # the displayed (r,g,b) color.

    if layer_name == "MODIS_Terra_NDSI_Snow_Cover":
        snow_val = pixel_val

    elif layer_name == "SMAP_L4_Snow_Mass":
        if pixel_val > 4:
            extra = 0.1 * int((pixel_val - 4) / 8)
            snow_val = (pixel_val * 0.8) - 0.8 - extra - 0.1
        elif pixel_val == 0:
            snow_val = 0
        elif pixel_val <= 4:
            snow_val = pixel_val * 0.8 - 0.8
    elif layer_name == "AMSR2_Snow_Water_Equivalent":
        snow_val = pixel_val

    return (math.floor(snow_val * 10) / 10)  # makes value a float with one decimal (brought down, not approximated)


# function used so that pixel values above chart go to zero
def pixelSnowVal(pixel_val, layer_name):
    if layer_name == "MODIS_Terra_NDSI_Snow_Cover":
        if pixel_val > 100:
            snow_val = 0
        else:
            snow_val = pixel_val
    elif layer_name == "SMAP_L4_Snow_Mass":
        if pixel_val > 4:
            extra = 0.1 * int((pixel_val - 4) / 8)
            snow_val = (pixel_val * 0.8) - 0.8 - extra - 0.1
        elif pixel_val == 0:
            snow_val = 0
        elif pixel_val <= 4:
            snow_val = pixel_val * 0.8 - 0.8
    elif layer_name == "AMSR2_Snow_Water_Equivalent":
        if pixel_val > 40:
            snow_val = 0
        else:
            snow_val = 2 * pixel_val

    return (math.floor(snow_val * 10) / 10)  # makes value a float with one decimal (brought down, not approximated)


def xCoordinateToLongitude(x, zoom):
    return float(x) / (2.0 ** zoom) * 360.0 - 180.0


def yCoordinateToLatitude(y, zoom):
    n = math.pi - (2 * math.pi * float(y)) / (2 ** zoom)
    lat_rad = math.atan(math.sinh(n))
    return lat_rad * (180.0 / math.pi)


def tileBoundsLonLat(x, y, zoom):
    xMin = xCoordinateToLongitude(x, zoom)
    yMin = yCoordinateToLatitude(y, zoom)
    xMax = xCoordinateToLongitude(x + 1, zoom)
    yMax = yCoordinateToLatitude(y + 1, zoom)
    return (xMin, yMin, xMax, yMax)


def getImage(url, rowpixel, colpixel):
    print(url)
    r = png.Reader(file=urllib.request.urlopen(url))
    w, h, pixels, metadata = r.read()
    pxlist = list(pixels)
    v = pxlist[rowpixel][colpixel]
    return v


def getImageVals(url):
    r = png.Reader(file=urllib.request.urlopen(url))
    w, h, pixels, metadata = r.read()
    pxlist = list(pixels)
    return pxlist


def process_query(request):
    # default value for lat, lon
    lat = '50'
    lon = '15'
    start = datetime.datetime.today().strftime("%Y-%m-%d")
    end = (datetime.datetime.today() - datetime.timedelta(days=365)).strftime("%Y-%m-%d")

    if request.GET:
        lat = request.GET["lat"]
        lon = request.GET["lon"]
        start = request.GET["start"]
        end = request.GET["end"]

        if request.GET["start"]:
            startdate = datetime.datetime.strptime(start, "%Y-%m-%d")
        if request.GET["end"]:
            enddate = datetime.datetime.strptime(end, "%Y-%m-%d")

    context = {'lat': lat, 'lon': lon, 'startdate': start, 'enddate': end}
    return context


def get_site_name(lat, lon):
    lat_name = "%0.4fN" % lat
    if lat < 0:
        lat_name = "%0.4fS" % (-1 * lat)
    lon_name = "%0.4fE" % lon
    if lon < 0:
        lon_name = "%0.4fW" % (-1 * lon)

    return lat_name + lon_name


def format_time_series(startDate, ts, nodata_value):
    nDays = len(ts)
    datelist = [startDate + datetime.timedelta(days=x) for x in range(0, nDays)]
    formatted_ts = []
    for i in range(0, nDays):
        formatted_val = ts[i]
        if (formatted_val is None):
            formatted_val = nodata_value
        formatted_date = datelist[i].strftime('%Y-%m-%dT%H:%M:%S')
        formatted_ts.append({'date': formatted_date, 'val': formatted_val})

    return formatted_ts


def get_data_for_pixel(request):
    """
    Controller that will show the snow data for a specific pixel in WaterML format
    """
    start = datetime.datetime.today().strftime("%Y-%m-%d")
    end = (datetime.datetime.today() - datetime.timedelta(days=365)).strftime("%Y-%m-%d")

    if request.GET:
        x = request.GET["x"]
        y = request.GET["y"]
        start = request.GET["start"]
        end = request.GET["end"]

        if request.GET["start"]:
            startdate = datetime.datetime.strptime(start, "%Y-%m-%d")
        if request.GET["end"]:
            enddate = datetime.datetime.strptime(end, "%Y-%m-%d")

    context = {'x': x, 'y': y, 'startdate': start, 'enddate': end}
    # pass url of tile to output
    zoom = 16
    lon = xCoordinateToLongitude(x, zoom)
    lat = yCoordinateToLatitude(y, zoom)
    ts = getTimeSeries(lat, lon, startdate, enddate)
    nodata_value = -9999
    time_series = format_time_series(startdate, ts, nodata_value)
    site_name = str(x) + '-' + str(y)
    context = {'lat': lat, 'lon': lon, 'startdate': start, 'enddate': end, 'site_name': site_name,
               'time_series': time_series}

    xmlResponse = render_to_response('snow_inspector/waterml.xml', context)
    xmlResponse['Content-Type'] = 'application/xml;'
    return xmlResponse


def get_data_json(request):
    """
    Controller that will show the snow data in Json format
    """
    lat = '50'
    lon = '15'
    start = datetime.datetime.today().strftime("%Y-%m-%d")
    end = (datetime.datetime.today() - datetime.timedelta(days=365)).strftime("%Y-%m-%d")

    if request.GET:
        lat = request.GET["lat"]
        lon = request.GET["lon"]
        start = request.GET["start"]
        end = request.GET["end"]
        layer = request.GET["layer"]
        level = request.GET["level"]
        zoom = request.GET["zoom"]

        if request.GET["start"]:
            startdate = datetime.datetime.strptime(start, "%Y-%m-%d")
        if request.GET["end"]:
            enddate = datetime.datetime.strptime(end, "%Y-%m-%d")

    context = {'lat': lat, 'lon': lon, 'startdate': start, 'enddate': end}
    # pass url of tile to output
    #zoom = 7
    zoom = int(zoom)

    xtile, ytile, xpixel, ypixel = deg2num(lat, lon, zoom)
    tile = getTileURLTemplate(xtile, ytile, zoom, layer)

    ts = getTimeSeries(lat, lon, startdate, enddate, zoom, layer, level)
    return JsonResponse({"query": context, "tile": tile, "xpixel": xpixel, "ypixel": ypixel, "data": ts})


def get_data_waterml(request):
    """
    Controller that will show the data in WaterML 1.1 format
    """
    lat = '50'
    lon = '15'
    start = datetime.datetime.today().strftime("%Y-%m-%d")
    end = (datetime.datetime.today() - datetime.timedelta(days=365)).strftime("%Y-%m-%d")
    layer = "MODIS_Terra_NDSI_Snow_Cover"
    level = "8"
    zoom = 8

    if request.GET:
        lat = request.GET["lat"]
        lon = request.GET["lon"]
        start = request.GET["start"]
        end = request.GET["end"]
        layer = request.GET["layer"]

        if request.GET["start"]:
            startdate = datetime.datetime.strptime(start, "%Y-%m-%d")
        if request.GET["end"]:
            enddate = datetime.datetime.strptime(end, "%Y-%m-%d")

    #zoom = 8
    nodata_value = -9999
    ts = getTimeSeries(lat, lon, startdate, enddate, zoom, layer, level)
    time_series = format_time_series(startdate, ts, nodata_value)
    site_name = get_site_name(float(lat), float(lon))
    context = {'lat': lat, 'lon': lon, 'startdate': start, 'enddate': end, 'site_name': site_name,
               'time_series': time_series}

    xmlResponse = render_to_response('snow_inspector/waterml.xml', context)
    xmlResponse['Content-Type'] = 'application/xml'
    xmlResponse['content-disposition'] = "attachment; filename=output-time-series.xml"
    return xmlResponse


# gets all of the tiles that are inside or overlap the bounding box
def getTilesInView(lonmin, latmin, lonmax, latmax, tileDate, zoom, layer, level):
    tiles = []
    tileInfos = []
    #zoom = 8

    # upper left
    ulX, ulY, ulpixelXUL, ulpixelYUL = deg2num(latmax, lonmin, zoom)
    ulTile = getTileURL(ulX, ulY, tileDate, zoom, layer, level)
    (xLeft, yTop, xRight, yBottom) = getPixelsInTile(ulX, ulY, lonmin, latmin, lonmax, latmax, zoom)
    tile_ul = ({"url": ulTile, "xTile": ulX, "yTile": ulY,
                "xPixelLeft": xLeft, "yPixelTop": yTop, "xPixelRight": xRight, "yPixelBottom": yBottom})

    # upper right
    urX, urY, urpixelX, urpixelY = deg2num(latmax, lonmax, zoom)
    urTile = getTileURL(urX, urY, tileDate, zoom, layer, level)
    (xLeft, yTop, xRight, yBottom) = getPixelsInTile(urX, urY, lonmin, latmin, lonmax, latmax, zoom)
    tile_ur = ({"url": urTile, "xTile": urX, "yTile": urY,
                "xPixelLeft": xLeft, "yPixelTop": yTop, "xPixelRight": xRight, "yPixelBottom": yBottom})

    # lower left
    llX, llY, llpixelX, llpixelY = deg2num(latmin, lonmin, zoom)
    llTile = getTileURL(llX, llY, tileDate, zoom, layer, level)
    (xLeft, yTop, xRight, yBottom) = getPixelsInTile(llX, llY, lonmin, latmin, lonmax, latmax, zoom)
    tile_ll = ({"url": llTile, "xTile": llX, "yTile": llY,
                "xPixelLeft": xLeft, "yPixelTop": yTop, "xPixelRight": xRight, "yPixelBottom": yBottom})

    # lower right
    lrX, lrY, lrpixelX, lrpixelY = deg2num(latmin, lonmax, zoom)
    lrTile = getTileURL(lrX, lrY, tileDate, zoom, layer, level)
    (xLeft, yTop, xRight, yBottom) = getPixelsInTile(lrX, lrY, lonmin, latmin, lonmax, latmax, zoom)
    tile_lr = ({"url": lrTile, "xTile": lrX, "yTile": lrY,
                "xPixelLeft": xLeft, "yPixelTop": yTop, "xPixelRight": xRight, "yPixelBottom": yBottom})

    # in between
    tileMinRow = tile_ul['yTile']
    tileMaxRow = tile_ll['yTile']
    tileMinCol = tile_ul['xTile']
    tileMaxCol = tile_ur['xTile']

    nTileCols = tileMaxCol - tileMinCol + 1
    nTileRows = tileMaxRow - tileMinRow + 1

    for tileRow in range(tileMinRow, tileMaxRow + 1):
        for tileCol in range(tileMinCol, tileMaxCol + 1):
            tileURL = getTileURL(tileCol, tileRow, tileDate, zoom, layer, level)
            (xLeft, yTop, xRight, yBottom) = getPixelsInTile(tileCol, tileRow, lonmin, latmin, lonmax, latmax, zoom)
            tileInfo = ({"url": tileURL, "xTile": tileCol, "yTile": tileRow,
                         "xPixelLeft": xLeft, "yPixelTop": yTop, "xPixelRight": xRight, "yPixelBottom": yBottom})
            tiles.append(tileURL)
            tileInfos.append(tileInfo)

    return tileInfos


def getPixelsInTile(tileX, tileY, lonmin, latmin, lonmax, latmax, zoom):
    tileXmin, tileYmin, xPixelLeft, yPixelTop = deg2num(latmax, lonmin, zoom)
    if (tileXmin == tileX):
        xPixelMin = xPixelLeft
    else:
        xPixelMin = 0

    # xPixelRight
    tileXmax, tileYmax, xPixelRight, yPixelBottom = deg2num(latmin, lonmax, zoom)
    if (tileXmax == tileX):
        xPixelMax = xPixelRight
    else:
        xPixelMax = 255

    # yPixelTop
    if (tileYmin == tileY):
        yPixelMin = yPixelTop
    else:
        yPixelMin = 0

    # yPixelBottom
    if (tileYmax == tileY):
        yPixelMax = yPixelBottom
    else:
        yPixelMax = 255

    return (xPixelMin, yPixelMin, xPixelMax, yPixelMax)


def get_zoom(zoom):
    if zoom == 8:
        zoom2 = 16
    if zoom == 6:
        zoom2 = 14
    return zoom2


# gets the pixel borders for the web Mercator mapX, mapY
def get_pixel_borders2(request):
    if request.GET:
        lonmin = float(request.GET["lonmin"])
        latmin = float(request.GET["latmin"])
        lonmax = float(request.GET["lonmax"])
        latmax = float(request.GET["latmax"])
        layer = request.GET["layer"]
        level = request.GET["level"]  # not used yet
        zoom = request.GET["zoom"]  # not used yet
        tileDate = datetime.datetime.strptime(request.GET["date"], "%Y-%m-%d")

        # making zoom a number
        zoom = int(zoom)

        # get zoom for big tiles
        zoom2 = get_zoom(zoom)

        # to get the bottom-right
        lon = lonmax
        lat = latmin

        boundaryList = []
        tileId = 0

        # check tiles in view
        tiles = getTilesInView(lonmin, latmin, lonmax, latmax, tileDate, zoom, layer, level)

        # json feature list
        featureList = {"type": "FeatureCollection", "features": []}

        # for each tile...
        for tile in tiles:
            bigTileLon = xCoordinateToLongitude(tile["xTile"], zoom)
            bigTileLat = yCoordinateToLatitude(tile["yTile"], zoom)

            startTileX, startTileY, xPixel, yPixel = deg2num(bigTileLat, bigTileLon, zoom2)
            vals = getImageVals(tile["url"])

            for i in range(tile["yPixelTop"], tile["yPixelBottom"] + 1):
                for j in range(tile["xPixelLeft"], tile["xPixelRight"] + 1):
                    tileY = startTileY + i
                    tileX = startTileX + j
                    tileId = tileId + 1
                    pixelVal = vals[i][j]

                    snowVal = pixelValueToSnowPercent(pixelVal, layer)

                    minX, minY, maxX, maxY = tileBoundsLonLat(tileX, tileY, zoom2)
                    pixel = {"id": tileId, "pixelval": snowVal, "minX": minX, "minY": minY, "maxX": maxX, "maxY": maxY}
                    boundaryList.append(pixel)

                    newF = {
                        "type": "Feature",
                        "properties": {
                            "id": tileId,
                            "val": snowVal
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [minX, minY],
                                [maxX, minY],
                                [maxX, maxY],
                                [minX, maxY],
                                [minX, minY]
                            ]]
                        }
                    }
                    featureList["features"].append(newF)

    return JsonResponse(featureList)
