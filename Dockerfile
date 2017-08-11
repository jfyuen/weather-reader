FROM debian:stable
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y python3-grib python3-rasterio python3-scipy python3-matplotlib python3-pandas\
    && apt-get clean
