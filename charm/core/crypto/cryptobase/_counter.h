/*
 *  _counter.h: Fast counter for use with CTR-mode ciphers
 *
 * Written in 2008 by Dwayne C. Litzenberger <dlitz@dlitz.net>
 *
 * ===================================================================
 * The contents of this file are dedicated to the public domain.  To
 * the extent that dedication to the public domain is not available,
 * everyone is granted a worldwide, perpetual, royalty-free,
 * non-exclusive license to exercise all rights associated with the
 * contents of this file for any purpose whatsoever.
 * No rights are reserved.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 * ===================================================================
 */
#ifndef PCT__COUNTER_H
#define PCT__COUNTER_H

#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif

#include <stdint.h>
#include "Python.h"

/* Python 3.14+ compatibility - PyUnicode_GET_SIZE was removed */
#if PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION >= 14
#define PyUnicode_GET_SIZE(o) PyUnicode_GetLength(o)
#define PyUnicode_AS_STRING(o) PyUnicode_AsUTF8(o)
#endif

typedef struct {
    PyObject_HEAD
    PyObject *prefix;           /* Prefix bytes (useful for a nonce) */
    PyObject *suffix;           /* Suffix bytes (useful for a nonce) */
    uint8_t *val;               /* Buffer for our output string */
    uint32_t buf_size;          /* Size of the buffer */
    uint8_t *p;                 /* Pointer to the part of the buffer that we're allowed to update */
    uint16_t nbytes;            /* The number of bytes that from .p that are part of the counter */
    void (*inc_func)(void *);   /* Pointer to the counter increment function */
    int shortcut_disabled;      /* This gets set to a non-zero value when the shortcut mechanism is disabled */
    int carry;                  /* This gets set by Counter*Object_increment when the counter wraps around */
    int allow_wraparound;       /* When this is false, we raise OverflowError on next_value() or __call__() when the counter wraps around */
} PCT_CounterObject;

#endif /* PCT__COUNTER_H */
