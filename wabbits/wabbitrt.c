/* wabbitsrt.c

   This file contains runtime support functions for the Wabbit language. 
   Compile using the supplied Makefile.
*/

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#ifdef WINDOWS
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

EXPORT
void _print_int(int x) {
  printf("%i\n", x);
}

EXPORT
void _print_float(double x) {
  printf("%f\n", x);
}

EXPORT
void _print_byte(int ch) {
  printf("%c", (char) ch);
  fflush(stdout);
}

// The Wabbit memory system
static unsigned char *memory = 0;
static uint32_t memsize = 0;

EXPORT
uint32_t _grow(uint32_t incr) {
  if (incr == 0) {
    return memsize;
  }
  memsize += incr;
  if (!memory) {
    memory = (unsigned char *) malloc(memsize);
  } else {
    memory = (unsigned char *) realloc(memory, memsize);
  }
  return memsize;
}

EXPORT
int32_t _peeki(uint32_t addr) {
  int32_t val;
  memmove(&val, memory+addr, 4);
  return val;
}

EXPORT
double _peekf(uint32_t addr) {
  double val;
  memmove(&val, memory+addr, 8);
  return val;
}

EXPORT
int32_t _peekb(uint32_t addr) {
  return (int32_t) memory[addr];
}

EXPORT
void _pokei(uint32_t addr, int32_t value) {
  memmove(memory+addr, &value, 4);
}

EXPORT
void _pokef(uint32_t addr, double value) {
  memmove(memory+addr, &value, 8);
}

EXPORT
void _pokeb(uint32_t addr, int32_t value) {
  memory[addr] = (unsigned char) value;
}


