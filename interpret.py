import re
import xml.etree.ElementTree as ET
import argparse
import sys

f_stack = [None]
#global variable for avaliable frames
ramec = {
    'GF': {},
    'LF': None,
    'TF': None,
}

xstr = lambda s: '' if s is None else str(s)

regex = {
    'var': '^(?:LF|GF|TF)@[a-zA-Z_\-$&%*!?][\w\-$&%*!?]*$',
    'int': '^[+-]?[\d]+$',
    'bool': '^true|false$',
    'string': '',
    'nil': '^nil$',
    'label': '^[a-zA-Z_\-$&%*!?][\w\-$&%*!?]*$',
    'type': '^(int|bool|string|nil|float)$',
    'float': '',
}


def nil(var):
    return 'nil'


def var(var):
    return var


def bool(var):
    return re.match('(?i)true', var) is not None


def floati(var):
    try:
        tmp = float.fromhex(var)
    except:
        exit(-10)
    return tmp


cast = {
    'int': int,
    'bool': bool,
    'string': xstr,
    'nil': nil,
    'var': var,
    'float': floati,
    'type': xstr,
}


# returns real type - no var
def get_type(type, val):
    if type == 'var':
        m_frame = ramec.get(val[:2])
        if m_frame is None:
            eprint("frame missing")
            exit(55)
        if val[3:] not in m_frame:
            eprint("undefined variable")
            exit(54)
        tmp = m_frame[val[3:]]['type']
        if tmp is None:
            eprint("undefined value")
            exit(56)
        return tmp
    else:
        return type


def get_val(type, val):
    if type == 'var':
        m_frame = ramec.get(val[:2])
        if m_frame is None:
            eprint("frame missing")
            exit(55)
        if val[3:] not in m_frame:
            eprint("undefined variable")
            exit(54)
        tmp = m_frame[val[3:]]['val']
        if tmp is None:
            eprint("undefined value")
            exit(56)
        return tmp

    else:
        return cast[type](val)


def set_val(val, res, res_type):
    m_frame = ramec.get(val[:2])
    if m_frame is None:
        eprint("frame missing")
        exit(55)
    if val[3:] not in m_frame:
        eprint("undefined variable")
        exit(54)
    m_frame[val[3:]] = {'val': res, 'type': res_type}


def MOVE():
    set_val(val1, get_val(type2, val2), get_type(type2, val2))


def CREATEFRAME():
    ramec['TF'] = {}


def DEFVAR():
    m_frame = ramec.get(val1[:2])
    if m_frame is None:
        eprint("frame missing")
        exit(55)

    if val1[3:] in m_frame:
        eprint("redefinition of variable")
        exit(52)
    # instrukce
    m_frame[val1[3:]] = {'val': None, 'type': None}


def PUSHFRAME():
    if ramec['TF'] is None:
        eprint('undefined TF')
        exit(55)
    f_stack.append(ramec['LF'])
    ramec['LF'] = ramec['TF']
    ramec['TF'] = None


def POPFRAME():
    if ramec['LF'] is None:
        eprint('undefined LF')
        exit(55)
    ramec['TF'] = ramec['LF']
    ramec['LF'] = f_stack.pop()

#help structure for CALL/RETURN instructions
store_calls = [None]


def CALL():
    global i
    store_calls.append(i)
    # has same call siganture
    JUMP()


def RETURN():
    global i
    tmp = store_calls.pop()
    if tmp is None:
        eprint('call stack empty')
        exit(56)
    i = tmp

#help structure for stack instructions
val_stack = [None]


def PUSHS():
    val_stack.append({'val': get_val(type1, val1), 'type': get_type(type1, val1)})


def POPS():
    tmp = val_stack.pop()
    if tmp is None:
        eprint('var stack empty')
        exit(56)
    set_val(val1, tmp['val'], tmp['type'])


def ADD():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) not in ['int', 'float']:
        eprint('type mismatch - ADD')
        exit(53)
    set_val(val1, get_val(type2, val2) + get_val(type3, val3), get_type(type3, val3))


def SUB():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) not in ['int', 'float']:
        eprint('type mismatch - SUB')
        exit(53)
    set_val(val1, get_val(type2, val2) - get_val(type3, val3), get_type(type3, val3))


