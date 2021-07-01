Rillgen2D is written in `C`

The code is compiled by the Python script when the program is run.

To compile the `C` code outside of python, you can use `gcc` in Linux or Mac OS X

```
gcc -Wall -shared -fPIC rillgen2d.c -o rillgen2d.so
```

To compile the `C` code outside of Python on Windows 10:

```
gcc -o rillgen2d.exe rillgen2d.c
```
