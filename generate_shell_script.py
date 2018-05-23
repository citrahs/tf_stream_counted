import csv


with open("cctv.csv", "r") as file:
    reader = csv.reader(file)
    i = 0
    for row in reader:
        i = i + 1
        with open("script"+str(i)+".sh", "w") as out:
            out.write("python3 cctv_object_detection.py "+" ".join('"'+r+'"' for r in row))
    