def MUL():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) not in ['int', 'float']:
        eprint('type mismatch - MUL')
        exit(53)
    set_val(val1, get_val(type2, val2) * get_val(type3, val3), get_type(type3, val3))


def IDIV():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) != 'int':
        eprint('type mismatch - IDIV')
        exit(53)
    if get_val(type3, val3) == 0:
        eprint('division by zero')
        exit(57)
    set_val(val1, get_val(type2, val2) // get_val(type3, val3), 'int')


def LT():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) not in ['int', 'bool', 'string','float']:
        eprint('type mismatch')
        exit(53)
    set_val(val1, get_val(type2, val2) < get_val(type3, val3), 'bool')


def GT():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) not in ['int', 'bool', 'string','float']:
        eprint('type mismatch')
        exit(53)
    set_val(val1, get_val(type2, val2) > get_val(type3, val3), 'bool')


def EQ():
    typ2 = get_type(type2, val2)
    typ3 = get_type(type3, val3)

    #EQ can compare nil
    if typ2 == 'nil' and typ3 == 'nil':
        set_val(val1, 'true', 'bool')
    elif typ2 == 'nil' or typ3 == 'nil':
        set_val(val1, 'false', 'bool')
    elif typ2 != typ3 or typ3 not in ['int', 'bool', 'string', 'float']:
        eprint('type mismatch')
        exit(53)
    else:
        set_val(val1, get_val(type2, val2) == get_val(type3, val3), 'bool')

def AND():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) != 'bool':
        eprint('type mismatch')
        exit(53)
    set_val(val1, get_val(type2, val2) and get_val(type3, val3), 'bool')


def OR():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) != 'bool':
        eprint('type mismatch')
        exit(53)
    set_val(val1, get_val(type2, val2) or get_val(type3, val3), 'bool')


def NOT():
    if get_type(type2, val2) != 'bool':
        eprint('type mismatch')
        exit(53)
    set_val(val1, not get_val(type2, val2), 'bool')


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
    set_val(val1, val, 'string')


def STRI2INT():
    if get_type(type2, val2) != 'string' or get_type(type3, val3) != 'int':
        eprint('type mismatch')
        exit(53)
    stri = get_val(type2, val2)
    index = get_val(type3, val3)
    if index < 0 or index >= len(stri):
        eprint('stri2int error')
        exit(58)

    try:
        stri = ord(stri[index])
    except:
        eprint('stri2int error')
        exit(58)
    set_val(val1, stri, 'int')


def READ():
    typ = get_val(type2, val2)
    if typ not in ['int', 'string', 'bool', 'float']:
        eprint('type mismatch')
        exit(53)
    _vstup = inputs.readline()
    flag = '\n' in _vstup
    vstup = _vstup.rstrip('\n')
    #empty/incorect input -> nil
    if typ == 'string' and (flag or (len(vstup) > 0)):
        set_val(val1, vstup, 'string')
    elif len(vstup) == 0:
        set_val(val1, 'nil', 'nil')
    elif typ == 'bool':
        if 'true' == vstup.lower():
            set_val(val1, True, 'bool')
        else:
            set_val(val1, False, 'bool')
    elif typ == 'int':
        try:
            set_val(val1, int(vstup), 'int')
        except:
            set_val(val1, 'nil', 'nil')
    elif typ == 'float':
        try:
            set_val(val1, float.fromhex(vstup), 'float')
        except:
            set_val(val1, 'nil', 'nil')
    else:
        exit(99)


def WRITE():
    stri = get_val(type1, val1)
    if get_type(type1, val1) == 'float':
        print(float.hex(stri), end='')
    elif get_type(type1, val1) == 'nil':
        return #''
    elif get_type(type1, val1) == 'bool':
        print(str(stri).lower(), end='')
    else:
        print(stri, end='')


def CONCAT():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) != 'string':
        eprint('type mismatch - CONCAT')
        exit(53)
    set_val(val1, get_val(type2, val2) + get_val(type3, val3), 'string')


def STRLEN():
    if get_type(type2, val2) != 'string':
        eprint('type mismatch - STRLEN')
        exit(53)
    length = len(get_val(type2, val2))
    set_val(val1, length, 'int')


def GETCHAR():
    if get_type(type2, val2) != 'string' or get_type(type3, val3) != 'int':
        eprint('type mismatch')
        exit(53)
    stri = get_val(type2, val2)
    index = get_val(type3, val3)
    if index < 0 or index >= len(stri):
        eprint('getchar error')
        exit(58)
    set_val(val1, stri[index], 'string')


