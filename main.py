from functions import main
import time

iName = str(time.time())

for i in range(200): 
    filename = iName+"."+str(i)
    main(filename)


