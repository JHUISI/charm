/*
 * Charm-Crypto is a framework for rapidly prototyping cryptosystems.
 *
 * Charm-Crypto is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * Charm-Crypto is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with Charm-Crypto. If not, see <http://www.gnu.org/licenses/>.
 *
 * Please contact the charm-crypto dev team at support@charm-crypto.com
 * for any questions.
 */

/*
 *   @file    charm_embed_api.c
 *
 *   @brief   charm interface for C/C++ applications
 *
 *   @author  ayo.akinyele@charm-crypto.com
 *
 ************************************************************************/

#include "charm_embed_api.h"

int set_python_path(const char *path_to_mod)
{
    // set path
    PyObject *sys_path;
    PyObject *path;

    sys_path = PySys_GetObject("path");
    if (sys_path == NULL)
	return -1;
    path = PyUnicode_FromString(path_to_mod);
    if (path == NULL)
        return -1;
    if (PyList_Append(sys_path, path) < 0)
        return -1;

    return 0;
}

char *ltrim(char *s)
{
    while(isspace(*s)) s++;
    return s;
}

char *rtrim(char *s)
{
    char* back = s + strlen(s);
    while(isspace(*--back));
    *(back+1) = '\0';
    return s;
}

char *trim(char *s)
{
	if(s != NULL)
		return rtrim(ltrim(s));
	return NULL;
}

int InitializeCharm(void)
{
    Py_Initialize();

    char cwd[1024];
    memset(cwd, 0, 1024);
    if(getcwd(cwd, sizeof(cwd)) != NULL)
    	fprintf(stdout, "CWD: %s\n", cwd);
    else {
    	fprintf(stderr, "getcwd() error.\n");
    	return -1;
    }

    /* set the python path */
    set_python_path(cwd);

    return 0;
}

void CleanupCharm(void)
{
    Py_Finalize();
}

void CheckError(char *error_msg)
{
    if (PyErr_Occurred()) {
    	PyErr_Print();
    	fprintf(stderr, "%s\n", error_msg);
    }
}

result_t getType(PyObject *o)
{
	PyTypeObject *t = o->ob_type;
	//debug("Object type: '%s'\n", t->tp_name);

	if(strcmp(t->tp_name, INTEGER_TYPE) == 0)
		return INTEGER_T;
	else if(strcmp(t->tp_name, EC_TYPE) == 0)
		return EC_T;
	else if(strcmp(t->tp_name, PAIRING_TYPE) == 0)
		return PAIRING_T;
	else if(strcmp(t->tp_name, PYDICT_TYPE) == 0)
		return PYDICT_T;
	else if(strcmp(t->tp_name, PYTUPLE_TYPE) == 0)
		return PYTUPLE_T;
	else if(strcmp(t->tp_name, PYBYTES_TYPE) == 0)
		return PYBYTES_T;
	else if(strcmp(t->tp_name, PYINT_TYPE) == 0)
		return PYINT_T;
	else if(strcmp(t->tp_name, PYSTR_TYPE) == 0)
		return PYSTR_T;
	else if(strcmp(t->tp_name, PYNONE_TYPE) == 0)
		return NONE_T;
	else {
		printf("%s: unrecognized type.\n", __FUNCTION__);
		printf("%s: type => '%s'\n", __FUNCTION__, t->tp_name);
	}

	return NONE_T;
}

Charm_t *InitPairingGroup(Charm_t *pModule, const char *param_id)
{
	PyObject *pName, *pArgs, *pFunc, *pValue=NULL, *tmp;

	pName = PyUnicode_FromString("charm.toolbox.pairinggroup");

	if(pModule != NULL) PyObject_Del(pModule);
	pModule = PyImport_Import(pName);
	if(pModule != NULL)
		debug("import module ok: '%s'\n", pModule->ob_type->tp_name);
    Free(pName);

    if (pModule != NULL) {
        pFunc = PyObject_GetAttrString(pModule, "PairingGroup");
    	debug("got attr string: '%s'\n", pFunc->ob_type->tp_name);

        if (pFunc && PyCallable_Check(pFunc)) {
            pArgs = PyTuple_New(1);
            tmp = PyUnicode_FromString(param_id);
            if (!tmp) {
                Py_DECREF(pArgs);
                Py_DECREF(pModule);
                fprintf(stderr, "Cannot convert argument\n");
                return NULL;
            }
            /* tmp reference stolen here: */
            PyTuple_SetItem(pArgs, 0, tmp);
        	pValue = PyObject_CallObject(pFunc, pArgs);
        	Free(pArgs);
        }
        else {}

        Free(pFunc);
        return (Charm_t *) pValue;
    }
    else {
		if (PyErr_Occurred())
			PyErr_Print();
		fprintf(stderr, "Cannot find function.\n");

    }

    return NULL;
}

