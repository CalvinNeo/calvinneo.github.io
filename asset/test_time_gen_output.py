import os, sys
import subprocess
import time

inp = open("B.in", "rb")
oup = open("B.out", "wb")
start_time = time.time()
stdoutput = subprocess.check_output(["B.exe"], stdin=inp)  
end_time = time.time()
oup.write(stdoutput)
print "time cost: {}".format(end_time - start_time)
oup.close()