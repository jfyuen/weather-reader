import argparse
import pygrib
import sys

import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator


def init_interpolator(lats, lons, values, method='nearest'):
    """
        Interpolate coordinates at point based on a grid values using latitudes and longitudes
        Point is (lat, long)
    """
    if not np.all(np.diff(lats) > 0.):
        lats = lats[::-1]  # Reverse to have latitudes in ascending order
        values = values[::-1, :]  # Reverse latitudes for grid interpolation
    # Use method='linear' for linear interpolation
    return RegularGridInterpolator((lats, lons), values, method=method)


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('grib', help='grib file to read')
    parser.add_argument('-o', help='save output to file, default to stdout', default=sys.stdout)
    parser.add_argument('--data', help='data to extract from grib, e.g: "2 metre temperature", or all if not specified. Accept multiple values separated by ","',
                        default=None)
    parser.add_argument('--level', help='levels to extract. Accept multiple values separated by ","', default=None)
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


def check_bounds(l, v, typ):
    if not l.min() < v < l.max():
        raise Exception('{} {} is out of bounds for [{}, {}]'.format(typ, v, l.min(), l.max()))


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
    with pygrib.open(args.grib) as grbs:
        grbs_params = {}
        if args.data is not None:
            grbs_params['name'] = args.data.split(',')
        if args.level is not None:
            grbs_params['level'] = [int(l) for l in args.level.split(',')]
        for grb in grbs.select(**grbs_params):
            lats, lons = grb.latlons()
            interpolator = init_interpolator(grb.distinctLatitudes, grb.distinctLongitudes, grb.values)

            for i, row in in_df.iterrows():
                latitude, longitude = row['latitude'], row['longitude']
                check_bounds(lons, longitude, 'longitude')
                check_bounds(lats, latitude, 'latitude')

                df = pd.DataFrame()
                df['type'] = [grb.name]
                val = interpolator((latitude, longitude))
                df['value'] = [val]
                df['unit'] = [grb.units]
                df['valid_time'] = [grb.validDate]
                df['ref_time'] = [grb.analDate]  # TODO: really analDate?
                df['level'] = [grb.level]
                for c in in_df.columns:
                    df[c] = row[c]
                dfs.append(df)

    all_df = pd.concat(dfs)
    all_df.to_csv(args.o, index=False)
