import csv, os

words = ["i", "ii", "iii","iiii", "iiiii"]

input_file = os.path.join(os.path.dirname(__file__), "./syllabes_data.csv")


with open(input_file, 'w', newline='') as file:
    writer = csv.writer(file)
    for word in words:
        length = len(word)
        row = [''] * (length - 1)
        row.append(word) 
        writer.writerow(row)

