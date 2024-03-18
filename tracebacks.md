# Traceback Challenges
See the "Python Stack Traces" attachment which lists several python stack traces. 
Your task is to examine the stack traces and provide a brief response for each 
one that summarizes what the problem or likely problem is, and the first line of 
code you would jump to in your code editor given the trace.

## What this program does
This program does a variety of math operations given an input function
name and two other args for x and y representing dicts, ints, etc.

Below is a similar implementation with improved functions (except for spelunk() as did 
not yet think of better way to handle.)
```python
#somewhat similar implementation - improved functions below
import functools


def calc_decorator(function):
    print(function)
    def calc(*args, **kwargs):
        print(args)
        function = args[0]
        restofargs = args[1:]
        print("Calling %s with:" % function.__name__, args[1:], kwargs)
        return function(*args[1:], **kwargs)
    return calc


@calc_decorator
def perform_calculation(*args, **kwargs):
    print("doing calc...")

    
def old_add(x, y):
    return x+y


def add(x, y):
    if isinstance(x, int) is False or isinstance(y, int) is False:
        raise ValueError("one of the inputs is not an int")
    return x+y


def old_mult(x, y):
    return x*y


def mult(x, y):
    if isinstance(x, int) is False or isinstance(y, int) is False:
        raise ValueError("one of the inputs is not an int")
    return x*y


def comp_calc(x, y, function):
    return [perform_calculation(function, x_i, y_i) for x_i, y_i in zip(x, y)]


def calc_dict(dict_obj, key_1, key_2, function):
    return perform_calculation(function, dict_obj[key_1], dict_obj[key_2])


def better_comp_calc(x, y, function):
    if isinstance(x, list) is False or isinstance(y, list) is False:
        raise ValueError("one of the inputs is not a list")
    if all(isinstance(xl, int) for xl in x) is False or all(isinstance(yl, int) for yl in y) is False:
        raise ValueError("a value in one or both of the input lists is not an int")
    if len(x) == len(y):
        # if we care about the lists to zip being same size
        return [perform_calculation(function, x_i, y_i) for x_i, y_i in zip(x, y)]
    else:
        raise ValueError("lists not same size")


def better_calc_dict(dict_obj, key_1, key_2, function):
    if dict_obj:
        if key_1 in dict_obj.keys() and key_2 in dict_obj.keys():
            if isinstance(dict_obj[key_1], int) is False or isinstance(dict_obj[key_2], int) is False:
                raise ValueError("one or both of the values for the keys is not an int")
            return perform_calculation(function, dict_obj[key_1], dict_obj[key_2])
        else:
            raise KeyError("missing one or both keys")
    else:
        raise ValueError("input dict is empty")


#traceback 1
perform_calculation(add, 5, 3)

#traceback 2
perform_calculation(mult, 5, 3)

#traceback 3
#perform_calculation(mult, '3', '3')

#traceback 4
perform_calculation(mult, [4], [3])

#traceback 5
#perform_calculation(innoc, [4], [3])

# traceback 6
#comp_calc([1, 2, 3], 1, add)
better_comp_calc([1, 2, 3], 1, add)

# traceback 7
#comp_calc([1, 2, [3]], [4, 5, 6], add)
better_comp_calc([1, 2, [3]], [4, 5, 6], add)

# traceback 8
#calc_dict({'one': 1, 'two': '2'}, 'one', 'two', add)
better_calc_dict({'one': 1, 'two': '2'}, 'one', 'two', add)

#traceback 9
#calc_dict({}, 'one', 'two', add)
better_calc_dict({}, 'one', 'two', add)
```
## Problem 1 
### Traceback
```shell
Traceback (most recent call last):
  File "stack_traces.py", line 36, in run_trace
    f()
  File "stack_traces.py", line 45, in <lambda>
    run_trace(1, lambda: perform_calculation(add, '1', 3))
  File "stack_traces.py", line 8, in perform_calculation
    calc(x, y)
  File "stack_traces.py", line 12, in add
    return x + y
TypeError: can only concatenate str (not "int") to str
```
### Response
Int and strings can't be added - looks like a manual passing of a
string on line 45 in the lambda (i.e., the '1'). 
I'd start in the `run_trace` function.
In this case,
you could either check/coerce to `int('1')` or `isdigit` or use another number 
checking method, raise an error right away, or just don't pass a string.

**Note**: For all of these problems, one can either fix the input values (so the line number
would be the number listed for the inputs) *or* the methods.  I attempted
some fixes for the methods above in the code block.

## Problem 2
### Traceback
```shell
Traceback (most recent call last):
  File "stack_traces.py", line 36, in run_trace
    f()
  File "stack_traces.py", line 46, in <lambda>
    run_trace(2, lambda: perform_calculation(add, 7, '3'))
  File "stack_traces.py", line 8, in perform_calculation
    calc(x, y)
  File "stack_traces.py", line 12, in add
    return x + y
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```
### Response
Same as #1 above. Either way, need to revisit the perform_calculation lambda.