def SETCHAR():
    if get_type(type2, val2) != 'int' or get_type(type3, val3) != 'string' or get_type(type1, val1) != 'string':
        eprint('type mismatch')
        exit(53)
    stri = get_val(type1, val1)
    index = get_val(type2, val2)
    if index < 0 or index >= len(stri) or len(get_val(type3, val3)) < 1:
        eprint('setchar error')
        exit(58)
    set_val(val1, stri[:index] + get_val(type3, val3)[0] + stri[index+1:], 'string')


def TYPE():
    #get_type but uninitalized var is allowed
    if type2 == 'var':
        m_frame = ramec.get(val2[:2])
        if m_frame is None:
            eprint("frame missing")
            exit(55)
        if val2[3:] not in m_frame:
            eprint("undefined variable")
            exit(54)
        tmp = m_frame[val2[3:]]['type']
        if tmp is None:
            alter_type = ''
        else:
            alter_type = tmp
    else:
        alter_type = type2

    set_val(val1, alter_type, 'string')

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

    typ2 = get_type(type2, val2)
    typ3 = get_type(type3, val3)
    # EQ can compare nil
    if typ2 == 'nil' and typ3 == 'nil':
        i = temp
    elif typ2 == 'nil' or typ3 == 'nil':
        return
    elif typ2 != typ3 or typ3 not in ['int', 'bool', 'string', 'float']:
        eprint('type mismatch - JUMPIFEQ')
        exit(53)
    elif get_val(type2, val2) == get_val(type3, val3):
        i = temp


def JUMPIFNEQ():
    global i
    temp = labels.get(val1)
    if temp is None:
        eprint('undefined label')
        exit(52)

    typ2 = get_type(type2, val2)
    typ3 = get_type(type3, val3)
    # EQ can compare nil
    if typ2 == 'nil' and typ3 == 'nil':
        return
    elif typ2 == 'nil' or typ3 == 'nil':
        i = temp
    elif typ2 != typ3 or typ3 not in ['int', 'bool', 'string', 'float']:
        eprint('type mismatch - JUMPIFEQ')
        exit(53)
    elif get_val(type2, val2) != get_val(type3, val3):
        i = temp


def EXIT():
    if get_type(type1, val1) != 'int':
        exit(53)
    tmp = get_val(type1, val1)
    if tmp < 0 or tmp > 49:
        exit(57)
    exit(tmp)


def DPRINT():
    eprint(get_val(type1, val1))


def BREAK():
    eprint('state of interpret:', str(i)+'. line\nLF:', ramec['LF'], '\nTF:', ramec['TF'], '\nGF:', ramec['GF'])


def INT2FLOAT():
    if get_type(type2, val2) != 'int':
        eprint('type mismatch')
        exit(53)
    set_val(val1, float(get_val(type2, val2)), 'float')


def FLOAT2INT():
    if get_type(type2, val2) != 'float':
        eprint('type mismatch')
        exit(53)
    set_val(val1, int(get_val(type2, val2)), 'int')


def DIV():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) != 'float':
        eprint('type mismatch - DIV')
        exit(53)
    if get_val(type3, val3) == 0:
        eprint('division by zero')
        exit(57)
    set_val(val1, get_val(type2, val2) / get_val(type3, val3), 'float')


# STACK extension
def CLEARS():
    global val_stack
    val_stack = [None]


def ADDS():
    if len(val_stack) < 3:
        exit(56)
    symb2 = val_stack.pop()
    if symb2['type'] != val_stack[-1]['type'] or symb2['type'] not in ['int', 'float']:
        exit(53)
    val_stack[-1]['val'] += symb2['val']


def SUBS():
    if len(val_stack) < 3:
        exit(56)
    symb2 = val_stack.pop()
    if symb2['type'] != val_stack[-1]['type'] or symb2['type'] not in ['int', 'float']:
        exit(53)
    val_stack[-1]['val'] -= symb2['val']


def MULS():
    if len(val_stack) < 3:
        exit(56)
    symb2 = val_stack.pop()
    if symb2['type'] != val_stack[-1]['type'] or symb2['type'] not in ['int', 'float']:
        exit(53)
    val_stack[-1]['val'] *= symb2['val']


