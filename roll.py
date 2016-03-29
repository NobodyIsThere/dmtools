#!/usr/bin/env python

import argparse
import random
import re

def parse(string, value_only=True):
    pattern = '((\d+)?(d(\d+)))?(([+-])?(\d))?'
    inp = re.match(pattern, string)
    groups = inp.groups()
    # groups:
    # 1: Number of dice rolled
    # 3: Type
    # 5: Operator (+/-/None)
    # 6: Number to add or subtract
    num_dice = groups[1]
    type_dice = groups[3]
    op = groups[5]
    mod = groups[6]
    
    if mod and not op:
        if value_only:
            return int(mod)
        return int(mod), None, None, int(mod), str(mod)
    
    if not num_dice:
        num_dice = 1
    if not type_dice:
        type_dice = 20
    if not op:
        op = '+'
    if not mod:
        mod = 0
    mod = int(mod)
    
    total = 0
    for i in range(int(num_dice)):
        total += random.randint(1, int(type_dice))
    result = total + mod if op == '+' else total - mod
    
    if value_only:
        return result
    if not op or mod == 0:
        string = str(result)
    else:
        string = "%i %s %i = %i"%(total, op, mod, result)
    return total, op, mod, result, string

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("string", nargs='?', default="d20")
    parser.add_argument("--twice", action="store_true")
    args = parser.parse_args()

    for i in range(2 if args.twice else 1):
        total, op, mod, result, string = parse(args.string, value_only=False)
        print string
