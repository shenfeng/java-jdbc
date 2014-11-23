# encoding: utf8

__author__ = 'Feng Shen <shenedu@gmail.com>'

import re
import os
import logging
import argparse

from tornado import template


FORMAT = '%(asctime)-15s %(name)s:%(lineno)d %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

parser = argparse.ArgumentParser(description="Generate alading xml")

parser.add_argument('--input', type=str, default='', help='SQL like definition file, see example.sf')
parser.add_argument('--out', type=str, default="", help='When to put the generated Java code')
parser.add_argument('--test', type=bool, default=False, help='Generate test code')
parser.add_argument('--static', type=bool, default=False,
                    help='Generate static names for each name in the struct: public static final int ID = "ID"')

ARGS = parser.parse_args()

DIR = os.path.abspath(os.path.dirname(__file__))

FUNC = 'func'
STRUCT = 'struct'

TYPE_MAPPING = [
    ('list<i32>', 'List<Integer>'),
    ('list<', 'List<'),
    ('i32', 'int'),
    ('i64', 'long'),
    ('bool', 'boolean'),
    ('string', 'String'),
    ('datetime', 'Timestamp')
]


def convert_to_java_type(t):
    for k, v in TYPE_MAPPING:
        t = t.replace(k, v)

    return t


def java_name2_sql_name(n):
    """yourName -> your_name"""
    return re.sub('[A-Z]', lambda x: '_' + x.group().lower(), n)


def parse_sqls(sqls, args):
    sql = ' '.join(sqls)
    args = {name: type for type, name in args}
    sql = sql.replace('\S+', ' ').replace('\n', '')
    # print sql, args

    holders = re.findall(':([a-zA-Z\.]+)', sql)

    sql_args, idx = [], 0

    for h in holders:
        arg = h
        if '.' in arg:
            arg = h.split('.')[0]

        if arg not in args:
            raise Exception(":%s is not an argument in %s" % (h, sql))

        if 'List' in args[arg]:
            sql = re.sub(':%s' % h, '" + join(%s) + "' % h, sql)
        else:
            idx += 1
            sql_args.append((idx, h))

    ps_sql = re.sub(':[a-zA-Z\.]+', '?', sql)

    return ps_sql, sql_args


def run_tests():
    assert 'company_id' == java_name2_sql_name('companyId')

    input_args = [("int", "id"), ("Bean", "arg")]

    sql, args = parse_sqls(['SELECT * FROM table WHERE id = :id AND name = :arg.name'], input_args)

    assert sql == 'SELECT * FROM table WHERE id = ? AND name = ?'
    assert args == [(1, 'id'), (2, 'arg.name')]
    assert len(args) == 2

    input_args = [("List<Integer>", "ids"), ("Bean", "arg")]
    sql, args = parse_sqls(['SELECT * FROM table WHERE id IN (:ids) AND name = :arg.name'], input_args)

    assert sql == 'SELECT * FROM table WHERE id IN (" + join(ids) + ") AND name = ?'
    assert args == [(1, 'arg.name')]

    print 'tests pass'


run_tests()


