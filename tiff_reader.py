import argparse
import sys

import pandas as pd
import rasterio
from affine import Affine


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('tiff', help='geotiff file to read')
    parser.add_argument('latitude', help='latitude to extract value at', type=float)
    parser.add_argument('longitude', help='longitude to extract value at', type=float)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = read_args()
    with rasterio.open(args.tiff) as src:
        if src.count != 1:
            raise Exception('{} only works with 1 band tiff, found {}'.format(sys.argv[0], src.count))
        bounds = src.bounds
        if not bounds.left < args.longitude < bounds.right:
            raise Exception('longitude {} is out of bounds for tiff {}'.format(args.longitude, bounds))
        if not bounds.top > args.latitude > bounds.bottom:
            raise Exception('latitude {} is out of bounds for tiff {}'.format(args.latitude, bounds))
        t0 = src.affine  # upper-left pixel corner affine transform
        t1 = t0 * Affine.translation(0.5, 0.5)
        rev = ~t1
        x, y = [round(x) for x in rev * (args.longitude, args.latitude)]

        vals = src.read(1)  # pixel values
        tags = src.tags(1)  # GDAL Metadata
        df = pd.DataFrame()
        df['type'] = [tags['GRIB_ELEMENT']]
        df['value'] = [vals[y][x]]
        df['unit'] = [tags['GRIB_UNIT']]
        df['latitude'] = [args.latitude]
        df['longitude'] = [args.longitude]
        df['valid_time'] = [tags['GRIB_VALID_TIME']]
        df['ref_time'] = [tags['GRIB_REF_TIME']]
        df.to_csv(sys.stdout, index=False)
