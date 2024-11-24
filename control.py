import time
from functions import main

time_name = str(time.time())

for i in range(1): 
    filename = "control_"+time_name+"."+str(i)
    main(filename, 20000, 400)
