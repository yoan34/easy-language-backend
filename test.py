import os
file_list = [f for f in os.listdir('data/') if os.path.isfile(os.path.join('data/', f))]
print(file_list)