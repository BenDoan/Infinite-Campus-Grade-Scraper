import matplotlib.pyplot as plt
import csv

def read_csv(file_name):
    final_list = []
    reader = csv.reader(open(file_name, 'rb'), delimiter=',')
    for x in reader:
        final_list.append(x)
    return final_list

def add_to_csv(file_name, single_list):
    final_list = read_csv(file_name)
    writer = csv.writer(open(file_name, 'wb'), delimiter=',',quoting=csv.QUOTE_MINIMAL)
    final_list.append(single_list)
    for x in final_list:
        writer.writerow(x)

grade_list = []
date_list = []
for x in read_csv('data.csv'):
    print x[0]
    if x[0] == "0333-33 Zoology":
        grade_list.append(x[1])
        date_list.append(x[2])

for x in date_list:
    print x

plt.plot(date_list, grade_list)
plt.ylabel('Grades')
plt.ylabel('Date')
plt.show()

