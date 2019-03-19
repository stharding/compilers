# Makefile for creating a shared-library version of the Wabbit runtime.
# This is used if you're going to run Wabbit programs as a JIT. 
# See the file wabbit/run.py

osx::
	gcc -bundle -undefined dynamic_lookup wabbitrt.c -o wabbitrt.so

linux::
	gcc -shared -fPIC wabbitrt.c -o wabbitrt.so

# Prerequisite: cl.exe on path configured for x64, run "vcvarsall.bat x64".

win::
	cl /LD wabbitrt.c /link /out:wabbitrt.dll