Charm_t *InitECGroup(Charm_t *pModule, int param_id)
{
	PyObject *pName, *pArgs, *pFunc, *pValue=NULL;

	pName = PyUnicode_FromString("charm.toolbox.ecgroup");

	if(pModule != NULL) PyObject_Del(pModule);
	pModule = PyImport_Import(pName);
	if(pModule != NULL)
		debug("import module ok: '%s'\n", pModule->ob_type->tp_name);
    Free(pName);

    if (pModule != NULL) {
        pFunc = PyObject_GetAttrString(pModule, "ECGroup");
    	debug("got attr string: '%s'\n", pFunc->ob_type->tp_name);

        if (pFunc && PyCallable_Check(pFunc)) {
            pArgs = PyTuple_New(1);
            pValue = PyLong_FromLong(param_id);
            if (!pValue) {
                Free(pArgs);
                Free(pModule);
                fprintf(stderr, "Cannot convert argument\n");
                return NULL;
            }
            /* pValue reference stolen here: */
            PyTuple_SetItem(pArgs, 0, pValue);
        	pValue = PyObject_CallObject(pFunc, pArgs);
        	Free(pArgs);
        }
        else {}

        Free(pFunc);
        return (Charm_t *) pValue;
    }
    else {
		if (PyErr_Occurred())
			PyErr_Print();
		fprintf(stderr, "Cannot find function.\n");

    }

    return NULL;
}

Charm_t *InitIntegerGroup(Charm_t *pModule, int param_id)
{
	PyObject *pName, *pArgs, *pFunc, *pValue=NULL;

	pName = PyUnicode_FromString("charm.toolbox.integergroup");

	if(pModule != NULL) PyObject_Del(pModule);
	pModule = PyImport_Import(pName);
	if(pModule != NULL)
		debug("import module ok: '%s'\n", pModule->ob_type->tp_name);
	Free(pName);

    if (pModule != NULL) {
        pFunc = PyObject_GetAttrString(pModule, "IntegerGroup");
    	debug("got attr string: '%s'\n", pFunc->ob_type->tp_name);

        if (pFunc && PyCallable_Check(pFunc)) {
            pArgs = PyTuple_New(1);
            pValue = PyLong_FromLong(param_id);
            if (!pValue) {
            	Free(pArgs);
            	Free(pModule);
                fprintf(stderr, "Cannot convert argument\n");
                return NULL;
            }
            /* pValue reference stolen here: */
            PyTuple_SetItem(pArgs, 0, pValue);
        	pValue = PyObject_CallObject(pFunc, pArgs);
        	Free(pArgs);
        }
        else {}

        Free(pFunc);
        return (Charm_t *) pValue;
    }
    else {
		if (PyErr_Occurred())
			PyErr_Print();
		fprintf(stderr, "Cannot find function.\n");

    }

    return NULL;
}


// returns the class object
Charm_t *InitScheme(const char *class_file, const char *class_name, Charm_t *pObject)
{
	if(pObject == NULL) return NULL;
	PyObject *pClassName, *pModule, *pFunc, *pArgs, *pValue=NULL;
	pClassName = PyUnicode_FromString(class_file);

	pModule = PyImport_Import(pClassName);
    Free(pClassName);
	if(pModule != NULL)
		debug("successful import: '%s'\n", pModule->ob_type->tp_name);

    if(pModule != NULL) {
    	pFunc = PyObject_GetAttrString(pModule, class_name);
    	debug("got attr string: '%s'\n", pFunc->ob_type->tp_name);

    	if (pFunc && PyCallable_Check(pFunc)) {
            pArgs = PyTuple_New(1);
            /* pValue reference stolen here: */
            PyTuple_SetItem(pArgs, 0, pObject);
            debug("calling class init.\n");
        	// instantiate pValue = ClassName( pObject )
            pValue = PyObject_CallObject(pFunc, pArgs);
            debug("success: \n");
        	Free(pArgs);
    	}
    	else {
    		// call failed
    		if (PyErr_Occurred())
    			PyErr_Print();
    		fprintf(stderr, "Cannot find function.\n");
    	}
        Free(pFunc);
        Free(pModule);
    	return (Charm_t *) pValue;
    }
    else {
		if (PyErr_Occurred())
			PyErr_Print();
		fprintf(stderr, "Cannot complete import.\n");
    }

    return NULL;
}

