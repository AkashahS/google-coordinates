import csv
import eviltransform

# input and output files
file_in =  r'C:\pycode\Baidu_in.csv'
file_out = r'C:\pycode\Baidu_out.csv'

# Reading orignal file into a table
table = []
with open(file_in, 'r', newline='', encoding='utf-8') as inFile:
    reader = csv.reader(inFile)
#     header = next(reader)      # skip header
    for row in reader:
        table.append(row)
print("Orignal file: ")
print(table)

# converting bd-09 to gcj-02 coordinates

with open(file_out, "w", newline='', encoding='utf-8') as outFile:
    writer = csv.writer(outFile)
    writer.writerow(["name", "Longitude", "latitude"]) # adding header
    print("google map Coordinates:")
    for row in table:
        new_row = []
        wgs = eviltransform.bd2wgs(float(row[1]),float(row[2]))
        gcj = eviltransform.wgs2gcj(wgs[0],wgs[1])
        new_row.append(row[0])
        new_row.append(gcj[0])
        new_row.append(gcj[1])
        print(new_row)
        writer.writerow(new_row)


print("Coordinate conversion is completed")
