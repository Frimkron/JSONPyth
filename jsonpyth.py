import re
import logging
import pyparsing as pp


class ParseError(Exception):

    def __init__(self, linetext, col, msg):
        self.linetext = linetext
        self.col = col
        self.msg = msg

    def __str__(self):
        return '{}, here:\n{}\n{}^'.format(self.msg, self.linetext, ' '*(self.col-1))


class PythonSyntaxError(ParseError):

    def __str__(self):
        return 'Python syntax error - ' + super().__str__()
    

class JsonPathSyntaxError(ParseError):  

    def __str__(self):
        return 'JSONPath syntax error - ' + super().__str__()


class _Parsed:

    TEMP_CURR_VAR = '__current'
    TEMP_ROOT_VAR = '__root'

    def __init__(self, tokens=None, **values):    
        self._values = dict(tokens.items()) if tokens is not None else values
        for name,val in self._values.items():
            setattr(self, name, val)

    def __repr__(self):
        return '{}({})'.format(type(self).__name__, 
                               ','.join('{}={}'.format(k,v) for k,v in self._values.items()))

    def property_of(self, node, propname):
        obj, path = node
        return (obj[propname], '{}["{}"]'.format(path, propname.replace('\\','\\\\').replace('"','\\"')))

    def index_of(self, node, index):
        obj, path = node
        return (obj[index], '{}[{}]'.format(path, index))

    def all_children_of(self, node):
        obj, path = node
        if isinstance(obj, (list, tuple)):
            return [self.index_of(node,i) for i in range(len(obj))]
        elif isinstance(obj, dict):
            return [self.property_of(node, k) for k in sorted(obj.keys())]
        else:
            return []

    def code_at_regex_sub(self, match):
        return match.group(1) + ( '@' if match.group(2) else self.TEMP_CURR_VAR )

    def code_dollar_regex_sub(self, match):
        return match.group(1) + ( '$' if match.group(2) else self.TEMP_ROOT_VAR )

    def eval_code_for(self, data, node):
        obj, path = node
        # replace non-escaped @ symbols with variable and escaped with plain symbol.
        # Capture all preceeding backslashes to resolve multiply-escaped symbol.        
        to_eval = re.sub(r'(?<!\\)((?:\\\\)*)(\\?)@', self.code_at_regex_sub, self.code)
        # same for root ($) symbols
        to_eval = re.sub(r'(?<!\\)((?:\\\\)*)(\\?)\$', self.code_dollar_regex_sub, to_eval)
        return eval(to_eval, { self.TEMP_CURR_VAR: obj, self.TEMP_ROOT_VAR: data })

    def replace_values_if_tokens_empty(self, tokens, values, **newvalues):
        if tokens is not None and len(list(tokens.items())) == 0:
            tokens = None
            values = newvalues
        return tokens, values


class PChild(_Parsed): 

    def apply_to(self, data, currnodes):
        retval = []
        for targ in self.targets:
            retval.extend(targ.apply_to(data, currnodes))
        return retval

        
class PRecursive(_Parsed):

    def apply_to(self, data, currnodes):
        retval = []
        for targ in self.targets:
            retval.extend(targ.apply_to(data, currnodes))
        # recurse down
        for node in currnodes:
            retval.extend(self.apply_to(data, self.all_children_of(node)))
        return retval
        
                    
class PRoot(_Parsed):

    def apply_to(self, data, currnodes):
        return [ (data, '$') ]


class PCurrent(_Parsed):

    def apply_to(self, data, currnodes):
        return list(currnodes)


class PWildcard(_Parsed):

    def apply_to(self, data, currnodes):
        retval = []
        for node in currnodes:            
            retval.extend(self.all_children_of(node))
        return retval
                

class PProperty(_Parsed):

    def apply_to(self, data, currnodes):
        retval = []
        for node in currnodes:
            obj, path = node
            if not isinstance(obj, dict): 
                logging.debug('ignoring property "{}" for {}'.format(self.name, type(obj).__name__))
                continue
            try:
                retval.append(self.property_of(node, self.name))
            except KeyError as e:
                logging.debug('{} {}'.format(type(e).__name__, str(e)))
        return retval
        

