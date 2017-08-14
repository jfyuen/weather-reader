import argparse
import sys

import datetime
import pandas as pd
import rasterio
from affine import Affine


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('tiff', help='geotiff file to read')
    parser.add_argument('-o', help='save output to file, default to stdout', default=sys.stdout)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--pos', help='latitude,longitude tuple', default=None)
    group.add_argument('--csv',
                       help='csv (comma separated) file containing Latitude,Longitude columns, will extract values for each row',
                       default=None)
    args = parser.parse_args()
    if args.pos is None and args.csv is None:
        parser.print_help()
        sys.exit(1)
    return args


def format_time(s):
    end_patt = " sec UTC"
    if not s.endswith(end_patt):
        raise Exception('Unknown time format "{}", expecting "timestamp sec UTC"'.format(s))
    v = int(s.replace(end_patt, ""))
    return datetime.datetime.utcfromtimestamp(v)


def check_bounds(bounds, latitude, longitude):
    if not bounds.left < longitude < bounds.right:
        raise Exception('longitude {} is out of bounds for tiff {}'.format(longitude, bounds))
    if not bounds.top > latitude > bounds.bottom:
        raise Exception('latitude {} is out of bounds for tiff {}'.format(latitude, bounds))


if __name__ == '__main__':
    args = read_args()
    if args.pos is not None:
        in_df = pd.DataFrame()
        latitude, longitude = args.pos.split(',')
        in_df['latitude'] = [float(latitude)]
        in_df['longitude'] = [float(longitude)]
    else:
        in_df = pd.read_csv(args.csv, sep=',')

    dfs = []
    with rasterio.open(args.tiff) as src:
        if src.count != 1:
            raise Exception('{} only works with 1 band tiff, found {}'.format(sys.argv[0], src.count))

        t0 = src.affine  # upper-left pixel corner affine transform
        t1 = t0 * Affine.translation(0.5, 0.5)
        rev = ~t1

        bounds = src.bounds

        vals = src.read(1)  # pixel values
        tags = src.tags(1)  # GDAL Metadata

        for i, row in in_df.iterrows():
            latitude, longitude = row['latitude'], row['longitude']
            check_bounds(bounds, latitude, longitude)
            x, y = [int(round(x)) for x in rev * (longitude, latitude)]

            df = pd.DataFrame()
            df['type'] = [tags['GRIB_ELEMENT']]
            df['value'] = [vals[y][x]]
            df['unit'] = [tags['GRIB_UNIT']]
            valid_time = format_time(tags['GRIB_VALID_TIME'])
            df['valid_time'] = [valid_time]
            ref_time = format_time(tags['GRIB_REF_TIME'])
            df['ref_time'] = [ref_time]
            for c in in_df.columns:
                df[c] = row[c]
            dfs.append(df)

    all_df = pd.concat(dfs)
    all_df.to_csv(args.o, index=False)
