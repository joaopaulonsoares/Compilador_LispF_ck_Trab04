import ox
import click
import pprint

lexer = ox.make_lexer([
    ('LOOP', r'loop'),
    ('DEC', r'dec'),
    ('INC', r'inc'),
    ('LPAR', r'\('),
    ('RPAR', r'\)'),
    ('RIGHT', r'right'),
    ('LEFT', r'left'),
    ('PRINT', r'print'),
    ('READ', r'read'),
    ('DO', r'do'),
    ('DO_AFTER', r'do-after'),
    ('DO_BEFORE', r'do-before'),
    ('ADD', r'add'),
    ('SUB', r'sub'),
    ('NUMBER', r'[0-9]+'),
    ('ignore_COMMENT', r';[^\n]*'),
    ('ignore_BREAK_LINE', r'\n'),
    ('ignore_SPACE', r'\s+')
])

tokens_list = ['LOOP',
               'DEC',
               'INC',
               'LPAR',
               'RPAR',
               'RIGHT',
               'LEFT',
               'PRINT',
               'READ',
               'DO',
               'DO_AFTER',
               'DO_BEFORE',
               'ADD',
               'SUB',
               'NUMBER']

parser = ox.make_parser([
    ('expr : LPAR RPAR', lambda x, y: '()'),
    ('expr : LPAR term RPAR', lambda x, y, z: y),
    ('term : atom term', lambda x, y: (x,) + y),
    ('term : atom', lambda x:(x,)),
    ('atom : expr', lambda x:x),
    ('atom : DEC', lambda x:x),
    ('atom : INC', lambda x:x),
    ('atom : LOOP', lambda x:x),
    ('atom : RIGHT', lambda x:x),
    ('atom : LEFT', lambda x:x),
    ('atom : PRINT', lambda x:x),
    ('atom : READ', lambda x:x),
    ('atom : DO', lambda x:x),
    ('atom : DO_AFTER', lambda x:x),
    ('atom : DO_BEFORE', lambda x:x),
    ('atom : ADD', lambda x:x),
    ('atom : SUB', lambda x:x),
    ('atom : NUMBER', int),
], tokens_list)


def do_after(command, old_array):
    array = []
    count = 0
    while count < len(old_array):
        if old_array[count] == 'add' or old_array[count] == 'sub':
            array.append(old_array[count])
            count += 1
        array.append(old_array[count])
        array.append(command)

        count += 1

    return array


def do_before(command, old_array):
    array = []
    count = 0
    while count < len(old_array):
        array.append(command)
        array.append(old_array[count])
        if old_array[count] == 'add' or old_array[count] == 'sub':
            count += 1
            array.append(old_array[count])

        count += 1

    return array


def lisp_f_ck_interpreter(tree, source_array, count):
    loop_active = False
    i = 0

    while i < len(tree):
        if isinstance(tree[i], tuple):
            source_array, count = lisp_f_ck_interpreter(tree[i], source_array, count)

        elif tree[i] == 'inc':
            source_array[count] += 1

        elif tree[i] == 'dec':
            source_array[count] -= 1

        elif tree[i] == 'right':
            count += 1
            if len(source_array) - 1 < count:
                source_array.append(0)

        elif tree[i] == 'left':
            count -= 1
            if count < 0:
                source_array.append(0)

        elif tree[i] == 'add':
            i += 1
            source_array[count] += tree[i]

        elif tree[i] == 'sub':
            i += 1
            source_array[count] -= tree[i]

        elif tree[i] == 'print':
            print(chr(source_array[count]), end='')

        elif tree[i] == 'read':
            source_array[count] = input('input: ')

        elif tree[i] == 'do-after':
            i += 1
            command = tree[i]
            i += 1
            array = do_after(command, list(tree[i]))
            lisp_f_ck_interpreter(array, source_array, count)

        elif tree[i] == 'do-before':
            i += 1
            command = tree[i]
            i += 1
            array = do_before(command, list(tree[i]))
            lisp_f_ck_interpreter(array, source_array, count)

        elif tree[i] == 'loop':
            if source_array[count] == 0:
                loop_active = False
                break
            else:
                loop_active = True

        if loop_active is True and i == len(tree) - 1:
            i = -1

        i += 1

    return source_array, count


def eval(tree):
    source_array = [0]
    count = 0
    print('\nOutput:')
    source_array, count = lisp_f_ck_interpreter(tree, source_array, count)
    print()


@click.command()
@click.argument('source', type=click.File('r'))
def make_tree(source):
    source_code = source.read()
    tokens = lexer(source_code)
    print('Tokens List:\n', tokens)
    tree = parser(tokens)
    print("\nSyntax Tree:")
    pprint.pprint(tree)
    eval(tree)


if __name__ == '__main__':
    make_tree()
