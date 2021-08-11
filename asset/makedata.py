
inp = open("A.dat")
oup = open("A.in", "w+")
times = 5
s = ""
for line in inp:
    line = line.strip("\n")
    if(line == "---"):
        pass
    else:
        s += line
        s += "\n"
for iter in xrange(times):
    oup.write(s)
oup.close()
