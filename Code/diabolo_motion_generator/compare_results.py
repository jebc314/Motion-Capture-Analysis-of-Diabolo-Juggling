import numpy as np

f1 = open('output.csv')
f2 = open('correct_output.csv')

f1_lines = f1.readlines()
f2_lines = f2.readlines()

length = min(len(f1_lines), len(f2_lines))

error = 0

previous = None
for i in range(length):
    f1_line = np.array([float(part) for part in f1_lines[i].split(',')])
    try:
        f2_line = np.array([float(part) for part in f2_lines[i].split('\t')])
        previous = f2_line
    except:
        f2_line = previous
    diff = f1_line - f2_line
    value = np.sqrt(np.sum(np.dot(diff, diff)))
    correct_distance = np.sqrt(np.sum(np.dot(f2_line, f2_line)))
    print(value, correct_distance)
    error += value

print(error/length)

