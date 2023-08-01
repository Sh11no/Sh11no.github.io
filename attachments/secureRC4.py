from secret import cipher, key
import string

class Encoder:
    def __init__(self):
        self.stream = self.randomBox(self._init_box(key))

    def do_encrypt(self, c):
        return ord(c) ^ next(self.stream)

    def _init_box(self, crypt_key):
        Box = list(range(256))
        key_length = len(crypt_key)
        j = 0
        for i in range(256):
            index = ord(crypt_key[(i % key_length)])
            j = (j + Box[i] + index) % 256
            Box[i], Box[j] = Box[j], Box[i]

        return Box

    def randomBox(self, S):
        i = 0
        j = 0
        while True:
            i = i + 1 & 255
            j = j + S[i] & 255
            S[i], S[j] = S[j], S[i]
            yield S[(S[i] + S[j] & 255)]


encoder = Encoder()
flag = input("input flag>> ")
table = string.digits + string.ascii_letters + "{}_"
i = 0
correct = 0

while i < len(flag):
    while i < len(flag) and flag[i] not in table:
        i += 1
    if i >= len(flag):
        break
    if cipher[i] != encoder.do_encrypt(flag[i]):
        print("Wrong flag!")
        exit(0)
    else:
        correct += 1
    if correct == len(cipher):
        print("Correct flag!")
        exit(0)
    i += 1

print("Wrong flag!")