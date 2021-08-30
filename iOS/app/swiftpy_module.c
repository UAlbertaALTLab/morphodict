#include "Python.h"
#include "swiftpy_module.h"

// Very basic callback registry: a linked list of structs containing
// (name, function pointer).

typedef struct callable {
    char* name;
    swiftpy_callback_t* callback;
    struct callable* next;
} callable_t;

static callable_t* HEAD = NULL;

void swiftpy_register_callback(const char* name,
    swiftpy_callback_t* callback)
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
        while (node->next) { node = node->next; }
        node->next = new_node;
    }
}

static PyObject* trigger(PyObject *self, PyObject *args) {
    char* callback_name;
    if(!PyArg_ParseTuple(args, "s:trigger", &callback_name))
        return NULL;

    callable_t* node = HEAD;
    while (node != NULL) {
        if (!strcmp(node->name, callback_name)) {
            node->callback();
            Py_RETURN_NONE;
        }
        node = node->next;
    }
    fprintf(stderr, "swiftpy: warning: did not find callback ‘%s’\n",
            callback_name);

    Py_RETURN_NONE;
}

static PyMethodDef SwiftpyMethods[] = {
    {"trigger", trigger, METH_VARARGS,
     "Trigger a callback."},
    {NULL, NULL, 0, NULL}
};

static PyModuleDef SwiftpyModule = {
    PyModuleDef_HEAD_INIT, "swiftpy", NULL, -1, SwiftpyMethods,
    NULL, NULL, NULL, NULL
};

PyObject*
PyInit_swiftpy(void)
{
    return PyModule_Create(&SwiftpyModule);
}