## Problem 3
### Traceback
```shell
Traceback (most recent call last):
  File "stack_traces.py", line 36, in run_trace
    f()
  File "stack_traces.py", line 47, in <lambda>
    run_trace(3, lambda: perform_calculation(mult, '3', '3'))
  File "stack_traces.py", line 8, in perform_calculation
    calc(x, y)
  File "stack_traces.py", line 15, in mult
    return x * y
TypeError: can't multiply sequence by non-int of type 'str'
```
### Response
In this case, much like #1 and #2, the values being passed into the calculations
need some additional type checking and/or conversion to a number. String and int work, but
string and string do not work for multiplication. 

## Problem 4
### Traceback
```shell
Traceback (most recent call last):
  File "stack_traces.py", line 36, in run_trace
    f()
  File "stack_traces.py", line 48, in <lambda>
    run_trace(4, lambda: perform_calculation(mult, [4], [3]))
  File "stack_traces.py", line 8, in perform_calculation
    calc(x, y)
  File "stack_traces.py", line 15, in mult
    return x * y
TypeError: can't multiply sequence by non-int of type 'list'
```
### Response
In this case, much like the above, lists can't be multiplied.

## Problem 5
### Traceback 
```shell
Traceback (most recent call last):
  File "stack_traces.py", line 36, in run_trace
    f()
  File "stack_traces.py", line 49, in <lambda>
    run_trace(5, lambda: perform_calculation(innoc, '1', 3))
  File "stack_traces.py", line 8, in perform_calculation
    calc(x, y)
  File "stack_traces.py", line 22, in innoc
    spelunk()
  File "stack_traces.py", line 21, in spelunk
    raise ValueError('Invalid')
ValueError: Invalid
```
### Response
My assumption here is that the spelunk method is attempting to find
a matching method. In this case, explicit error handling for unknown
values is raising a ValueError since this is an invalid/not found name/method.


## Problem 6
### Traceback
```shell
Traceback (most recent call last):
  File "stack_traces.py", line 36, in run_trace
    f()
  File "stack_traces.py", line 50, in <lambda>
    run_trace(6, lambda: comp_calc([1, 2, 3], 1, add))
  File "stack_traces.py", line 30, in comp_calc
    return [perform_calculation(calc, x_i, y_i) for x_i, y_i in zip(x, y)]
TypeError: zip argument #2 must support iteration
```
### Response
In this case, since the single int 1 is passed in as arg[1] and then passed into a zip,
the TypeError is raised because 1 is not iterable. If it were a list this would be possible.



## Problem 7
### Traceback
```shell
Traceback (most recent call last):
  File "stack_traces.py", line 36, in run_trace
    f()
  File "stack_traces.py", line 51, in <lambda>
    run_trace(7, lambda: comp_calc([1, 2, [3]], [4, 5, 6], add))
  File "stack_traces.py", line 30, in comp_calc
    return [perform_calculation(calc, x_i, y_i) for x_i, y_i in zip(x, y)]
  File "stack_traces.py", line 30, in <listcomp>
    return [perform_calculation(calc, x_i, y_i) for x_i, y_i in zip(x, y)]
  File "stack_traces.py", line 8, in perform_calculation
    calc(x, y)
  File "stack_traces.py", line 12, in add
    return x + y
TypeError: can only concatenate list (not "int") to list
```
### Response
This is problematic due to the [3] in the first list (nested list which is unexpected); 
comp_calc seems to be expecting x and y to be of the same type.


## Problem 8
### Traceback
```shell
Traceback (most recent call last):
  File "stack_traces.py", line 36, in run_trace
    f()
  File "stack_traces.py", line 52, in <lambda>
    run_trace(8, lambda: calc_dict({'one': 1, 'two': '2'}, 'one', 'two', add))
  File "stack_traces.py", line 26, in calc_dict
    return perform_calculation(calc, d[k1], d[k2])
  File "stack_traces.py", line 8, in perform_calculation
    calc(x, y)
  File "stack_traces.py", line 12, in add
    return x + y
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```
### Response
Much like the errors above, attempting to add the 1 and '2' (int and string) results in an error.
Type checking or string to number conversion could fix this.

## Problem 9
### Traceback
```shell
Traceback (most recent call last):
  File "stack_traces.py", line 36, in run_trace
    f()
  File "stack_traces.py", line 53, in <lambda>
    run_trace(9, lambda: calc_dict({}, 'one', 'two', add))
  File "stack_traces.py", line 26, in calc_dict
    return perform_calculation(calc, d[k1], d[k2])
KeyError: 'one'
```
### Response
The input dictionary is empty, so when attempting to get the value for key 'one' an
error is thrown as it does not exist. 
A better solution could be to use dict_obj.get(some_key, None/0) depending on
the desired outcome.


