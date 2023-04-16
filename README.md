The idea is to go from a traceback to a nice context of the traceback.
For example, traceback in `buggy_script.py` is 

```
  File "buggy_script.py", line 26, in calculate
    return res
NameError: name 'res' is not defined
```

Feed `buggy_script.py` and `'calculate'` to minimal extractor, and it should return the source code that is required to run `calculate` in `buggy_script.py`.

```python3
import sys
import fire

def add_numbers(a, b):
    return a + b

def multiply_numbers(a, b):
    return a * b

def divide_numbers(a, b):
    return a / b


def calculate(operation, num1, num2):
    if operation == "add":
        result = add_numbers(num1, num2)
    elif operation == "subtract":
        result = subtract_numbers(num1, num2)
    elif operation == "multiply":
        result = multiply_numbers(num1, num2)
    elif operation == "divide":
        result = divide_numbers(num1, num2)
    else:
        print("Invalid operation")

    return res


if __name__ == "__main__":
    fire.Fire(calculate)

```

returns

```python3
import fire

def add_numbers(a, b):
    return a + b

def divide_numbers(a, b):
    return a / b

def multiply_numbers(a, b):
    return a * b

def calculate(operation, num1, num2):
    if operation == 'add':
        result = add_numbers(num1, num2)
    elif operation == 'subtract':
        result = subtract_numbers(num1, num2)
    elif operation == 'multiply':
        result = multiply_numbers(num1, num2)
    elif operation == 'divide':
        result = divide_numbers(num1, num2)
    else:
        print('Invalid operation')
    return res
```
