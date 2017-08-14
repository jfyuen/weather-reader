# Weather Reader

Basic docker image and scripts to read geotiff and grib2 files at selected longitude/latitude using python 3.
It can read both tiff and grib2 files based on their extension.

## Usage

The scripts are very basic and were only tested with grib files from Meteo France and NOAA. 
Tiff files were only tested with Meteo France export with a single value encoded in the image.

### Geotiff
```bash
python3 tiff_reader.py ${FILE_PATH} --pos=latitude,longitude
```

- `${FILE_PATH}`: path to file to read`
- `latitude`, `longitude`: coordinates to get value
- Option `-o` to save output to a file, default to stdout

The output is in csv format, to handle future multiple coordinates to output at once.

Alternatively, a `-csv` flag can be given instead of `--pos` to read a csv file containing `latitude` and `longitude` columns.
Read values will be appended to the csv for each row.
```bash
python3 tiff_reader.py  --csv=${POSITIONS.csv} ${FILE_PATH}
```

### Grib2
```bash
python3 grib_reader.py --pos=latitude,longitude ${FILE_PATH}
```

- `${FILE_PATH}` path to file to read`
- Option `--data`: extract selected data from file, e.g: '2 metre temperature'
- `latitude`, `longitude`: coordinates to get value
- Option `-o` to save output to a file, default to stdout

Example:
```bash
python3 grib_reader.py --data='2 metre temperature' --pos=50.136000,1.834000 ${FILE_PATH}
```

Alternatively, a `--csv` flag can be given instead of `--pos` to read a csv file containing `latitude` and `longitude` columns.
Read values will be appended to the csv for each row:
```bash
python3 grib_reader.py --data '2 metre temperature' --csv=${POSITIONS.csv} ${FILE_PATH} 
```

### With docker image

```bash
docker pull jfyuen/pyweather
docker run --rm -v ${SCRIPT_PATH}:/srv/ jfyuen/pyweather python3 /srv/reader.py /srv/${FILE_PATH}
```
- `${SCRIPT_PATH}` is where the reader script and files to analyze are both located, they are to be mounted as a volume in docker.
- `${FILE_PATH}` is the relative file path to read from `${SCRIPT_PATH}`


### With Debian

```bash
# apt-get install -y python3-grib python3-rasterio python3-scipy python3-matplotlib python3-pandas
```

## TODO

- When scripts are stable, embed them in the docker image
- Handle mutliple location to be exported at once
- Add a requirements.txt