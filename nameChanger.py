import os


folder = "C:/Users/henry/Desktop/cansat_code/data"

file_names = os.listdir(folder)

i = 1
for name in file_names:
    src = os.path.join(folder, name)
    dst = str(i) + '.jpg'
    dst = os.path.join(folder, dst)
    print(dst)
    os.rename(src, dst)
    i += 1