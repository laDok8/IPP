import re
import xml.etree.ElementTree as ET
import argparse
import sys

LF = None
GF = {}
TF = None

f_stack = [None]

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
    "PUSHS": ["symb", ],
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

regex = {
    'var': '^(?:LF|GF|TF)@[a-zA-Z_\-$&%*!?][\w\-$&%*!?]*$',
    'int': '^[+-]?[\d]+$',
    'bool': '^true|false$',
    'string': '^.*$',
    'nil': '^nil$',
    'label': '^[a-zA-Z_\-$&%*!?][\w\-$&%*!?]*$',
    'type': '^int|bool|string|nil$',
}


def nil(var):
    return None


def var(var):
    return var


cast = {
    'int': int,
    'bool': bool,
    'string': str,
    'nil': nil,
    'var': var,
}


# returns real type - no var
def get_type(type, val):
    if type == 'var':
        m_frame = ramec[val[:2]]
        if m_frame is None:
            eprint("frame missing")
            exit(54)
        if val not in m_frame:
            eprint("undefined variable")
            exit(52)
        if isinstance(m_frame[val], str):
            return 'string'
        elif isinstance(m_frame[val], int):
            return 'int'
        elif isinstance(m_frame[val], bool):
            return 'bool'
        else:
            return 'nil'
    else:
        return type


def get_val(type, val):
    if type == 'var':
        m_frame = ramec[val[:2]]
        if m_frame is None:
            eprint("frame missing")
            exit(54)
        if val not in m_frame:
            eprint("undefined variable")
            exit(52)
        return m_frame[val]
    else:
        return cast[type](val)


def set_val(val, res):
    m_frame = ramec[val[:2]]
    if m_frame is None:
        eprint("frame missing")
        exit(54)
    if val1 not in m_frame:
        eprint("undefined variable")
        exit(52)
    m_frame[val] = res


def MOVE():
    set_val(val1, get_val(type2, val2))


def CREATEFRAME():
    global TF
    TF = {}


def DEFVAR():
    m_frame = ramec[val1[:2]]
    if m_frame is None:
        eprint("frame missing")
        exit(54)

    if val1 in m_frame:
        eprint("redefinition of variable")
        exit(52)
    # instrukce
    m_frame[val1] = None


def PUSHFRAME():
    global LF, TF
    if TF is None:
        eprint('undefined TF')
        exit(55)
    f_stack.push(LF)
    LF = TF
    TF = None


def POPFRAME():
    global LF, TF
    if LF is None:
        eprint('undefined LF')
        exit(55)
    TF = LF
    LF = f_stack.pop()


store_calls = [None]


def CALL():
    global i
    store_calls.append(i + 1)
    # has same call siganture
    JUMP();


def RETURN():
    global i
    tmp = store_calls.pop();
    if tmp is None:
        eprint('call stack empty')
        exit(56)
    i = tmp


val_stack = [None]


def PUSHS():
    val_stack.append(get_val(type1, val1))


def POPS():
    tmp = val_stack.pop()
    if tmp is None:
        eprint('var stack empty')
        exit(56)
    set_val(val1, tmp)


def ADD():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) != 'int':
        eprint('type mismatch - ADD')
        exit(53)
    set_val(val1, get_val(type2, val2) + get_val(type3, val3))


def SUB():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) != 'int':
        eprint('type mismatch - SUB')
        exit(53)
    set_val(val1, get_val(type2, val2) - get_val(type3, val3))


def MUL():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) != 'int':
        eprint('type mismatch - MUL')
        exit(53)
    set_val(val1, get_val(type2, val2) * get_val(type3, val3))


def IDIV():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) != 'int':
        eprint('type mismatch - IDIV')
        exit(53)
    if get_val(type3, val3) == 0:
        eprint('division by zero')
        exit(57)
    set_val(val1, get_val(type2, val2) // get_val(type3, val3))


def LT():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) not in ['int', 'bool', 'string']:
        eprint('type mismatch')
        exit(53)
    set_val(val1, get_val(type2, val2) < get_val(type3, val3))


def GT():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) not in ['int', 'bool', 'string']:
        eprint('type mismatch')
        exit(53)
    set_val(val1, get_val(type2, val2) > get_val(type3, val3))


def EQ():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) not in ['int', 'bool', 'string']:
        eprint('type mismatch')
        exit(53)
    set_val(val1, get_val(type2, val2) == get_val(type3, val3))


def AND():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) != 'bool':
        eprint('type mismatch')
        exit(53)
    set_val(val1, get_val(type2, val2) and get_val(type3, val3))


def OR():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) != 'bool':
        eprint('type mismatch')
        exit(53)
    set_val(val1, get_val(type2, val2) or get_val(type3, val3))


def NOT():
    if get_type(type2, val2) != 'bool':
        eprint('type mismatch')
        exit(53)
    set_val(val1, not get_val(type2, val2))


def INT2CHAR():
    if get_type(type2, val2) != 'int':
        eprint('type mismatch')
        exit(53)
    val = get_val(type2, val2)
    try:
        val = chr(val)
    except:
        eprint('int2char error')
        exit(58)
    set_val(val1, val)


