def simhash(tokens, bits=64):
    from collections import Counter
    v = [0]*bits
    for token, w in Counter(tokens).items():
        h = hash(token)
        for i in range(bits):
            v[i] += w if (h >> i) & 1 else -w
    out = 0
    for i, x in enumerate(v):
        if x > 0: out |= (1 << i)
    return out

def hamming(a, b):
    return bin(a ^ b).count("1")