def IDIVS():
    if len(val_stack) < 3:
        exit(56)
    symb2 = val_stack.pop()
    if symb2['type'] != val_stack[-1]['type'] or symb2['type'] != 'int':
        exit(53)
    if symb2['val'] == 0:
        eprint('division by zero')
        exit(57)
    val_stack[-1]['val'] //= symb2['val']


def LTS():
    if len(val_stack) < 3:
        exit(56)
    symb2 = val_stack.pop()
    if symb2['type'] != val_stack[-1]['type'] or symb2['type'] not in ['int', 'bool', 'string', 'float']:
        exit(53)
    val_stack[-1] = {'val': (val_stack[-1]['val'] < symb2['val']), 'type': 'bool'}


def GTS():
    if len(val_stack) < 3:
        exit(56)
    symb2 = val_stack.pop()
    if symb2['type'] != val_stack[-1]['type'] or symb2['type'] not in ['int', 'bool', 'string', 'float']:
        exit(53)
    val_stack[-1] = {'val': (val_stack[-1]['val'] > symb2['val']), 'type': 'bool'}


def EQS():
    if len(val_stack) < 3:
        exit(56)
    symb2 = val_stack.pop()
    # EQ can compare nil
    if symb2['type'] == 'nil' and val_stack[-1]['type'] == 'nil':
        val_stack[-1] = {'val': True, 'type': 'bool'}
    elif symb2['type'] == 'nil' or val_stack[-1]['type'] == 'nil':
        val_stack[-1] = {'val': False, 'type': 'bool'}
    elif symb2['type'] != val_stack[-1]['type']:
        exit(53)
    else:
        val_stack[-1] = {'val': (val_stack[-1]['val'] == symb2['val']), 'type': 'bool'}


def ANDS():
    if len(val_stack) < 3:
        exit(56)
    symb2 = val_stack.pop()
    if symb2['type'] != val_stack[-1]['type'] or symb2['type'] != 'bool':
        exit(53)
    val_stack[-1] = {'val': (val_stack[-1]['val'] and symb2['val']), 'type': 'bool'}


def ORS():
    if len(val_stack) < 3:
        exit(56)
    symb2 = val_stack.pop()
    if symb2['type'] != val_stack[-1]['type'] or symb2['type'] != 'bool':
        exit(53)
    val_stack[-1] = {'val': (val_stack[-1]['val'] or symb2['val']), 'type': 'bool'}


def NOTS():
    if len(val_stack) < 2:
        exit(56)
    if val_stack[-1]['type'] != 'bool':
        exit(53)
    val_stack[-1]['val'] = not val_stack[-1]['val']


def INT2CHARS():
    if len(val_stack) < 2:
        exit(56)
    if val_stack[-1]['type'] != 'int':
        exit(53)
    try:
        val_stack[-1] = {'val': chr(val_stack[-1]['val']), 'type': 'string'}
    except:
        eprint('int2char error')
        exit(58)


def STRI2INTS():
    if len(val_stack) < 3:
        exit(56)
    symb2 = val_stack.pop()
    if val_stack[-1]['type'] != 'string' or symb2['type'] != 'int':
        exit(53)
    index = symb2['val']
    if index < 0 or index >= len(val_stack[-1]['val']):
        exit(58)

    try:
        val_stack[-1] = {'val': ord(val_stack[-1]['val'][index]), 'type': 'int'}
    except:
        exit(58)


def JUMPIFEQS():
    global i
    if len(val_stack) < 3:
        exit(56)
    temp = labels.get(val1)
    if temp is None:
        eprint('undefined label')
        exit(52)

    symb2 = val_stack.pop()
    symb1 = val_stack.pop()

    if symb1['type'] == 'nil' and symb2['type'] == 'nil':
        i = temp
    elif symb1['type'] == 'nil' or symb2['type'] == 'nil':
        return
    elif symb1['type'] != symb2['type']:
        exit(53)
    elif symb1['val'] == symb2['val']:
        i = temp


def JUMPIFNEQS():
    global i
    if len(val_stack) < 3:
        exit(56)
    temp = labels.get(val1)
    if temp is None:
        eprint('undefined label')
        exit(52)

    symb2 = val_stack.pop()
    symb1 = val_stack.pop()

    if symb1['type'] == 'nil' and symb2['type'] == 'nil':
        return
    elif symb1['type'] == 'nil' or symb2['type'] == 'nil':
        i = temp
    elif symb1['type'] != symb2['type']:
        exit(53)
    elif symb1['val'] != symb2['val']:
        i = temp

