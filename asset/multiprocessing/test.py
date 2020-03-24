import multiprocessing
import _multiprocessing
import socket, os
from multiprocessing import Process

def make_pipe():
    s1, s2 = socket.socketpair()
    s1.setblocking(True)
    s2.setblocking(True)
    # c1 = _multiprocessing.Connection(os.dup(s1.fileno()))
    # c2 = _multiprocessing.Connection(os.dup(s2.fileno()))
    # s1.close()
    # s2.close()

    c1 = _multiprocessing.Connection(s1.fileno())
    c2 = _multiprocessing.Connection(s2.fileno())

    return c1, c2

def commu(w):
    w.send("aaaaaaaaaaaaaaaaaa")
    w.send("bbbbbbbbbbbbbbbbbb")

reader, writer = make_pipe()


print type(reader), dir(reader)

p = Process(target=commu, args=(writer, ))
p.start()

print reader.recv()
print reader.recv()