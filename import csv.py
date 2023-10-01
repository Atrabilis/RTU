import csv
from funciones import *

filename = 'ASDU_types.csv'
output_filename = 'tu_archivo_con_longitud.csv'

def calculate_object_len(asdu_type, format_elements):
    # Busca el formato correspondiente al tipo de ASDU.
    elements = ASDU_FORMATS.get(asdu_type, [])
    # Suma las longitudes correspondientes a cada elemento en el formato.
    length = sum(ELEMENT_LENGTHS.get(el, 0) for el in elements)
    return length

with open(filename, 'r') as infile, open(output_filename, 'w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    headers = next(reader)
    headers.append('object_len')
    writer.writerow(headers)
    
    for row in reader:
        # Asumiendo que el tipo está en la primera columna y el formato en la cuarta.
        asdu_type = int(row[0])
        format_elements = row[3].split('+') # Asumiendo que los elementos del formato están separados por '+'
        object_len = calculate_object_len(asdu_type, format_elements)
        row.append(str(object_len))
        writer.writerow(row)