def STRI2INT():
    if get_type(type2, val2) != 'string' or get_type(type3, val3) != 'int':
        eprint('type mismatch')
        exit(53)
    stri = get_val(type2, val2)
    index = get_val(type3, val3)
    if index < 0 or index > len(stri):
        eprint('stri2int error')
        exit(58)

    try:
        stri = chr(stri[index])
    except:
        eprint('stri2int error')
        exit(58)
    set_val(val1, stri)


def READ():
    if get_type(val3,type3) != 'type' or get_val(type3,val3) not in ['int','string','bool']:
        eprint('type mismatch')
        exit(53)
    typ = get_val(type3,val3)
    vstup = input()
    if typ == 'bool':
        if 'true' in vstup.lower():
            set_val(val1,True)
        else:
            set_val(val1,False)
    elif typ == 'int' and re.match('^[+-]?[\d]+$',vstup):
        set_val(val1,int(vstup))
    elif typ == 'string':
        set_val(val1,vstup)
    else:
        set_val(val1,None)


def WRITE():
    stri = get_val(type1, val1)
    print(xstr(stri), end='')


def CONCAT():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) != 'string':
        eprint('type mismatch - CONCAT')
        exit(53)
    set_val(val1, get_val(type2, val2) + get_val(type3, val3))


def STRLEN():
    if get_type(type2, val2) != 'string':
        eprint('type mismatch - STRLEN')
        exit(53)
    len = xstr(get_val(type2, val2))
    set_val(val1, len)


def GETCHAR():
    if get_type(type2, val2) != 'string' or get_type(type3, val3) != 'int':
        eprint('type mismatch')
        exit(53)
    stri = get_val(type2, val2)
    index = get_val(type3, val3)
    if index < 0 or index > len(stri):
        eprint('getchar error')
        exit(58)
    set_val(val1, stri[index])


def SETCHAR():
    if get_type(type2, val2) != 'int' or get_type(type3, val3) != 'string':
        eprint('type mismatch')
        exit(53)
    stri = get_val(type1, val1)
    index = get_val(type3, val3)
    if index < 0 or index > len(stri) or len(get_val(type3,val3) < 1):
        eprint('setchar error')
        exit(58)
    stri[index] = get_val(type3,val3)[0]
    set_val(val1, stri)


def TYPE():
    set_val(val1, get_type(type2,val2))


# nothing needed
def LABEL():
    pass


def JUMP():
    global i
    temp = labels.get(val1)
    if temp is None:
        eprint('undefined label')
        exit(52)
    # skok
    i = temp


def JUMPIFEQ():
    global i
    temp = labels.get(val1)
    if temp is None:
        eprint('undefined label')
        exit(52)

    if get_type(type2, val2) != get_type(type3, val3):
        eprint('type mismatch - JUMPIFEQ')
        exit(53)

    # skok
    if get_val(type2, val2) == get_val(type3, val3):
        i = temp


def JUMPIFNEQ():
    global i
    temp = labels.get(val1)
    if temp is None:
        eprint('undefined label')
        exit(52)

    if get_type(type2, val2) != get_type(type3, val3):
        eprint('type mismatch - JUMPIFEQ')
        exit(53)

    # skok
    if get_val(type2, val2) != get_val(type3, val3):
        i = temp


def EXIT():
    exit(0)


def DPRINT():
    stri = get_val(type1, val1)
    eprint(xstr(stri))


def BREAK():
    eprint('state of interpret:')


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


def argcheck(xml, type, value):
    translate = {
        'var': ['var'],
        'symb': ['int', 'bool', 'string', 'nil', 'var'],
        'label': ['label'],
        'type': ['type'],
    }
    # unknown type in xml
    if type not in translate.get(xml, {}):
        return False

    return re.match(regex.get(type), value) != None


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
        source = args.source
    else:
        source = sys.stdin
    if args.input is not None:
        input = open(args.input, "r")
    else:
        input = sys.stdin

    # load xml
    try:
        root = ET.parse(source).getroot()
    except:
        eprint("XML declaration not well-formed")
        exit(31)

    order_array = []
    # check xml structure
    if root.tag != 'program' or root.get('language') != 'IPPcode21' or len(root.attrib) != 1:
        exit(32)
    # check ins-xml
    for inst in root:
        if inst.tag != 'instruction' or inst.get('order') == None or switch.get(inst.get('opcode')) == None or len(
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
            if (argx.tag != 'arg' + str(arg + 1)) or argx.get('type') is None or len(argx.attrib) != 1:
                exit(32)
            # transform escaped string chars
            if argx.get('type') == 'string':
                reg = re.compile('\\\\(\d{3})')


                def replace(match):
                    return chr(int(match.group(1)))


                argx.text = reg.sub(replace, xstr(argx.text))

            # lexical & syntax check
            if not argcheck(arg_list[arg], argx.get('type'), xstr(argx.text)):
                exit(32)

    if len(order_array) != len(set(order_array)) or any(i < 0 for i in order_array):
        exit(32)

    # sort by instruction order
    root[:] = sorted(root, key=lambda child: int(child.get('order')))

    # prepare labels
    labels = {}
    for instruction in [i for i in root if i.get('opcode') == 'LABEL']:
        if instruction[0].text in labels:
            eprint("redefined label")
            exit(52)
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
