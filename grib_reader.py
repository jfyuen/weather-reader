import argparse
import pygrib
import sys

import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator


def interpolate_coord(lats, lons, values, point, method='nearest'):
    """
        Interpolate coordinates at point based on a grid values using latitudes and longitudes
        Point is (lat, long)
    """
    if not np.all(np.diff(lats) > 0.):
        lats = lats[::-1]  # Reverse to have latitudes in ascending order
        values = values[::-1, :]  # Reverse latitudes for grid interpolation
    # Use method='linear' for linear interpolation
    itp = RegularGridInterpolator((lats, lons), values, method=method)
    return itp(point)


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('grib', help='grib file to read')
    parser.add_argument('--data', help='data to extract from grib, e.g: "2 metre temperature", or all if not specified', default=None)
    parser.add_argument('latitude', help='latitude to extract value at', type=float)
    parser.add_argument('longitude', help='longitude to extract value at', type=float)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = read_args()

    dfs = []
    with pygrib.open(args.grib) as grbs:
        if args.data is None:
            selected = grbs
        else:
            selected = grbs.select(name=args.data)
        for grb in selected:
            lats, lons = grb.latlons()
            if not lons.min() < args.longitude < lons.max():
                raise Exception(
                    'longitude {} is out of bounds for [{}, {}]'.format(args.longitude, lons.min(), lons.max()))
            if not lats.min() < args.latitude < lats.max():
                raise Exception(
                    'latitude {} is out of bounds for for [{}, {}]'.format(args.latitude, lats.min(), lats.max()))

            df = pd.DataFrame()
            df['type'] = [grb.name]
            val = interpolate_coord(grb.distinctLatitudes, grb.distinctLongitudes, grb.values,
                                    (args.latitude, args.longitude))
            df['value'] = [val]
            df['unit'] = [grb.units]
            df['latitude'] = [args.latitude]
            df['longitude'] = [args.longitude]
            df['valid_time'] = [grb.validDate]
            df['ref_time'] = [grb.analDate]  # TODO: really analDate?
            dfs.append(df)

    all_df = pd.concat(dfs)
    all_df.to_csv(sys.stdout, index=False)
