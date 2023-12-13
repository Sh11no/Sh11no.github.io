
import os
import sys
import subprocess
from secret import flag

SRC = '/home/ctf/temp/code.c'
BIN = '/home/ctf/temp/temp_bin'
DATA = '/home/ctf/data'


res_map = {
    'CE': 'Compile Error',
    'TLE': 'Time Limit Exceeded',
    'RE': 'Runtime Error',
    'WA': 'Wrong Answer',
    'AC': 'Accepted'
}


def check_excutable(path, input, ans, timeout):
    if not os.path.isfile(path):
        return 'CE'

    try:
        p = subprocess.run(
            [f"./{path}"],
            input=input,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return 'TLE'

    if p.returncode != 0:
        return 'RE'

    try:
        output = p.stdout.decode()
    except UnicodeDecodeError:
        return 'WA'

    lines = output.strip().split('\n')
    return 'AC' if lines == ans else 'WA'


if __name__ == "__main__":

    print("Enter your code (ending with two blank lines):")

    code1 = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        code1.append(line)

        if len(code1) >= 2 and code1[-1] == '' and code1[-2] == '':
            break
    with open(SRC, "w") as fd1:
        fd1.write('\n'.join(code1))

    p = subprocess.run(
        ["gcc", "-w", "-O2", SRC, "-o", BIN],
        stdout=sys.stdout,
        stdin=subprocess.DEVNULL,
        stderr=subprocess.STDOUT
    )

    with open(os.path.join(DATA, f'input.in'), 'rb') as f:
        instr = f.read()
    with open(os.path.join(DATA, f'output.out'), 'r') as f:
        ans = f.read().strip().split('\n')

    res = check_excutable(BIN, instr, ans, 0.5)
    print('Result: ', res_map[res])
    if res == 'AC':
        print(flag)
    print('\n')
