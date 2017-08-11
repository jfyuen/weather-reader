# Weather Reader

Basic docker image and scripts to read geotiff and grib2 files at selected longitude/latitude using python 3.
It can read both tiff and grib2 files based on their extension.

## Usage

The scripts are very basic and were only tested with grib files from Meteo France and NOAA. 
Tiff files were only tested with Meteo France export with a single value encoded in the image.

### Geotiff
```bash
python3 tiff_reader.py ${FILE_PATH} latitude longitude
```

- `${FILE_PATH}`: path to file to read`
- `latitude`, `longitude`: coordinates to get value

The output is in csv format, to handle future multiple coordinates to output at once.

### Grib2
```bash
python grib_reader.py ${FILE_PATH} latitude longitude
```

- `${FILE_PATH}` path to file to read`
- Option `--data`: extract selected data from file, e.g: '2 metre temperature'

Example:
```bash
python grib_reader.py -data '2 metre temperature' ${FILE_PATH} 50.136000 1.834000
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