class PSlice(_Parsed):

    def apply_to(self, data, currnodes):
        retval = []
        for node in currnodes:
            obj, path = node
            if not isinstance(obj, (list, tuple)): 
                logging.debug('ignoring slice "{}" for {}'.format(self._values, type(obj).__name__))
                continue
            if hasattr(self, "index"):
                try:
                    retval.append(self.index_of(node, self.index))
                except IndexError as e:
                    logging.debug('{} {}'.format(type(e).__name__, str(e)))
            else:
                start = getattr(self, "start", None)
                end = getattr(self, "end", None)
                step = getattr(self, "step", None)
                for i,v in list(enumerate(obj))[start:end:step]:
                    retval.append(self.index_of(node, i))
        return retval
        
    
class PExpression(_Parsed):

    def __init__(self, tokens=None, **values):
        # hack to insert empty code property if parser doesn't provide one
        tokens, values = self.replace_values_if_tokens_empty(tokens, values, code='')
        super().__init__(tokens, **values)

    def apply_to(self, data, currnodes):        
        retval = []
        for node in currnodes:
            obj, path = node
            try:
                key = self.eval_code_for(data, node)
            except SyntaxError:
                raise
            except Exception as e:
                logging.warning('{} evaluating python expression script \"{}\": {}'
                                .format(type(e).__name__, self.code, e))
                continue
            if isinstance(obj, (list, tuple)) and isinstance(key, (int, float)) and not isinstance(key, bool):
                try:
                    retval.append(self.index_of(node, int(key)))
                except IndexError as e:
                    logging.debug('{} {}'.format(type(e).__name__, str(e)))
            elif isinstance(obj, dict) and isinstance(key, str):
                try:
                    retval.append(self.property_of(node, str(key)))
                except KeyError as e:
                    logging.debug('{} {}'.format(type(e).__name__, str(e)))
            else:
                logging.debug('ignoring key/index {} for {}'.format(repr(key),type(obj).__name__))
        return retval

    
class PFilter(_Parsed):

    def __init__(self, tokens=None, **values):
        # hack to insert empty code property if parser doesn't provide one
        tokens, values = self.replace_values_if_tokens_empty(tokens, values, code='')
        super().__init__(tokens, **values)

    def apply_to(self, data, currnodes):
        retval = []
        for node in currnodes:
            for child in self.all_children_of(node):
                try:
                    if not bool(self.eval_code_for(data, child)):
                        continue
                except SyntaxError:
                    raise
                except Exception as e:
                    logging.warning("{} evaluating python filter script \"{}\": {}"
                                    .format(type(e).__name__, self.code, e))
                    continue
                retval.append(child)
        return retval


def _token_printer(name):
    def print_tokens(tokens):
        print('{} - {}, keys: {}'.format(name, tokens, ','.join('{}={}'.format(k,v) for k,v in tokens.items())))
    return print_tokens


_ROOT = pp.Literal('$') \
                .setParseAction(PRoot)

_CURRENT = pp.Literal('@') \
                .setParseAction(PCurrent)

_WILDCARD = pp.Literal('*') \
                .setParseAction(PWildcard)

_NAME = pp.Word( pp.alphas+"_", pp.alphanums+"_" ) \
                .setName('name')

_PROPERTY = ( _NAME 
                    | pp.QuotedString('"','\\',None,False,True)
                    | pp.QuotedString("'",'\\',None,False,True) ) \
                .setResultsName('name').setParseAction(PProperty).setName('property')

_INTEGER = pp.Combine( pp.Literal("-")*(0,1) + pp.Word( pp.nums ) ) \
                .setParseAction(lambda t: int(t[0])).setName('integer')

_SLICE = ( _INTEGER.setResultsName('start')*(0,1) 
                + ':' + _INTEGER.setResultsName('end')*(0,1)
                + ( pp.Literal(':') + _INTEGER.setResultsName('step')*(0,1) )*(0,1)
            | _INTEGER.setResultsName('index') ) \
                .setParseAction(PSlice).setName('slice')

_EXPRESSION = pp.QuotedString('(','\\',None,False,True,')') \
                .setResultsName('code').setParseAction(PExpression).setName('script expression')

_FILTER = pp.QuotedString('?(','\\',None,False,True,')') \
                .setResultsName('code').setParseAction(PFilter).setName('script filter')

_TARGET = ( _ROOT | _CURRENT | _WILDCARD | _PROPERTY | _SLICE | _EXPRESSION | _FILTER ) \
                .setName('target')

