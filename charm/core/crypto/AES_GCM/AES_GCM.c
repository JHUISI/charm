/**
 * AES_GCM.c - Native AES-GCM (Galois/Counter Mode) using OpenSSL EVP API
 *
 * Provides authenticated encryption with associated data (AEAD) via
 * AES-GCM, without requiring the Python 'cryptography' package.
 *
 * Module functions:
 *   encrypt(key, plaintext, nonce, aad) -> ciphertext_and_tag
 *   decrypt(key, ciphertext_and_tag, nonce, aad) -> plaintext
 *
 * This module is part of the charm-crypto framework.
 */

#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif

#include <Python.h>
#include <openssl/evp.h>
#include <openssl/err.h>

#define AES_GCM_TAG_SIZE 16
#define AES_GCM_NONCE_SIZE 12

static PyObject *AESGCMError;

/**
 * encrypt(key, plaintext, nonce, aad=b'') -> bytes
 *
 * Encrypts plaintext with AES-GCM. Returns ciphertext || tag (16 bytes).
 */
static PyObject *
AESGCM_encrypt(PyObject *self, PyObject *args, PyObject *kwdict)
{
    const unsigned char *key, *plaintext, *nonce, *aad = NULL;
    Py_ssize_t key_len, pt_len, nonce_len, aad_len = 0;
    static char *kwlist[] = {"key", "plaintext", "nonce", "aad", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "y#y#y#|y#", kwlist,
            &key, &key_len, &plaintext, &pt_len,
            &nonce, &nonce_len, &aad, &aad_len))
        return NULL;

    /* Validate key length */
    if (key_len != 16 && key_len != 24 && key_len != 32) {
        PyErr_SetString(PyExc_ValueError,
            "AES-GCM key must be 16, 24, or 32 bytes");
        return NULL;
    }

    /* Select cipher based on key length */
    const EVP_CIPHER *cipher;
    switch (key_len) {
        case 16: cipher = EVP_aes_128_gcm(); break;
        case 24: cipher = EVP_aes_192_gcm(); break;
        case 32: cipher = EVP_aes_256_gcm(); break;
        default: return NULL; /* unreachable */
    }

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        PyErr_SetString(AESGCMError, "Failed to create cipher context");
        return NULL;
    }

    PyObject *result = NULL;
    unsigned char *outbuf = NULL;
    int outlen = 0, tmplen = 0;

    /* Allocate output: ciphertext + tag */
    outbuf = (unsigned char *)PyMem_Malloc(pt_len + AES_GCM_TAG_SIZE);
    if (!outbuf) {
        PyErr_NoMemory();
        goto cleanup;
    }

    if (EVP_EncryptInit_ex(ctx, cipher, NULL, NULL, NULL) != 1)
        goto openssl_err;

    /* Set nonce length (must be before setting key+nonce) */
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, (int)nonce_len, NULL) != 1)
        goto openssl_err;

    if (EVP_EncryptInit_ex(ctx, NULL, NULL, key, nonce) != 1)
        goto openssl_err;

    /* Process AAD if provided */
    if (aad && aad_len > 0) {
        if (EVP_EncryptUpdate(ctx, NULL, &tmplen, aad, (int)aad_len) != 1)
            goto openssl_err;
    }

    /* Encrypt plaintext */
    if (EVP_EncryptUpdate(ctx, outbuf, &outlen, plaintext, (int)pt_len) != 1)
        goto openssl_err;

    if (EVP_EncryptFinal_ex(ctx, outbuf + outlen, &tmplen) != 1)
        goto openssl_err;
    outlen += tmplen;

    /* Get the authentication tag */
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, AES_GCM_TAG_SIZE,
                            outbuf + outlen) != 1)
        goto openssl_err;

    result = PyBytes_FromStringAndSize((char *)outbuf, outlen + AES_GCM_TAG_SIZE);
    goto cleanup;

openssl_err:
    PyErr_SetString(AESGCMError, "OpenSSL AES-GCM encryption failed");

cleanup:
    if (outbuf) PyMem_Free(outbuf);
    EVP_CIPHER_CTX_free(ctx);
    return result;
}

/**
 * decrypt(key, ciphertext_and_tag, nonce, aad=b'') -> bytes
 *
 * Decrypts and authenticates AES-GCM ciphertext.
 * The last 16 bytes of ciphertext_and_tag are the authentication tag.
 * Raises AESGCMError if authentication fails.
 */
