# GCPMapping
Assignment: Using google metrics api page, webscrape the data and store into csv, yaml, and mapping files for intended purposes of reading data.
GCPMappingAssignment.py = Main python file with code to run that will create all the folders(csv, yaml, mapping). The code results in an error if folders are already present in the directory that the code is run in. To avoid this, if running for 2nd, 3rd, or nth time in directory, comment out line178:     "extractor.generate_folders()" so there is no error.
mapping: Mapping is a folder directory in the project that will hold mapping files for every single category/metric. Formatting for the mapping file header is located at the top of every file.
csv: Csv is a folder directory in the project that will hold csv files, with the header being at the top of every single file, and there being a file for every single category.
yaml: yaml is a folder directory in the project that will hold yaml files, and the metric/category name is at the bottom of all of the files where the metric_resources are above.
idea folder does not hold significant data for this project.
