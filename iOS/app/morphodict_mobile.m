// Please format this file with `clang-format -i --style=webkit`

#import <Foundation/Foundation.h>

#include "morphodict_mobile.h"

// MARK: Logging

/// Log the given string, using NSLog.
///
/// Example: `morphodict_mobile.log('foo')`  will log `foo` to the iOS system
/// log.
static PyObject* do_log(PyObject* self, PyObject* args)
{
    char* msg;
    // For more about argument parsing, see
    // https://docs.python.org/3/extending/extending.html#extracting-parameters-in-extension-functions
    // and the reference https://docs.python.org/3/c-api/arg.html#other-objects
    //
    // The `:log` bit is a function name to include in error messages when
    // invalid args are given.
    if (!PyArg_ParseTuple(args, "s:log", &msg))
        return NULL;

    NSLog(@"%s", msg);

    Py_RETURN_NONE;
}

// MARK: Callback registry

/// Very basic callback registry: a linked list of structs containing
/// (name, function pointer).
typedef struct callable {
    char* name;
    morphodict_callback_t* callback;
    struct callable* next;
} callable_t;

static callable_t* HEAD = NULL;

// documented in header
void morphodict_register_callback(const char* name,
    morphodict_callback_t* callback)
{
    callable_t* new_node = (callable_t*)malloc(sizeof(callable_t));
    new_node->name = strdup(name);
    new_node->callback = callback;
    new_node->next = NULL;

    // add to linked list
    if (!HEAD) {
        HEAD = new_node;
    } else {
        callable_t* node = HEAD;
        while (node->next) {
            node = node->next;
        }
        node->next = new_node;
    }
}

// Implementation of Python-callable morphodict_mobile.trigger
static PyObject* trigger(PyObject* self, PyObject* args)
{
    char* callback_name;
    if (!PyArg_ParseTuple(args, "s:trigger", &callback_name))
        return NULL;

    callable_t* node = HEAD;
    while (node != NULL) {
        if (!strcmp(node->name, callback_name)) {
            node->callback();
            Py_RETURN_NONE;
        }
        node = node->next;
    }
    NSLog(@"warning: did not find callback ‘%s’", callback_name);

    Py_RETURN_NONE;
}

// MARK: Server access

static void run_py_noargs_func(const char* module_name,
    const char* function_name)
{
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();

    PyObject *pModuleName, *pModule, *pFunc;

    pModuleName = PyUnicode_FromString(module_name);
    pModule = PyImport_Import(pModuleName);
    Py_DECREF(pModuleName);

    if (pModule) {
        pFunc = PyObject_GetAttrString(pModule, function_name);
        if (pFunc) {
            PyObject_CallNoArgs(pFunc);
            Py_DECREF(pFunc);
        } else {
            NSLog(@"Error: function not found: %s", function_name);
        }
        Py_DECREF(pModule);
    } else {
        NSLog(@"Error: module not found: %s", module_name);
    }

    PyGILState_Release(gstate);
}

// Documented in header file
void morphodict_stop_server()
{
    run_py_noargs_func("morphodict.runserver.mobile_run_handler", "stop_server");
}

void morphodict_resume_server()
{
    run_py_noargs_func("morphodict.runserver.mobile_run_handler",
        "resume_server");
}

// MARK: Python module setup

static PyMethodDef MorphodictMobileMethods[] = {
    { "log", do_log, METH_VARARGS, "Log a message to the system log." },
    { "trigger", trigger, METH_VARARGS,
        "Trigger a callback previously registered by the C-language function"
        " morphodict_register_callback." },
    { NULL, NULL, 0, NULL }
};

static PyModuleDef MorphodictMobileModule = {
    PyModuleDef_HEAD_INIT,
    "morphodict_mobile",
    NULL,
    -1,
    MorphodictMobileMethods,
    NULL,
    NULL,
    NULL,
    NULL
};

PyObject* PyInit_morphodict_mobile(void)
{
    return PyModule_Create(&MorphodictMobileModule);
}
