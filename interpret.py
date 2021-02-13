import re
import xml.etree.ElementTree as ET
import argparse
import sys

LF = {}
GF = {}
TF = {}

f_stack = []
f_stack.append(LF)

ramec = {
    'GF': GF,
    'LF': LF,
    'TF': TF,
}
arg_types = {
    "MOVE": ["var", "symb", ],
    "CREATEFRAME": [],
    "PUSHFRAME": [],
    "POPFRAME": [],
    "DEFVAR": ["var", ],
    "CALL": ["label", ],
    "RETURN": [],
    "PUSHS": ["symb",],
    "POPS": ["var", ],
    "ADD": ["var", "symb", "symb", ],
    "SUB": ["var", "symb", "symb", ],
    "MUL": ["var", "symb", "symb", ],
    "IDIV": ["var", "symb", "symb", ],
    "LT": ["var", "symb", "symb", ],
    "GT": ["var", "symb", "symb", ],
    "EQ": ["var", "symb", "symb", ],
    "AND": ["var", "symb", "symb", ],
    "OR": ["var", "symb", "symb", ],
    "NOT": ["var", "symb", ],
    "INT2CHAR": ["var", "symb", ],
    "STRI2INT": ["var", "symb", "symb", ],
    "READ": ["var", "type", ],
    "WRITE": ["symb", ],
    "CONCAT": ["var", "symb", "symb", ],
    "STRLEN": ["var", "symb", ],
    "GETCHAR": ["var", "symb", "symb", ],
    "SETCHAR": ["var", "symb", "symb", ],
    "TYPE": ["var", "symb", ],
    "LABEL": ["label", ],
    "JUMP": ["label", ],
    "JUMPIFEQ": ["label", "symb", "symb", ],
    "JUMPIFNEQ": ["label", "symb", "symb", ],
    "EXIT": ["symb", ],
    "DPRINT": ["symb", ],
    "BREAK": [],
}

xstr = lambda s: '' if s is None else str(s)


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


def STRI2INT():
    print('works')


def READ():
    print('works')


def WRITE():
    corect_frame = [val for key, val in ramec.items() if val1.startswith(key)]
    if len(corect_frame) == 0:
        print(re.sub(r'^[^@]*@', r'', val1))
    else:
        print(str(corect_frame[0][val1]))


def CONCAT():
    corect_frame = [val for key, val in ramec.items() if val2.startswith(key)]
    if len(corect_frame) == 0:
        st = re.sub(r'^[^@]*@', r'', val2)
    else:
        st = xstr(corect_frame[0][val2])
    corect_frame = [val for key, val in ramec.items() if val3.startswith(key)]
    if len(corect_frame) == 0:
        st += re.sub(r'^[^@]*@', r'', val3)
    else:
        st += xstr(corect_frame[0][val3])

    [val for key, val in ramec.items() if val1.startswith(key)][0][val1] = st


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

    corect_frame = [val for key, val in ramec.items() if key in val2][0]
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
    "STR2INT": STRI2INT,
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='IPP project'
                                                 'note: at least 1 parametr must be specified ( -s or -i) '
                                                 'interprets IPPcode21 from xml file')
    parser.add_argument('-s', '--source', help='source file with xml')
    parser.add_argument('-i', '--input', help='file with input for given program\n')
    args = parser.parse_args()
    if args.source is None and args.input is None:
        eprint("optional argument needed")
        exit(10)
    if args.source is not None:
        source = open(args.source, "r")
    else:
        source = sys.stdin
    if args.input is not None:
        input = open(args.input, "r")
    else:
        input = sys.stdin

    # load xml
    try:
        root = ET.fromstring(source.read())
    except:
        eprint("XML declaration not well-formed")
        exit(31)

    order_array = []
    # check xml structure
    if root.tag != 'program' or root.get('language') != 'IPPcode21' or len(root.attrib) != 1:
        exit(32)
    # check ins-xml
    for inst in root:
        if inst.tag != 'instruction' or inst.get('order') is None or switch.get(inst.get('opcode')) is None or len(
                inst.attrib) != 2:
            exit(32)
        order_array.append(int(inst.get('order')))
        # check args-xml need to sort first
        inst[:] = sorted(inst, key=lambda child: child.tag)
        arg_list = arg_types.get(inst.get('opcode'))
        if len(inst) != len(arg_list):
            exit(32)
        for arg in range(len(arg_list)):
            argx = inst[arg]
            if argx.tag != 'arg' + str(arg+1) or argx.get('type') is None or len(argx.attrib) != 1:
                exit(32)

    if len(order_array) != len(set(order_array)) or any(i < 0 for i in order_array):
        exit(32)


    # sort by instruction order
    root[:] = sorted(root, key=lambda child: int(child.get('order')))

    # prepare labels
    labels = {}
    for instruction in [i for i in root if i.get('opcode') == 'LABEL']:
        labels[instruction[0].text] = list(root).index(instruction)

    i = 0
    ma = len(root)

    while i < ma:
        ac_in = root[i]
        ac_opc = ac_in.get('opcode')

        type1 = None
        val1 = None
        type2 = None
        val2 = None
        type3 = None
        val3 = None
        try:
            type1 = ac_in.find('arg1').get('type')
            val1 = ac_in.find('arg1').text
            type2 = ac_in.find('arg2').get('type')
            val2 = ac_in.find('arg2').text
            type3 = ac_in.find('arg3').get('type')
            val3 = ac_in.find('arg3').text
        except:
            pass

        if ac_opc not in switch:
            eprint('wrong opcode')
            exit(10)
        switch[ac_opc]()
        i += 1
