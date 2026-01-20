# B = 100
# N = B * 50000
# K = N // 50

B = 10000
N = 500000000
K = 100000000
IS = 1500 * 10
IS = int(K * 0.0001)
IS = 50000

K = 500000
IS = 1500

SCALE = 100
B //= SCALE
N //= SCALE
K //= SCALE
IS //= SCALE

print("B {} N {} K {} IS {}".format(B, N, K, IS))

import random

T = 100

def count_buckets(l):
    s = set()
    for x in l:
        b = x % B
        s.add(b)
    return len(s)

def main_k():
    total_b = 0
    b = B * 1.0
    k = IS * 1.0
    expected = b * (1 - ((b - 1) / b) ** k)
    print("aaa", (b - 1) / b)
    for t in range(T):
        all_k = random.sample(range(N), IS)
        b = count_buckets(all_k)
        total_b += b
        print("res of {} is {}".format(t, b))

    print("final {} expecetd {}".format(total_b * 1.0 / T, expected))

def main_is():
    global T
    total_b = 0
    b = B * 1.0
    k = IS * 1.0
    expected = b * (1 - ((b - 1) / b) ** k)
    print("aaa", (b - 1) / b)
    for t in range(T):
        all_k = random.sample(range(N), K)
        all_is = random.sample(all_k, IS)
        b = count_buckets(all_is)
        total_b += b
        print("res of {} is {}".format(t, b))

    print("final {} expecetd {}".format(total_b * 1.0 / T, expected))

if __name__ == '__main__':
    main_is()