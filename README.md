# JSONPyth #

[![Build Status](https://travis-ci.com/Frimkron/JSONPyth.svg?branch=master)](
    https://travis-ci.com/Frimkron/JSONPyth)

Another [JSONPath] implementation for Python.

Supports:

* Root `$` and current `@` node
* Child operator `.` or `[` ... `]`
* Property access (including single quote `'` and double `"` quote delimited 
  names)
* Recursive descent `..`
* Wildcard `*`
* Sets of names/indices `[a,b,c]`
* Array slice `[start:end:step]` (including negative values)
* Python script expression `(` ... `)` and filter expression `?(` ... `)` using 
  `$` and `@`


## Requirements

Requires Python 3.5+ and depends on the [PyParsing] package.


## Installation ##

JSONPyth can be git-cloned directly from Github and installed along with its 
dependencies using `pip`:

    $ pip install git+https://github.com/Frimkron/JSONPyth#egg=JSONPyth

Or the source can be downloaded manually and then installed by running the 
`setup.py` script:

    $ python setup.py install
    

## Usage ##

First parse some JSON data into a Python structure, for example using the [json]
package from the standard library:

``` python

import json

# parse some JSON from a string
data = json.loads("""
    {
        "cakes": [
            { "name": "red velvet", "rating": 4.5 },
            { "name": "battenberg" },
            { "name": "jaffa cakes", "rating": 5.0 }
        ],
        "biscuits": [
            { "name": "bourbon", "rating": 5.0 },
            { "name": "custard cream", "rating": 3.5 },
            { "name": "pink wafer", "rating": null },
            { "name": "nice" }
        ]
    }
""")

```

Then the data can be queried with a JSONPath expression:

``` python

from jsonpyth import jsonpath

result = jsonpath(data, '$.biscuits[*].rating')

for r in result:
    print(r)
    
```

The example above would print the following output:

``` 
5
3.5
None

```

### Returning Paths

By default the value of each result is returned. To obtain the normalised path
of each result instead, set the `result_type` parameter to `RESULT_TYPE_PATH`,
or `RESULT_TYPE_BOTH` can be used to return 2-tuples containing both the value
and the path:

``` python

from jsonpyth import jsonpath, RESULT_TYPE_BOTH

result = jsonpath(data, '$.biscuits[*].rating', result_type=RESULT_TYPE_BOTH):

for r in result:
    print(r)

```

Output:

``` 
(5, '$["biscuits"][0]["rating"]')
(3.5, '$["biscuits"][1]["rating"]')
(None, '$["biscuits"][2]["rating"]')
```

### Python Expressions

A JSONPath _script expression_ (enclosed in parentheses `(...)` ) can be used to
evaluate a Python statement to provide a dictionary key as a string, or list 
index as a number. Return values of other types will be ignored.

As parentheses are used to delimit the expression, parentheses used in the 
script itself must be escaped with a backslash `\`.

The special symbols `@` (current node) and `$` (root node) will be substituted 
for variables named `__current` and `__root` respectively, using a simple text 
replacement before the statement is evaluated. To use a literal `@` or `$` in
the script, it must be escaped with _two_ backslashes `\\`. Note that a string 
literal will recognise `\\` as an escaped backslash; in such a case each 
backslash must be further escaped (`"\\\\@"`) or else a raw literal used 
(`r"\\@"`).

An example script expression:

``` python

result = jsonpath(data, r'$.cakes[(len\(@\)-1)].name')

for r in result:
    print(r)
```

Output:

``` 
jaffa cakes
```

**NOTE** JSONPyth calls `eval` to evaluate Python script, and so is **unsafe**
to use for JSONPath expressions from untrusted sources.


### Python Filters

Similar to expressions, filters ( `?(...)` ) use a Python statement to test 
whether to include a node or not. The truthiness of the resulting value will be
tested using `bool`, and if `False` the node will be omitted.

Example:

``` python

result = jsonpath(data, r'$[*][?(@["name"].startswith\("b"\))]')

for r in result:
    print(r)
```

Output:

``` 
{"name": "battenberg"}
{"name": "bourbon", "rating": 5}
```


# Credits and Licence

[JSONPyth] was written by Mark Frimston and is licenced using the the MIT 
licence. The full text of this licence can be found in the `LICENCE.txt` file.


[JSONPath]: http://goessner.net/articles/JsonPath/
[PyParsing]: https://github.com/pyparsing/pyparsing
[json]: https://docs.python.org/3/library/json.html
[JSONPyth]: https://github.com/Frimkron/JSONPyth
