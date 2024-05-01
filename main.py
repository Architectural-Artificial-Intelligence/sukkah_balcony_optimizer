import time
from functions import main

time_name = str(time.time())

for i in range(200): 
    filename = time_name+"."+str(i)
    main(filename)