static PyObject *
AESGCM_decrypt(PyObject *self, PyObject *args, PyObject *kwdict)
{
    const unsigned char *key, *ct_and_tag, *nonce, *aad = NULL;
    Py_ssize_t key_len, ct_tag_len, nonce_len, aad_len = 0;
    static char *kwlist[] = {"key", "ciphertext", "nonce", "aad", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "y#y#y#|y#", kwlist,
            &key, &key_len, &ct_and_tag, &ct_tag_len,
            &nonce, &nonce_len, &aad, &aad_len))
        return NULL;

    if (key_len != 16 && key_len != 24 && key_len != 32) {
        PyErr_SetString(PyExc_ValueError,
            "AES-GCM key must be 16, 24, or 32 bytes");
        return NULL;
    }

    if (ct_tag_len < AES_GCM_TAG_SIZE) {
        PyErr_SetString(PyExc_ValueError,
            "Ciphertext too short — must include 16-byte authentication tag");
        return NULL;
    }


    Py_ssize_t ct_len = ct_tag_len - AES_GCM_TAG_SIZE;
    const unsigned char *tag = ct_and_tag + ct_len;

    const EVP_CIPHER *cipher;
    switch (key_len) {
        case 16: cipher = EVP_aes_128_gcm(); break;
        case 24: cipher = EVP_aes_192_gcm(); break;
        case 32: cipher = EVP_aes_256_gcm(); break;
        default: return NULL;
    }

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        PyErr_SetString(AESGCMError, "Failed to create cipher context");
        return NULL;
    }

    PyObject *result = NULL;
    unsigned char *outbuf = NULL;
    int outlen = 0, tmplen = 0;

    outbuf = (unsigned char *)PyMem_Malloc(ct_len > 0 ? ct_len : 1);
    if (!outbuf) {
        PyErr_NoMemory();
        goto cleanup;
    }

    if (EVP_DecryptInit_ex(ctx, cipher, NULL, NULL, NULL) != 1)
        goto openssl_err;

    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, (int)nonce_len, NULL) != 1)
        goto openssl_err;

    if (EVP_DecryptInit_ex(ctx, NULL, NULL, key, nonce) != 1)
        goto openssl_err;

    /* Process AAD */
    if (aad && aad_len > 0) {
        if (EVP_DecryptUpdate(ctx, NULL, &tmplen, aad, (int)aad_len) != 1)
            goto openssl_err;
    }

    /* Decrypt ciphertext */
    if (ct_len > 0) {
        if (EVP_DecryptUpdate(ctx, outbuf, &outlen, ct_and_tag, (int)ct_len) != 1)
            goto openssl_err;
    }

    /* Set the expected tag */
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, AES_GCM_TAG_SIZE,
                            (void *)tag) != 1)
        goto openssl_err;

    /* Finalize — this verifies the tag */
    if (EVP_DecryptFinal_ex(ctx, outbuf + outlen, &tmplen) != 1) {
        PyErr_SetString(AESGCMError,
            "Decryption failed: authentication tag is invalid "
            "(data tampered or wrong key)");
        goto cleanup;
    }
    outlen += tmplen;

    result = PyBytes_FromStringAndSize((char *)outbuf, outlen);
    goto cleanup;

openssl_err:
    PyErr_SetString(AESGCMError, "OpenSSL AES-GCM decryption failed");

cleanup:
    if (outbuf) PyMem_Free(outbuf);
    EVP_CIPHER_CTX_free(ctx);
    return result;
}

/* Module method table */
static PyMethodDef AESGCM_methods[] = {
    {"encrypt", (PyCFunction)AESGCM_encrypt, METH_VARARGS | METH_KEYWORDS,
     "encrypt(key, plaintext, nonce, aad=b'') -> ciphertext_and_tag\n\n"
     "Encrypt with AES-GCM. Returns ciphertext || 16-byte auth tag."},
    {"decrypt", (PyCFunction)AESGCM_decrypt, METH_VARARGS | METH_KEYWORDS,
     "decrypt(key, ciphertext_and_tag, nonce, aad=b'') -> plaintext\n\n"
     "Decrypt and authenticate AES-GCM ciphertext."},
    {NULL, NULL, 0, NULL}
};

/* Module definition */
static struct PyModuleDef aesgcm_module = {
    PyModuleDef_HEAD_INIT,
    "AES_GCM",
    "Native AES-GCM authenticated encryption using OpenSSL EVP API.\n\n"
    "Provides encrypt() and decrypt() functions for AES-GCM AEAD.\n"
    "Supports AES-128, AES-192, and AES-256 key sizes.",
    -1,
    AESGCM_methods
};

PyMODINIT_FUNC
PyInit_AES_GCM(void)
{
    PyObject *m = PyModule_Create(&aesgcm_module);
    if (m == NULL)
        return NULL;

    AESGCMError = PyErr_NewException("AES_GCM.Error", NULL, NULL);
    if (AESGCMError == NULL) {
        Py_DECREF(m);
        return NULL;
    }
    Py_INCREF(AESGCMError);
    PyModule_AddObject(m, "Error", AESGCMError);

    /* Export constants */
    PyModule_AddIntConstant(m, "TAG_SIZE", AES_GCM_TAG_SIZE);
    PyModule_AddIntConstant(m, "NONCE_SIZE", AES_GCM_NONCE_SIZE);

    return m;
}