// Charm adapters usually have 2 arguments: 1st arg is the scheme, and 2nd arg is the group object
Charm_t *InitAdapter(const char *class_file, const char *class_name, Charm_t *pObject1, Charm_t *pObject2)
{
	if(pObject1 == NULL || pObject2 == NULL) return NULL;
	PyObject *pClassFile, *pModule, *pFunc, *pArgs, *pValue=NULL;
	pClassFile = PyUnicode_FromString(class_file);

	pModule = PyImport_Import(pClassFile);
    Free(pClassFile);
    debug("successful import: '%s'\n", pModule->ob_type->tp_name);

    if(pModule != NULL) {
    	pFunc = PyObject_GetAttrString(pModule, class_name);
    	debug("got attr string: '%s'\n", pFunc->ob_type->tp_name);

    	if (pFunc && PyCallable_Check(pFunc)) {
            pArgs = PyTuple_New(2);
            /* pObject1 & pObject2 reference stolen here: note might need to Py_INCREF before this point. */
            PyTuple_SetItem(pArgs, 0, pObject1);
            PyTuple_SetItem(pArgs, 1, pObject2);
            debug("calling class init.\n");
        	// instantiate pValue = ClassName( pObject )
            pValue = PyObject_CallObject(pFunc, pArgs);
            debug("success: \n");
        	Free(pArgs);
    	}
    	else {
    		// call failed
    		if (PyErr_Occurred())
    			PyErr_Print();
    		fprintf(stderr, "Cannot find function.\n");
    	}
        Free(pFunc);
        Free(pModule);
    	return (Charm_t *) pValue;
    }

    return NULL;
}


Charm_t *CallMethod(Charm_t *pObject, const char *func_name, char *types, ...)
{
	PyObject *pFunc, *pValue, *pArgs, *o = NULL, *l = NULL;
	char *fmt, *list, *list2, *token, *token2;
	char delims[] = "[,]";
	va_list arg_list;

	if(pObject == NULL) return NULL; /* can't do anything for you */
	pArgs = PyList_New(0);

	va_start(arg_list, types);

	/* iterate through string one character at a time */
	for(fmt = types; *fmt != '\0'; fmt++)
	{
		if(*fmt != '%') continue;
		switch(*++fmt) {
			case 'b':  o = PyBytes_FromString(va_arg(arg_list, char *));
			           PyList_Append(pArgs, o);
			           Free(o);
			           break;
			case 's':  o = PyUnicode_FromString(va_arg(arg_list, char *));
					   PyList_Append(pArgs, o);
					   Free(o);
					   break;
			case 'I':  o = PyLong_FromLong(atoi(va_arg(arg_list, char *)));
					   PyList_Append(pArgs, o);
					   Free(o);
					   break;
			case 'i':  o = PyLong_FromLong((long) va_arg(arg_list, int *));
					   PyList_Append(pArgs, o);
					   Free(o);
					   break;
			case 'A':  // list of strings?
					   list = va_arg(arg_list, char *);
//					   printf("attrlist ptr: '%s'\n", list);
					   list2 = strdup(list);
					   token = strtok(list2, delims);
					   token2 = trim(token);
					   o = PyList_New(0);
					   while(token2 != NULL) {
						   //printf("Adding : '%s'\n", token2);
						   l = PyUnicode_FromString(token2);
					       PyList_Append(o, l);
					       Py_XDECREF(l);
					       token = strtok(NULL, delims);
					       token2 = trim(token);
					   }

					   PyList_Append(pArgs, o);
					   Free(o);
					   free(list2);
					   break;
			case 'O':  o = va_arg(arg_list, PyObject *);
					   PyList_Append(pArgs, o);
					   Free(o);
					   break;
			default:
					 break;
		}
	}

	va_end(arg_list);

	/* fetch the attribtue from the object context - function in this case */
	pFunc = PyObject_GetAttrString(pObject, func_name);
	/* pFunc is a new reference */

	if (pFunc && PyCallable_Check(pFunc)) {
		/* call the function and pass the tuple since ar*/
		pValue = PyObject_CallObject(pFunc, PyList_AsTuple(pArgs));
		if(pValue == NULL) {
			if (PyErr_Occurred())
				PyErr_Print();
		}
		Free(pFunc);
		Free(pArgs);
		return (Charm_t *) pValue;
	}
	return NULL;
}