_TARGET_SET = pp.Group(pp.delimitedList( _TARGET, ',' )) \
                .setName('target set')

_IMPLICIT_CHILD = _TARGET_SET \
                .setResultsName('targets').setParseAction(PChild)

_CHILD = ( pp.Literal(".") + _TARGET_SET.setResultsName('targets') 
            | pp.Literal('[') + _TARGET_SET.setResultsName('targets') + ']' ) \
                .setParseAction(PChild).setName('child step')

_RECURSIVE = ( pp.Literal("..") + _TARGET_SET.setResultsName('targets') ) \
                .setParseAction(PRecursive).setName('recurse step')

_STEP = _CHILD | _RECURSIVE

_PATH = ( ( _IMPLICIT_CHILD | _STEP ) + _STEP*(0,) ) \
                .setName('path')


RESULT_TYPE_VALUE = "VALUE"
RESULT_TYPE_PATH = "PATH"
RESULT_TYPE_BOTH = "BOTH"


def parse(string):
    """Returns the parse tree from a string representing a JSONPath expression

    :param string: The JSONPath expression to parse
    :type string: str
    :return: Nested objects representing the JSONPath (root will be a list)
    :rtype: list
    :raises JsonPathSyntaxError: if the given string does not represent a valid JSONPath 
        expression. Note that Python script expressions are not parsed until the path is 
        evaluated.
    """
    try:
        return _PATH.parseString(string, True)
    except pp.ParseException as e:
        raise JsonPathSyntaxError(e.line, e.col, e.msg) from e


def evaluate(data, steps):
    """Applies a JSONPath representation to a data structure and returns the matching nodes

    :param data: The data structure of basic types to query, as returned by the `json` module
    :type data: bool, int, float, str, tuple, list, dict, None
    :param steps: The JSONPath representation, as returned by the `parse` function
    :type steps: list
    :return: List of 2-tuples, each containing the value followed by the path.
    :rtype: list
    :raises PythonSyntaxError: if the JSONPath includes an invalid Python script expression
    """
    currnodes = [(data,'$')]
    try:
        for step in steps:
            currnodes = step.apply_to(data, currnodes)
        return currnodes
    except SyntaxError as e:
        raise PythonSyntaxError(e.text, e.offset, e.msg) from e    


def jsonpath(obj, expr, result_type=RESULT_TYPE_VALUE, always_return_list=False):
    """Queries the given data structure using a JSONPath expression as a string.

    This is a convenience function that first `parse`es the expression string and then
    `evaluate`s the expression against the given data structure.

    :param obj: The data structure of basic types to query, as returned by the `json` module
    :type obj: bool, int, float, str, tuple, list, dict, None
    :param expr: A JSONPath expression to evaluate
    :type expr: str
    :param result_type: The type of data to return: `RESULT_TYPE_VALUE`, `RESULT_TYPE_PATH` or 
        `RESULT_TYPE_BOTH`. Returns values by default.
    :type result_type: str
    :param always_return_list: The JSONPath reference implementation returns the value ``false``
        in the case of no matching results, and this is the default behaviour. However an empty
        list (perhaps a more Pythonic alternative) can be returned instead by setting this 
        parameter `True`.
    :type always_return_list: bool
    :return: List of results. For values (the default) or paths, each result will be a string.
        If both are requested, each result will be a 2-tuple containing the value followed by
        the path.
    :rtype: list
    :raises ParseError: if the given string does not represent a valid JSONPath or contains
        an invalid Python script expression 
    :example:

    >>> from jsonpyth import jsonpath
    >>> data = {
    ...     "dogs": [
    ...         { "name": "Fido", "age": 6 },
    ...         { "name": "Gruff", "age": 8 }
    ...     ],
    ...     "cats": [
    ...         { "name": "Alfie", "age": 3 },
    ...         { "name": "Bubbles", "age": 5 },
    ...     ]
    ... }
    >>> jsonpath(data, "$.cats[*].name")
    ['Alfie', 'Bubbles']
    """
    result = evaluate(obj, parse(expr))
    
    if len(result) == 0 and not always_return_list:
        return False
    elif result_type == RESULT_TYPE_VALUE:
        return [val for val,path in result]
    elif result_type == RESULT_TYPE_PATH:
        return [path for val,path in result]
    else:
        return result