#list of avaliable instruction with interpret function to call and signature for lexical/syntax analysis
instructions = {
    "MOVE": {'call': MOVE, 'types': ["var", "symb", ]},
    "CREATEFRAME": {'call': CREATEFRAME, 'types': []},
    "DEFVAR": {'call': DEFVAR, 'types': ["var", ]},
    "PUSHFRAME": {'call': PUSHFRAME, 'types': []},
    "POPFRAME": {'call': POPFRAME, 'types': []},
    "CALL": {'call': CALL, 'types': ["label", ]},
    "RETURN": {'call': RETURN, 'types': []},
    "PUSHS": {'call': PUSHS, 'types': ["symb", ]},
    "POPS": {'call': POPS, 'types': ["var", ]},
    "ADD": {'call': ADD, 'types': ["var", "symb", "symb", ]},
    "SUB": {'call': SUB, 'types': ["var", "symb", "symb", ]},
    "MUL": {'call': MUL, 'types': ["var", "symb", "symb", ]},
    "IDIV": {'call': IDIV, 'types': ["var", "symb", "symb", ]},
    "LT": {'call': LT, 'types': ["var", "symb", "symb", ]},
    "GT": {'call': GT, 'types': ["var", "symb", "symb", ]},
    "EQ": {'call': EQ, 'types': ["var", "symb", "symb", ]},
    "AND": {'call': AND, 'types': ["var", "symb", "symb", ]},
    "OR": {'call': OR, 'types': ["var", "symb", "symb", ]},
    "NOT": {'call': NOT, 'types': ["var", "symb", ]},
    "INT2CHAR": {'call': INT2CHAR, 'types': ["var", "symb", ]},
    "STRI2INT": {'call': STRI2INT, 'types': ["var", "symb", "symb", ]},
    "READ": {'call': READ, 'types': ["var", "type", ]},
    "WRITE": {'call': WRITE, 'types': ["symb", ]},
    "CONCAT": {'call': CONCAT, 'types': ["var", "symb", "symb", ]},
    "STRLEN": {'call': STRLEN, 'types': ["var", "symb", ]},
    "GETCHAR": {'call': GETCHAR, 'types': ["var", "symb", "symb", ]},
    "SETCHAR": {'call': SETCHAR, 'types': ["var", "symb", "symb", ]},
    "TYPE": {'call': TYPE, 'types': ["var", "symb", ]},
    "LABEL": {'call': LABEL, 'types': ["label", ]},
    "JUMP": {'call': JUMP, 'types': ["label", ]},
    "JUMPIFEQ": {'call': JUMPIFEQ, 'types': ["label", "symb", "symb", ]},
    "JUMPIFNEQ": {'call': JUMPIFNEQ, 'types': ["label", "symb", "symb", ]},
    "EXIT": {'call': EXIT, 'types': ["symb", ]},
    "DPRINT": {'call': DPRINT, 'types': ["symb", ]},
    "BREAK": {'call': BREAK, 'types': []},
    "INT2FLOAT": {'call': INT2FLOAT, 'types': ["var", 'symb', ]},
    "FLOAT2INT": {'call': FLOAT2INT, 'types': ["var", "symb", ]},
    "DIV": {'call': DIV, 'types': ["var", 'symb', 'symb']},
    "CLEARS": {'call': CLEARS, 'types': []},
    "ADDS": {'call': ADDS, 'types': []},
    "SUBS": {'call': SUBS, 'types': []},
    "MULS": {'call': MULS, 'types': []},
    "IDIVS": {'call': IDIVS, 'types': []},
    "LTS": {'call': LTS, 'types': []},
    "GTS": {'call': GTS, 'types': []},
    "EQS": {'call': EQS, 'types': []},
    "ANDS": {'call': ANDS, 'types': []},
    "ORS": {'call': ORS, 'types': []},
    "NOTS": {'call': NOTS, 'types': []},
    "INT2CHARS": {'call': INT2CHARS, 'types': []},
    "STRI2INTS": {'call': STRI2INTS, 'types': []},
    "JUMPIFEQS": {'call': JUMPIFEQS, 'types': ["label",]},
    "JUMPIFNEQS": {'call': JUMPIFNEQS, 'types': ["label",]},
}

