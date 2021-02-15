import re
import xml.etree.ElementTree as ET
import argparse
import sys
from typing import Dict, List, Any, Union, Callable

f_stack = [None]

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
    'string': '^.*$',
    'nil': '^nil$',
    'label': '^[a-zA-Z_\-$&%*!?][\w\-$&%*!?]*$',
    'type': '^int|bool|string|nil|float$',
    'float': '^.*$',
}


def nil(var):
    return 'nil'

def var(var):
    return var

def bool(var):
    return re.match('(?i)true',var) is not None
#TODO zjistit chyby
def float(var):
    try:
        tmp = float.fromhex(var)
    except:
        exit(-10)
    return tmp

cast = {
    'int': int,
    'bool': bool,
    'string': str,
    'nil': nil,
    'var': var,
    'float': float,
}


# returns real type - no var
def get_type(type, val):
    if type == 'var':
        m_frame = ramec.get(val[:2])
        if m_frame is None:
            eprint("frame missing")
            exit(54)
        if val not in m_frame:
            eprint("undefined variable")
            exit(52)
        return m_frame[val]['type']
    else:
        return type


def get_val(type, val):
    if type == 'var':
        m_frame = ramec.get(val[:2])
        if m_frame is None:
            eprint("frame missing")
            exit(54)
        if val not in m_frame:
            eprint("undefined variable")
            exit(52)
        return m_frame[val]['val']
    else:
        return cast[type](val)


def set_val(val, res, res_type):
    m_frame = ramec.get(val[:2])
    if m_frame is None:
        eprint("frame missing")
        exit(54)
    if val1 not in m_frame:
        eprint("undefined variable")
        exit(52)
    m_frame[val] = {'val': res, 'type': res_type}


def MOVE():
    set_val(val1, get_val(type2, val2), get_type(type2, val2))


def CREATEFRAME():
    ramec['TF'] = {}


def DEFVAR():
    m_frame = ramec.get(val1[:2])
    if m_frame is None:
        eprint("frame missing")
        exit(54)

    if val1 in m_frame:
        eprint("redefinition of variable")
        exit(52)
    # instrukce
    m_frame[val1] = {'val': None, 'type': None}


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
    val_stack.append({'val': get_val(type1, val1), 'type': get_type(type1, val1)})


def POPS():
    tmp = val_stack.pop()
    if tmp is None:
        eprint('var stack empty')
        exit(56)
    set_val(val1, tmp['val'], tmp['type'])


def ADD():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) != 'int':
        eprint('type mismatch - ADD')
        exit(53)
    set_val(val1, get_val(type2, val2) + get_val(type3, val3), get_type(type3, val3))


def SUB():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) != 'int':
        eprint('type mismatch - SUB')
        exit(53)
    set_val(val1, get_val(type2, val2) - get_val(type3, val3), get_type(type3, val3))


def MUL():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) != 'int':
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
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) not in ['int', 'bool', 'string', 'float']:
        eprint('type mismatch')
        exit(53)
    set_val(val1, get_val(type2, val2) < get_val(type3, val3), 'bool')


def GT():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) not in ['int', 'bool', 'string', 'float']:
        eprint('type mismatch')
        exit(53)
    set_val(val1, get_val(type2, val2) > get_val(type3, val3), 'bool')


def EQ():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) not in ['int', 'bool', 'string', 'float']:
        eprint('type mismatch')
        exit(53)
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
    if index < 0 or index > len(stri):
        eprint('stri2int error')
        exit(58)

    try:
        stri = chr(stri[index])
    except:
        eprint('stri2int error')
        exit(58)
    set_val(val1, stri, 'int')


def READ():
    if get_type(val3, type3) != 'type' or get_val(type3, val3) not in ['int', 'string', 'bool', 'float']:
        eprint('type mismatch')
        exit(53)
    typ = get_val(type3, val3)
    vstup = input()
    if typ == 'bool':
        if 'true' in vstup.lower():
            set_val(val1, True, 'bool')
        else:
            set_val(val1, False, 'bool')
    elif typ == 'int' and re.match('^[+-]?[\d]+$', vstup):
        set_val(val1, int(vstup), 'int')
    elif typ == 'string':
        set_val(val1, vstup, 'string')
    elif typ == 'float':
        set_val(val1, vstup, 'float')
    else:
        set_val(val1, 'nil', 'nil')


def WRITE():
    stri = get_val(type1, val1)
    print(xstr(stri), end='')


def CONCAT():
    if get_type(type2, val2) != get_type(type3, val3) or get_type(type3, val3) != 'string':
        eprint('type mismatch - CONCAT')
        exit(53)
    set_val(val1, get_val(type2, val2) + get_val(type3, val3), 'string')


def STRLEN():
    if get_type(type2, val2) != 'string':
        eprint('type mismatch - STRLEN')
        exit(53)
    len = xstr(get_val(type2, val2))
    set_val(val1, len, 'int')


