

#ifndef BLOCK_TEMPLATE_H
#define BLOCK_TEMPLATE_H

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#ifdef _HAVE_STDC_HEADERS
#include <string.h>
#endif

#include <Python.h>
#include <structmember.h>
#include "modsupport.h"
#include "_counter.h"

#define TRUE	1
#define FALSE	0

/* Cipher operation modes */
#define MODE_ECB 1
#define MODE_CBC 2
#define MODE_CFB 3
#define MODE_PGP 4
#define MODE_OFB 5
#define MODE_CTR 6

#define _STR(x) #x
#define _XSTR(x) _STR(x)
#define _PASTE(x,y) x##y
#define _PASTE2(x,y) _PASTE(x,y)
#define _MODULE_STRING _XSTR(MODULE_NAME)

#if PY_MAJOR_VERSION >= 3
#define _MODULE_NAME _PASTE2(PyInit_, MODULE_NAME)
#else
#define _MODULE_NAME _PASTE2(init,MODULE_NAME)
#endif

typedef struct
{
	PyObject_HEAD
	int mode, count, segment_size, prf_mode;
	unsigned char IV[BLOCK_SIZE], oldCipher[BLOCK_SIZE];
	PyObject *counter;
	int counter_shortcut;
	block_state st;
} ALGobject;

// staticforward PyTypeObject ALGtype;
static PyTypeObject ALGtype;

#define is_ALGobject(v)		((v)->ob_type == &ALGtype)

PyMemberDef ALGmembers[];
PyMethodDef ALGmethods[];

#endif