class Row(dict):
    """A dict that allows for object-like property access syntax."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


METHODS = dict(
    int=('getInt', '0'),
    long=('getLong', '0'),
    String=('getString', "null"),
    Timestamp=('getTimestamp', "null"),
    boolean=('getBoolean', "false"),
    double=('getDouble', '0.0'),
)


class Struct(object):
    def __init__(self, line):
        # struct Interview {
        if 'extends' not in line:
            self.name = line.strip('{').split()[-1].strip()
            self.extends = None
        else:
            _, self.name, _, self.extends = line.strip('{').split()
            # struct JobsWithGeo extends FetchedJob
        self.fields = []

    def add_field(self, line):
        type, name = convert_to_java_type(line.strip(',;').strip()).split()
        self.fields.append((type, name))

    def __str__(self):
        return '%s {\n%s\n}\n' % (self.name, '\n'.join('%s %s' % f for f in self.fields))

    @property
    def fields_rs(self):
        results = []

        for idx, (t, name) in enumerate(self.fields):
            results.append(Row(
                # var='f%d' % (idx + 1),
                var=name,
                field=java_name2_sql_name(name),
                name=name,
                type=t,
                method=METHODS[t][0]
            ))

        return results

    @property
    def static(self):
        return ARGS.static


class Func(object):
    def __init__(self, line):
        _, resp, name, _ = re.split('\s+|\(', line, 3)
        args = convert_to_java_type(re.search('\((.*)\)', line).group(1)).strip()

        self.resp = convert_to_java_type(resp)
        self.name = name
        self.args = []

        if args:
            for arg in args.split(','):
                t, name = arg.split()
                self.args.append((t, name))

        self.sqls = []

    def add_sql(self, line):
        self.sqls.append(line)

    def __str__(self):
        return '%s %s (%s)\n%s\n' % (
            self.resp, self.name, ','.join(['%s %s' % t for t in self.args]), '\n'.join(self.sqls))

    @property
    def sql(self):
        # sql = ' '.join(self.sqls)
        # sql = sql.replace(r'\s+', ' ')

        sql, args = parse_sqls(self.sqls, self.args)
        return sql

    @property
    def sql_args(self):
        sql, args = parse_sqls(self.sqls, self.args)
        return args

    @property
    def resp_is_list(self):
        return 'list' in self.resp.lower()

    @property
    def is_primitive(self):
        m = dict([(l.lower(), r) for l, r in METHODS.items()])
        if self.resp.lower() in m:
            return m[self.resp.lower()]
        else:
            return ''

            # if self.resp.lower() in [l.lower() for l in METHODS.keys()]:
            #
            # return ''

    @property
    def has_resp(self):
        return 'void' not in self.resp.lower()

    @property
    def generate_id(self):
        return 'insert' in self.sql.lower() and 'int' in self.resp.lower()

    @property
    def update_insert(self):
        return 'update ' in self.sql.lower() or 'insert ' in self.sql.lower()

    @property
    def resp_bean(self):
        if self.resp_is_list:
            return re.search('<(.+)>', self.resp).group(1)
        else:
            return self.resp


class DbApi(object):
    def __init__(self):
        self.namespace = ''
        self.structs = []
        self.funcs = []


# FUNC_START, FUNC_MID, FUNC_END, STRUCT_START, STRUCT_MID, STRUCT_END = range(6)

IN_FUNC, IN_STRUCT, OTHER = range(3)


def parse_file(f):
    dbapi = DbApi()
    state = OTHER

    for line in open(f):
        # clean and remove comment
        idx = line.find('//')
        if idx >= 0:
            line = line[:idx]
        line = line.strip()

        if not line:
            continue

        if 'namespace' in line:
            dbapi.namespace = line.split()[-1]
            continue

        if line.startswith(STRUCT):
            state = IN_STRUCT
            struct = Struct(line)
        elif line.startswith(FUNC):
            state = IN_FUNC
            func = Func(line)
        elif line == '}':
            if state == IN_FUNC:
                dbapi.funcs.append(func)
            elif state == IN_STRUCT:
                dbapi.structs.append(struct)
            state = OTHER
        else:
            if state == IN_FUNC:
                func.add_sql(line)
            elif state == IN_STRUCT:
                struct.add_field(line)

    loader = template.Loader(DIR, autoescape=None)

    folder = dbapi.namespace.replace('.', '/')

    def write_to_file(name, data):
        f = '%s/%s/%s.java' % (ARGS.out, folder, name)
        if not os.path.isdir(os.path.dirname(f)):
            os.makedirs(os.path.dirname(f))

        open(f, 'w').write(data)

    for bean in dbapi.structs:
        java = loader.load('bean.tpl').generate(bean=bean, ns=dbapi.namespace)
        write_to_file(bean.name, java)

    fname = os.path.splitext(ARGS.input)[0].capitalize()

    class_name = "%sApi" % fname

    java = loader.load('api.tpl').generate(funcs=dbapi.funcs, ns=dbapi.namespace, class_name=class_name)
    write_to_file(class_name, java)

    if ARGS.test:
        java = loader.load('api_test.tpl').generate(funcs=dbapi.funcs, ns=dbapi.namespace)
        write_to_file("DBApiTest", java)


if __name__ == '__main__':
    if ARGS.input and ARGS.out:
        parse_file(ARGS.input)
    else:
        parser.print_help()