def GETCHAR():
    if get_type(type2, val2) != 'string' or get_type(type3, val3) != 'int':
        eprint('type mismatch')
        exit(53)
    stri = get_val(type2, val2)
    index = get_val(type3, val3)
    if index < 0 or index > len(stri):
        eprint('getchar error')
        exit(58)
    set_val(val1, stri[index], 'string')


def SETCHAR():
    if get_type(type2, val2) != 'int' or get_type(type3, val3) != 'string':
        eprint('type mismatch')
        exit(53)
    stri = get_val(type1, val1)
    index = get_val(type3, val3)
    if index < 0 or index > len(stri) or len(get_val(type3, val3) < 1):
        eprint('setchar error')
        exit(58)
    stri[index] = get_val(type3, val3)[0]
    set_val(val1, stri, 'string')


def TYPE():
    set_val(val1, 'string@'+xstr(get_type(type2, val2)), 'string')


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
        eprint('type mismatch - JUMPIFNEQ')
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

def INT2FLOAT():
    if get_type(type2, val2) != 'int':
        eprint('type mismatch')
        exit(53)
    set_val(val1,float(get_val(type2, val2)),'float')


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


instructions = {
    "MOVE":         {'call': MOVE,      'types': ["var", "symb", ]},
    "CREATEFRAME":  {'call': CREATEFRAME,'types': []},
    "DEFVAR":       {'call': DEFVAR,    'types': ["var", ]},
    "PUSHFRAME":    {'call': PUSHFRAME, 'types': []},
    "POPFRAME":     {'call': POPFRAME,  'types': []},
    "CALL":         {'call': CALL,      'types': ["label", ]},
    "RETURN":       {'call': RETURN,    'types': []},
    "PUSHS":        {'call': PUSHS,     'types': ["symb", ]},
    "POPS":         {'call': POPS,      'types': ["var", ]},
    "ADD":          {'call': ADD,       'types': ["var", "symb", "symb", ]},
    "SUB":          {'call': SUB,       'types': ["var", "symb", "symb", ]},
    "MUL":          {'call': MUL,       'types': ["var", "symb", "symb", ]},
    "IDIV":         {'call': IDIV,      'types': ["var", "symb", "symb", ]},
    "LT":           {'call': LT,        'types': ["var", "symb", "symb", ]},
    "GT":           {'call': GT,        'types': ["var", "symb", "symb", ]},
    "EQ":           {'call': EQ,        'types': ["var", "symb", "symb", ]},
    "AND":          {'call': AND,       'types': ["var", "symb", "symb", ]},
    "OR":           {'call': OR,        'types': ["var", "symb", "symb", ]},
    "NOT":          {'call': NOT,       'types': ["var", "symb", ]},
    "INT2CHAR":     {'call': INT2CHAR,  'types': ["var", "symb", ]},
    "STRI2INT":     {'call': STRI2INT,  'types': ["var", "symb", "symb", ]},
    "READ":         {'call': READ,      'types': ["var", "type", ]},
    "WRITE":        {'call': WRITE,     'types': ["symb", ]},
    "CONCAT":       {'call': CONCAT,    'types': ["var", "symb", "symb", ]},
    "STRLEN":       {'call': STRLEN,    'types': ["var", "symb", ]},
    "GETCHAR":      {'call': GETCHAR,   'types': ["var", "symb", "symb", ]},
    "SETCHAR":      {'call': SETCHAR,   'types': ["var", "symb", "symb", ]},
    "TYPE":         {'call': TYPE,      'types': ["var", "symb", ]},
    "LABEL":        {'call': LABEL,     'types': ["label", ]},
    "JUMP":         {'call': JUMP,      'types': ["label", ]},
    "JUMPIFEQ":     {'call': JUMPIFEQ,  'types': ["label", "symb", "symb", ]},
    "JUMPIFNEQ":    {'call': JUMPIFNEQ, 'types': ["label", "symb", "symb", ]},
    "EXIT":         {'call': EXIT,      'types': ["symb", ]},
    "DPRINT":       {'call': DPRINT,    'types': ["symb", ]},
    "BREAK":        {'call': BREAK,     'types': []},
    "INT2FLOAT" :   {'call': INT2FLOAT, 'types':["var", 'symb',]},
    "FLOAT2INT" :   {'call': FLOAT2INT, 'types':["var", "symb", ]},
    "DIV" :         {'call': DIV,       'types':["var", 'symb', 'symb']},
}


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


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
        if inst.tag != 'instruction' or inst.get('order') is None or instructions.get(inst.get('opcode'), {}).get(
                'call') is None or len(
            inst.attrib) != 2:
            exit(32)
        order_array.append(int(inst.get('order')))
        # check args-xml need to sort first
        inst[:] = sorted(inst, key=lambda child: child.tag)
        arg_list = instructions.get(inst.get('opcode'))['types']
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

        if ac_opc not in instructions:
            eprint('wrong opcode')
            exit(10)
        instructions[ac_opc]['call']()
        i += 1
