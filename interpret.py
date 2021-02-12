import re
from xml.dom.minidom import parse, parseString
import argparse
import sys

xstr = lambda s: '' if s is None else str(s)
# TODO checks

def MOVE():
    if 'GF' in val1 and val1 in GF:
        GF[val1] = val2
    elif 'TF' in val1 and val1 in TF:
        TF[val1] = val2
    elif 'LF' in val1 and val1 in LF:
        LF[val1] = val2
    else:
        eprint("incorect frame/ already declared")
        exit(1)


def CREATEFRAME():
    print('works')


def DEFVAR():
    if 'GF' in val1 and val1 not in GF:
        GF[val1] = None
    elif 'TF' in val1 and val1 not in TF:
        TF[val1] = None
    elif 'LF' in val1 and val1 not in LF:
        LF[val1] = None
    else:
        eprint("incorect frame/ already declared")
        exit(1)


def PUSHFRAME():
    print('works')


def POPFRAME():
    print('works')


def CALL():
    print('works')


def RETURN():
    print('works')


def PUSHS():
    print('works')


def POPS():
    print('works')


def ADD():
    print('works')


def SUB():
    print('works')


def MUL():
    print('works')


def IDIV():
    print('works')


def LT():
    print('works')


def GT():
    print('works')


def EQ():
    print('works')


def AND():
    print('works')


def OR():
    print('works')


def NOT():
    print('works')


def INT2CHAR():
    print('works')


def STR2INT():
    print('works')


def READ():
    print('works')


def WRITE():
    ramec = {
            'GF': GF,
            'LF': LF,
            'TF': TF,
        }

    corect_frame = [val for key,val in ramec.items() if val1.startswith(key)]
    if len(corect_frame) == 0:
        print(re.sub(r'^[^@]*@',r'',val1))
    else:
        print(str(corect_frame[0][val1]))




def CONCAT():
    ramec = {
                'GF': GF,
                'LF': LF,
                'TF': TF,
            }
    corect_frame = [val for key,val in ramec.items() if val2.startswith(key)]
    if len(corect_frame) == 0:
        st = re.sub(r'^[^@]*@',r'',val2)
    else:
        st = xstr(corect_frame[0][val2])
    corect_frame = [val for key,val in ramec.items() if val3.startswith(key)]
    if len(corect_frame) == 0:
          st += re.sub(r'^[^@]*@',r'',val3)
    else:
          st += xstr(corect_frame[0][val3])

    [val for key,val in ramec.items() if val1.startswith(key)][0][val1] = st









def STRLEN():
    print('works')


def GETCHAR():
    print('works')


def SETCHAR():
    print('works')


def TYPE():
    print('works')


def LABEL():
    pass


def JUMP():
    global i
    i = labels[val1]


def JUMPIFEQ():
    global i
    ramec = {
        'GF': GF,
        'LF': LF,
        'TF': TF,
    }

    corect_frame = [val for key,val in ramec.items() if key in val2][0]
    if corect_frame[val2] == val3:
        i = labels[val1]


def JUMPIFNEQ():
    print('works')


def EXIT():
    print('works')


def DPRINT():
    print('works')


def BREAK():
    print('works')


LF = {}
GF = {}
TF = {}

f_stack = []
f_stack.append(LF)

switch = {
    "MOVE": MOVE,
    "CREATEFRAME": CREATEFRAME,
    "DEFVAR": DEFVAR,
    "PUSHFRAME": PUSHFRAME,
    "POPFRAME": POPFRAME,
    "DEFVAR": DEFVAR,
    "CALL": CALL,
    "RETURN": RETURN,
    "PUSHS": PUSHS,
    "POPS": POPS,
    "ADD": ADD,
    "SUB": SUB,
    "MUL": MUL,
    "IDIV": IDIV,
    "LT": LT,
    "GT": GT,
    "EQ": EQ,
    "AND": AND,
    "OR": OR,
    "NOT": NOT,
    "INT2CHAR": INT2CHAR,
    "STR2INT": STR2INT,
    "READ": READ,
    "WRITE": WRITE,
    "CONCAT": CONCAT,
    "STRLEN": STRLEN,
    "GETCHAR": GETCHAR,
    "SETCHAR": SETCHAR,
    "TYPE": TYPE,
    "LABEL": LABEL,
    "JUMP": JUMP,
    "JUMPIFEQ": JUMPIFEQ,
    "JUMPIFNEQ": JUMPIFNEQ,
    "EXIT": EXIT,
    "DPRINT": DPRINT,
    "BREAK": BREAK,
}


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(description='IPP project'
                                                 'note: at least 1 parametr must be specified ( -s or -i) '
                                                 'interprets IPPcode21 from xml file')
    parser.add_argument('-s', '--source', help='source file with xml')
    parser.add_argument('-i', '--input', help='file with input for given program\n')
    args = parser.parse_args()
    if (args.source is None and args.input is None):
        eprint("optional argument needed")
        exit(10);
    if (args.source is not None):
        source = open(args.source, "r")
    else:
        source = sys.stdin
    if (args.input is not None):
        input = open(args.input, "r")
    else:
        input = sys.stdin

    xml = parseString(source.read());
    instructions = xml.getElementsByTagName("instruction")

    # prepare labels
    labels = {}
    for instr in instructions:
        if instr.attributes['opcode'].value == "LABEL":
            labels[instr.getElementsByTagName('arg1')[0].firstChild.data] = instructions.index(instr)

    # TODO: sort by instruction order

    i = 0  # int(instructions[0].attributes['order'].value)
    ma = len(instructions)

    while i < ma:
        ac_in = instructions[i]
        ac_opc = ac_in.attributes['opcode'].value

        type1 = None
        val1 = None
        try:
            var1 = ac_in.getElementsByTagName('arg1')[0]
            type1 = var1.attributes['type'].value
            val1 = var1.firstChild.data
        except:
            pass
        type2 = None
        val2 = None
        try:
            var2 = ac_in.getElementsByTagName('arg2')[0]
            type2 = var2.attributes['type'].value
            val2 = var2.firstChild.data
        except:
            pass
        type3 = None
        val3 = None
        try:
            var3 = ac_in.getElementsByTagName('arg3')[0]
            type3 = var3.attributes['type'].value
            val3 = var3.firstChild.data
        except:
            pass

        if ac_opc not in switch:
            eprint('wrong opcode')
            exit(10)
        switch[ac_opc]()
        #print('\n' + str(i) + '\n')
        i += 1