Charm_t *GetIndex(Charm_t *pObject, int index)
{
	if(PyTuple_Check(pObject)) {
		if(index < PyTuple_Size(pObject)) {
		   /* return borrowed reference */
		   return PyTuple_GetItem(pObject, index);
		}
	}
	else if(PyList_Check(pObject)) {
		/* handle this case too */
	}

	return NULL;
}

Charm_t *GetDict(Charm_t *pObject, char *key)
{
	if(PyDict_Check(pObject)) {
		return PyDict_GetItemString(pObject, key);
	}

	return NULL;
}

Charm_t *objectToBytes(Charm_t *object, Charm_t *group)
{
	PyObject *pName, *pModule, *pArgs, *pFunc, *pValue=NULL;
	if(group == NULL || object == NULL) return NULL;

	pName = PyUnicode_FromString("charm.core.engine.util");
	pModule = PyImport_Import(pName);
	if(pModule != NULL)
		debug("import module ok: '%s'\n", pModule->ob_type->tp_name);
    Free(pName);

    if (pModule != NULL) {
        pFunc = PyObject_GetAttrString(pModule, "objectToBytes");
    	debug("got attr string: '%s'\n", pFunc->ob_type->tp_name);

        if (pFunc && PyCallable_Check(pFunc)) {
            pArgs = PyTuple_New(2);
            if (!pArgs) {
                Py_DECREF(pArgs);
                Py_DECREF(pModule);
                fprintf(stderr, "Cannot create tuple for arguments\n");
                return NULL;
            }
            /* object & group references stolen here: */
            Py_INCREF(object);
            Py_INCREF(group);
            PyTuple_SetItem(pArgs, 0, object);
            PyTuple_SetItem(pArgs, 1, group);
        	pValue = PyObject_CallObject(pFunc, pArgs);
        	Free(pArgs);
        }
        else {}

        /* perform serialization */
        Free(pFunc);
        return (Charm_t *) pValue;
    }
    else {
		if (PyErr_Occurred())
			PyErr_Print();
		fprintf(stderr, "Cannot find function.\n");
    }

	return NULL;
}

Charm_t *bytesToObject(Charm_t *object, Charm_t *group)
{
	PyObject *pName, *pModule, *pArgs, *pFunc, *pValue=NULL;
	if(group == NULL || object == NULL) return NULL;

	pName = PyUnicode_FromString("charm.core.engine.util");
	pModule = PyImport_Import(pName);
	if(pModule != NULL)
		debug("import module ok: '%s'\n", pModule->ob_type->tp_name);
    Free(pName);

    if (pModule != NULL) {
        pFunc = PyObject_GetAttrString(pModule, "bytesToObject");
    	debug("got attr string: '%s'\n", pFunc->ob_type->tp_name);

        if (pFunc && PyCallable_Check(pFunc)) {
            pArgs = PyTuple_New(2);
            if (!pArgs) {
                Py_DECREF(pArgs);
                Py_DECREF(pModule);
                fprintf(stderr, "Cannot create tuple for arguments\n");
                return NULL;
            }
            /* object & group references stolen here: */
            Py_INCREF(object);
            Py_INCREF(group);
            PyTuple_SetItem(pArgs, 0, object);
            PyTuple_SetItem(pArgs, 1, group);
        	pValue = PyObject_CallObject(pFunc, pArgs);
        	Free(pArgs);
        }
        else {}

        /* perform deserialization */
        Free(pFunc);
        return (Charm_t *) pValue;
    }
    else {
		if (PyErr_Occurred())
			PyErr_Print();
		fprintf(stderr, "Cannot find function.\n");
    }

	return NULL;
}
