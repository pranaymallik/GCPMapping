from bs4 import BeautifulSoup
import requests
import csv
import yaml
import os

#Headers names, and all the
METRIC_HEADERS = ["metric_name", "metric_display", "metric_kind", "metric_type", "metric_ unit", "metric_resource",
                  "metric_description"]
IGNORED_VALUES = ["BETA", "ALPHA", "GA", "DEPRECATED", "EARLY_ACCESS", ""]
YAML_FILE = "gcp.yaml"
CSV_FILE = "gcp.csv"
CSV_FOLDER = "csv"
YAML_FOLDER = "yaml"
MAPPING_FOLDER = "mapping"


# create a class
class GCPExtractor:
    def __init__(self, url=""):
        self.page = None
        self.url = url
        self.csv_array = []
        self.metric_type_dict = {}

    def load_page(self):
        self.page = requests.get(self.url)

    def get_content(self):
        return self.page.content

    def generate_mapping(self):
        path3 = './mapping'
        os.chdir(path3)
        categories = {}
        for row in self.csv_array:
            mapping_array = []
            category = row[0].split('.')[1]
            if category in categories:
                mapping_array = categories[category]
            part1 = row[0]
            part11 = part1[4:]
            part2 = " stackdriver_"
            part3 = str(row[5])
            part4 = part11[:part11.find('.')]
            part5 = "_googleapis_com_"
            find_part_6 = part11.find('.')
            part6 = part11[find_part_6:]
            part6_2 = part11.replace('.','_')
            finalString = part11+part2+part3+"_"+part4+part5+part6_2
            mapping_array.append(finalString)
            categories[category] = mapping_array
        for category in categories:
            file_name = category+".mapping"
            f = open(file_name, 'w', newline='')
            f.write("stackdriver_<monitoted_resource>_<component_googleapis_com>_subcomponent_metricname\n")
            for i in categories[category]:
                f.write(i+"\n")
            f.close()
    def generate_csv(self):
        index = 0
        path2 = './csv'
        os.chdir(path2)
        categories = {}
        for row in self.csv_array:
            csv_array =  []
            category = row[0].split('.')[1]
            if category in categories:
                csv_array = categories[category]
            csv_array.append(row)
            categories[category] = csv_array
        for category in categories:
            file_name = category+".csv"
            f = open(file_name, 'w', newline='')
            writer = csv.writer(f)
            writer.writerow(METRIC_HEADERS)
            writer.writerows(categories[category])
            f.close()
        os.chdir('..')


    def generate_folders(self):
        path = './'
        os.chdir(path)
        if not os.path.exists(CSV_FOLDER):
            NewFolder = CSV_FOLDER
            os.mkdir(NewFolder)
        if not os.path.exists(YAML_FOLDER):
            NewFolder2 = YAML_FOLDER
            os.mkdir(NewFolder2)
        if not os.path.exists(MAPPING_FOLDER):
            NewFolder3 = MAPPING_FOLDER
            os.mkdir(NewFolder3)

    def generate_yaml(self):
        path2 = './yaml'
        os.chdir(path2)

        metric_category_list = []
        for key in self.metric_type_dict:
            metric_dict = {'type': key}
            metric_category_list.append(metric_dict)
            keys = []
            for value in self.metric_type_dict[key]:
                keys.append({'name': value})
            metric_dict['keys'] = keys
        counter = 0
        for fileNumber in metric_category_list:
            fileName = (metric_category_list[counter]['type'])
            with open(fileName+".yaml", 'w') as f:
                yaml.dump(metric_category_list[counter], f)
            counter+=1
        os.chdir('..')

    def process_content(self):
        soup = BeautifulSoup(self.page.content, 'html.parser')
        table_rows = soup.find_all('tr')
        self.metric_type_dict = {}
        for row in table_rows:
            if 'met_type' in row.get("class"):
                original_row_id = row.get("id")
                if original_row_id is not None:
                    metric_category = original_row_id.split('/')[0]
                    row_id = original_row_id.replace("/", ".")
                   # print(row_id)

                    row_children = row.find_all(text=True)
                    for child in row_children:
                        child_string = child.string.strip()
                        if child_string in IGNORED_VALUES:
                            pass
                        elif '_' in child_string or '/' in child_string:
                            pass
                        else:
                            approved_child_string = child_string
                         #   print(approved_child_string)
            elif 'met_desc' in row.get("class"):
                columns = row.select("td")
                if columns and len(columns) > 0:
                    column = columns[0]
                    ktu = column.select("code", text=True)
                    if len(ktu) > 0:
                        ktu_values = ','.join(code.text for code in ktu)
                        if ktu_values == "GAUGE,BOOL,":
                            ktu_values = "GAUGE,BOOL,(blank)"
                        if ktu_values == "GAUGE,STRING,":
                            ktu_values = "GAUGE,STRING,(blank)"
                        for code in ktu:
                            if code != "":
                                code_string = code.string
                             #   print(code_string)
                    monitored_resources = column.select("b", text=True)
                    for resource in monitored_resources:
                        resource_string = resource.string
                 #       print(resource_string)
                if columns and len(columns) > 1:
                    column = columns[1]
                    labels = column.select("code", text=True)
                    for label in labels:
                        metric_labels = []
                        if metric_category in self.metric_type_dict:
                            metric_labels = self.metric_type_dict[metric_category]
                        label_text = metric_category + "_" + label.text
                        if label_text in metric_labels:
                            pass
                        else:
                            label_text = label_text
                            metric_labels.append(label_text)
                            self.metric_type_dict[metric_category] = metric_labels
                      #      print(self.metric_type_dict)
                    desc = column.select("i", text=True)
                    description = desc[0].text
                    kind = ktu_values.split(",")[0]
                    type = ktu_values.split(",")[1]
                    unit = ktu_values.split(",")[2]
                    description = ' '.join(description.split('\n'))
                    self.csv_array.append(
                        ["gcp." + row_id, approved_child_string, kind, type, unit, resource_string, description])
if __name__ == '__main__':
    extractor = GCPExtractor("https://cloud.google.com/monitoring/api/metrics_gcp")
    extractor.load_page()
    extractor.process_content();
    extractor.generate_folders()
    extractor.generate_yaml()
    extractor.generate_csv()
    extractor.generate_mapping()
