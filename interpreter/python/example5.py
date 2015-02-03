#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

# So that you can still run this module under standard CPython, I add this
# import guard that creates a dummy class instead.
try:
    from rpython.rlib.jit import JitDriver, purefunction
except ImportError:
    class JitDriver(object):
        def __init__(self,**kw): pass
        def jit_merge_point(self,**kw): pass
        def can_enter_jit(self,**kw): pass
    def purefunction(f): return f

def get_location(pc, program, bracket_map):
    return "%s_%s_%s" % (
        program[:pc], program[pc], program[pc+1:]
    )

jitdriver = JitDriver(
                greens=['pc', 'program', 'bracket_map'],
                reds=['tape'],
                get_printable_location=get_location,
            )

@purefunction
def get_matching_bracket(bracket_map, pc):
    return bracket_map[pc]

class Tape(object):
    def __init__(self):
        self.thetape = [0]
        self.position = 0

    def get(self):
        return self.thetape[self.position]

    def set(self, val):
        self.thetape[self.position] = val

    def inc(self):
        self.thetape[self.position] += 1

    def dec(self):
        self.thetape[self.position] -= 1

    def advance(self):
        self.position += 1
        if len(self.thetape) <= self.position:
            self.thetape.append(0)

    def devance(self):
        self.position -= 1

def main_loop(program, bracket_map):
    pc = 0
    tape = Tape()

    while pc < len(program):
        jitdriver.jit_merge_point(pc=pc, tape=tape, program=program, bracket_map=bracket_map)

        code = program[pc]

        if code == ">":
            tape.advance()

        elif code == "<":
            tape.devance()

        elif code == "+":
            tape.inc()

        elif code == "-":
            tape.dec()

        elif code == ".":
            # print
            os.write(1, chr(tape.get()))

        elif code == ",":
            # read from stdin
            data = os.read(0, 1)    # 0 for stdin, 1 for one byte

            if data == '':
                # EOF
                pass
            else:
                tape.set(ord(data[0]))

        elif code == "[" and tape.get() == 0:
            # Skip forward to the matching ]
            pc = get_matching_bracket(bracket_map, pc)

        elif code == "]" and tape.get() != 0:
            # Skip back to the matching [
            pc = get_matching_bracket(bracket_map, pc)

        pc += 1

def parse(program):
    parsed = []
    bracket_map = {}
    leftstack = []

    pc = 0
    for char in program:
        if char in ('[', ']', '<', '>', '+', '-', ',', '.'):
            parsed.append(char)

            if char == '[':
                leftstack.append(pc)
            elif char == ']':
                left = leftstack.pop()
                right = pc
                bracket_map[left] = right
                bracket_map[right] = left
            pc += 1

    return ''.join(parsed), bracket_map

def run(input_file):

    with open(input_file, 'r') as f:
        program, bracket_map = parse(f.read())

    main_loop(program, bracket_map)

def entry_point(argv):
    if len(argv) > 1:
        filename = argv[1]
    else:
        print("You must supply a filename")
        return 1

    run(filename)
    return 0

def target(*args):
    return entry_point

if __name__ == "__main__":
    import sys
    entry_point(sys.argv)
