# Slex

Is an language thats compile into c++.

Common file extension `.slx`

---
### Data Types
| Slex Type |       C++ Type         |  Size  |
|:---------:|:----------------------:|:------:|
|   bool    |          bool          |  8bits |
|     i8    |          char          |  8bits |
|    i16    |          short         | 16bits |
|    i32    |           int          | 32bits |
|    i64    |      long long int     | 64bits |
|     u8    |      unsigned char     |  8bits |
|    u16    |     unsigned short     | 16bits |
|    u32    |      unsigned int      | 32bits |
|    u64    | unsigned long long int | 64bits |
|    f32    |          float         | 32bits |
|    f64    |         double         | 64bits |

The pointers are defined by '*' after data type
```python
i32* ptr # this is i32 pointer
```
the references use `ref` keyword
```python
i32 b = 10
ref i32 a = b # a is reference of b
```

---
### Commentaries
Use `#` for one line commentaries
```python
# This is a commentary
```

---
### Variables

You can define one variable with its data type and then set the value
```python
i32 var_a
var_a = 10
i32 var_b = 10 # the same in one line
```
or define the value and the type using `:=`, with this the data type is automaticlly detected (currently not work)
```python
var_a := 10 # var_a is i32
var_b := "Hello, World!" # var_b is i8*
```
the variables assignation after declaration is like others languages
```python
var_a = 1
var_b = "reassignation"
```

---
### Functions

For functions definitions, start using `def` then the function name, parameters list and after colons define the return data type.

```python
def main(i32 a, i8* b): i32
    return 0
```

the templates are defined with `<>` after the function name and have the list of typenames to use for the template

```python
def explicit_template<T>(): T
    T* a = new T
    return a

i32 var_a = explicit_template<i32>()

def implicit_template<T>(T a): T
    return a
    
i32 var_b = implicit_template(10)

def impicit_and_explicit<T, A>(A arg): T
    return (T) arg

i32 var_c = impicit_and_explicit<i32>(2.0)

```

---
### Classes

The class are defined with, `class` keyword then the name, `<>` template typenames and extends with `()`, the last two are not obligatory

```python
class Base:
    i32 prop_1

# This class is derived from Base
class Derived(Base):
    i32 prop_2

# Simple template
class List<T>:
    T* data
```

the methods are defined like functions
with `@static` before method define it as static

```python
class MyClass:
    @static
    def this_is_static_method():
        return
```

`@virtual` for create virtual method, is obligatory override this methods in inherited classes

```python
class Virtual:
    @virtual
    def overrid_me(): i32

class Derived(Vitual):
    def overrid_me(): i32
        return 0
```

### Start [WIP]

```python
class Int:
    i32 value
    
    def Int(i32 a): # constructor
        self.value = a
    
    @operator
    def +(i32 a): Int
        return Int(self.value + a)
    
    @operator
    def -(i32 a): Int
        return Int(self.value - a)

class GetterClass:
    i32 get_count = 0
    i32 set_count = 0
    
    i32* prop_a
    
    @getter
    def prop_a(): i32 # getter
        self.get_count += 1
        return self.prop_a
       
    @setter
    def prop_a(i32* val): # setter
        self.set_count += 1
        self.prop_a = val
    
GetterClass* gc = new GetterClass()
gc.prop_a = 10 # call prop_a setter
i32* c = gc.prop_a # call prop_a getter

```

### End [WIP]

for allocate memory use `new` before class name and constructor parameters, this return object pointer

```python
Base* obj = new Base()

# for free the memory use del
del obj

# can allocate memory of all datatypes
i32* _int_ = new i32
del _int_ # but remember free the memory
```

---
### Flow control structures

The flow control structure are generally like python

```python
if condition:
    #code...
    
elif condition:
    #code...
    
else:
    #code...

while condition:
    #code...

for element in array:
    #code...
```

except the `for` in case of numbers range and the `switch`

```python
# for range
for i in 0 to 10:
    #code...

switch n:
    case 1:
        #code...
    
    case 2:
        #code...
    
    default:
        #code...
```

---
### Enum

For enumerators use `enum` keyword
```python
enum Name:
    TYPE_A     # 1
    TYPE_B     # 2
    TYPE_C = 4 # 4
    TYPE_D     # 5
```