#print to stderr
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

#syntax/lexical check of argument
def argcheck(xml, type, value):
    translate = {
        'var': ['var'],
        'symb': ['int', 'bool', 'string', 'nil', 'var', 'float'],
        'label': ['label'],
        'type': ['type'],
    }
    # unknown type in xml
    if type not in translate.get(xml, {}):
        return False

    return re.match(regex.get(type), value) is not None


if __name__ == "__main__":
    # help override
    if len(sys.argv) > 2 and ('-h' in sys.argv or '--help' in sys.argv):
        exit(10)
    #parsing arguments
    parser = argparse.ArgumentParser(description='IPP project'
                                                 'note: at least 1 parametr must be specified ( -s or -i) '
                                                 'interprets IPPcode21 from xml file'
                                                 'outputs to stdout')
    parser.add_argument('-s', '--source', help='source file with xml')
    parser.add_argument('-i', '--input', help='file with input for given program\n')
    args = parser.parse_args()
    # help has ben writen by parse_args

    if args.source is None and args.input is None:
        eprint("optional argument needed")
        exit(10)
    if args.source is not None:
        try:
            source = open(args.source, "r")
        except:
            eprint('failed to open input file')
            exit(11)
    else:
        source = sys.stdin
    if args.input is not None:
        try:
            inputs = open(args.input, "r")
        except:
            eprint('failed to open input file')
            exit(11)
    else:
        inputs = sys.stdin

    # load xml
    try:
        root = ET.parse(source).getroot()
    except:
        eprint("XML not well-formed")
        exit(31)

    order_array = []
    # check xml structure
    if root.tag != 'program' or root.get('language').lower() != 'ippcode21' or len(
            [x for x in root.attrib if x not in ['language', 'name', 'description']]) != 0:
        exit(32)
    # check instructions in xml
    for inst in root:
        if inst.tag != 'instruction' or inst.get('order') is None or instructions.get(xstr(inst.get('opcode')).upper(), {}).get(
                'call') is None or len(inst.attrib) != 2:
            exit(32)
        try:
            order_array.append(int(inst.get('order')))
        except:
            exit(32)

        # check args-xml need to sort first
        inst[:] = sorted(inst, key=lambda child: child.tag)
        arg_list = instructions.get(inst.get('opcode').upper())['types']
        if len(inst) != len(arg_list):
            exit(32)
        for arg in range(len(arg_list)):
            argx = inst[arg]
            if (argx.tag != 'arg' + str(arg + 1)) or argx.get('type') is None or len(argx.attrib) != 1:
                exit(32)

            # transform escaped string chars
            if argx.get('type').lower() == 'string':
                reg = re.compile('\\\\(\d{3})')

                def replace(match):
                    return chr(int(match.group(1)))

                argx.text = reg.sub(replace, xstr(argx.text))

            # lexical & syntax check
            if not argcheck(arg_list[arg], argx.get('type').lower(), xstr(argx.text)):
                exit(32)

    if len(order_array) != len(set(order_array)) or any(i < 1 for i in order_array):
        exit(32)

    # sort by instruction order
    root[:] = sorted(root, key=lambda child: int(child.get('order')))

    # prepare labels
    labels = {}
    for instruction in [i for i in root if i.get('opcode').upper() == 'LABEL']:
        if instruction[0].text in labels:
            eprint("redefined label")
            exit(52)
        labels[instruction[0].text] = list(root).index(instruction)

    # intepret loop
    i = 0
    ma = len(root)
    while i < ma:
        ac_in = root[i]
        ac_opc = ac_in.get('opcode').upper()

        type1 = None
        val1 = None
        type2 = None
        val2 = None
        type3 = None
        val3 = None
        try:
            type1 = ac_in.find('arg1').get('type').lower()
            val1 = ac_in.find('arg1').text
            type2 = ac_in.find('arg2').get('type').lower()
            val2 = ac_in.find('arg2').text
            type3 = ac_in.find('arg3').get('type').lower()
            val3 = ac_in.find('arg3').text
        except:
            pass

        instructions[ac_opc]['call']()
        i += 1
    #close files
    if args.source is not None:
        source.close()
    if args.input is not None:
        inputs.close()
