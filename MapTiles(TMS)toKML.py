import os
import shutil
import mercantile

inputdir = r'C:/pycode/ortho_tiles_input/'
outputdir = r'C:/pycode/ortho_tiles_kml_output/'
rootdir =  'C:/pycode/'

tileext = 'png'
tile_size = 256
tileswne = lambda x, y, z: (0, 0, 0, 0)   # noqa
tx = 0
ty = 0
tz = 0
cx = 0
cy = 0
cz = 0
children = []
title = 'Base'
url = ''
map_tiles = []

args = {}
args['title'] = title
args['south'], args['west'], args['north'], args['east'] = (0, 0, 0, 0)
args['tx'], args['ty'], args['tz'] = tx, ty, tz
args['tileformat'] = tileext

def generate_tileswne(x, y, z):
    y = (2**z - 1) - y                      # converts tms to xyz 
    tile_swne = mercantile.bounds(x, y, z)
    south = tile_swne.south
    west = tile_swne.west
    north = tile_swne.north
    east = tile_swne.east
    return south, west, north, east

def generate_kml(tx, ty, tz, tileext, tile_size, tileswne, title , children=None, **args):
    """
    Template for the KML. Returns filled string.
    """
    if not children:
        children = []

    args['tx'], args['ty'], args['tz'] = tx, ty, tz
    args['tileformat'] = tileext
    if 'tile_size' not in args:
        args['tile_size'] = tile_size

    if 'minlodpixels' not in args:
        args['minlodpixels'] = int(args['tile_size'] / 2)
    if 'maxlodpixels' not in args:
        args['maxlodpixels'] = int(args['tile_size'] * 8)
    if children == []:
        args['maxlodpixels'] = -1

    if tx is None:
        tilekml = False
        args['title'] = title
    else:
        tilekml = True
        args['realtiley'] = ty
        args['title'] = "%d/%d/%d.kml" %(tz , tx , ty)
        args['south'], args['west'], args['north'], args['east'] = generate_tileswne(tx, ty, tz)

    if tx == 0:
        args['drawOrder'] = 2 * tz + 1
    elif tx is not None:
        args['drawOrder'] = 2 * tz
    else:
        args['drawOrder'] = 0
    
    url = ""
    if not url:
        if tilekml:
            url = "../../"
        else:
            url = ""

    s = """<?xml version="1.0" encoding="utf-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>%(title)s</name>
    <description></description>
    <Style>
      <ListStyle id="hideChildren">
        <listItemType>checkHideChildren</listItemType>
      </ListStyle>
    </Style>""" % args
    if tilekml:
        s += """
    <Region>
      <LatLonAltBox>
        <north>%(north).14f</north>
        <south>%(south).14f</south>
        <east>%(east).14f</east>
        <west>%(west).14f</west>
      </LatLonAltBox>
      <Lod>
        <minLodPixels>%(minlodpixels)d</minLodPixels>
        <maxLodPixels>%(maxlodpixels)d</maxLodPixels>
      </Lod>
    </Region>
    <GroundOverlay>
      <drawOrder>%(drawOrder)d</drawOrder>
      <Icon>
        <href>%(realtiley)d.%(tileformat)s</href>
      </Icon>
      <LatLonBox>
        <north>%(north).14f</north>
        <south>%(south).14f</south>
        <east>%(east).14f</east>
        <west>%(west).14f</west>
      </LatLonBox>
    </GroundOverlay>
""" % args

    for cx, cy, cz in children:
        csouth, cwest, cnorth, ceast = generate_tileswne(cx, cy, cz)
        ytile = cy
        s += """
    <NetworkLink>
      <name>%d/%d/%d.%s</name>
      <Region>
        <LatLonAltBox>
          <north>%.14f</north>
          <south>%.14f</south>
          <east>%.14f</east>
          <west>%.14f</west>
        </LatLonAltBox>
        <Lod>
          <minLodPixels>%d</minLodPixels>
          <maxLodPixels>-1</maxLodPixels>
        </Lod>
      </Region>
      <Link>
        <href>%s%d/%d/%d.kml</href>
        <viewRefreshMode>onRegion</viewRefreshMode>
        <viewFormat/>
      </Link>
    </NetworkLink>
        """ % (cz, cx, ytile, args['tileformat'], cnorth, csouth, ceast, cwest,
               args['minlodpixels'], url, cz, cx, ytile)

    s += """      </Document>
</kml>
    """
    return s

# copy input files to output destination
os.chdir(rootdir[:-1])
shutil.copytree( inputdir[:-1], outputdir[:-1])

# reading all TMS tiles 
for r, d, f in os.walk(os.path.normpath(outputdir), topdown=True):   
    for file in f:
        if '.png' in file:
            map_tiles.append([r.split("\\")[-1],file.split('.')[0],r.split("\\")[-2]])
                
    
#   generating base KML
children = []          # child tiles for base KML
z = map_tiles[0][2]    # lowest zoom level in inputdir
for map_tile in map_tiles:
    if z > map_tile[2]: 
        z = map_tile[2]
for map_tile in map_tiles:
    if map_tile[2] == z:
        children.append([int(i) for i in map_tile])
              
if not os.path.exists(outputdir + 'doc.kml'):
    with open(outputdir + 'doc.kml', 'wb') as f:
        f.write(generate_kml(None, None, None, tileext, tile_size, tileswne, title, children).encode('utf-8'))
        print("doc.kml created")
else:
    print("doc.kml already exist")

#  Create a KML file for tile.
for map_tile in map_tiles:
    children = []
    tx,ty,tz = [int(i) for i in map_tile]  
    sub_tiles = [[tx*2,ty*2,tz+1],[tx*2+1,ty*2,tz+1],[tx*2,ty*2+1,tz+1],[tx*2+1,ty*2+1,tz+1]] 
    for sub_tile in sub_tiles:
        if [str(i) for i in sub_tile] in map_tiles:
            children.append(sub_tile)
    kmlfilename = outputdir + str(tz) + '/' + str(tx) + '/' + str(ty) + '.kml'
    print(kmlfilename)
    if not os.path.exists(kmlfilename):
        with open(kmlfilename, 'wb') as f:
            f.write(generate_kml(tx, ty, tz, tileext, tile_size, tileswne, title, children).encode('utf-8'))
            print(" kml file created")
    else:
        print("kml file already exist")
    
