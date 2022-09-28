WRF-observational-nudging-Python-scripts

These scripts are tools to prepare Lufft surface weather station data or raws
surface weather station data into LITTLE_R format. lufft2littler.py or raws2littler.py
must be run for each input file. littler2date.py then takes the outputs of the above
programs and then combines them into files for the OBSGRID program.

An example bash script ("example_prepare_lufft_obs.sh") is provided to show the data
flow for observations from a lufft weather station.

Note: It is recommended to use at least a 3 hour period for input into OBSGRID.

These scripts are meant to be used as templates in converting other data sources into
LITTLE_R format.