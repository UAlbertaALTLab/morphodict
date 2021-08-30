// A bridge to allow python to call into swift code. For now,
// only string messages are supported.
//
// From swift:
//
//    swiftpy_register_callback("ready") { print("hello from swift") }
//
// From python:
//
//    import swiftpy
//
//    swiftpy.trigger("ready")
//    // prints "hello from swift"

#ifndef swiftpy_module_h
#define swiftpy_module_h

#include "Python.h"

// Only currently-supported callback type: function taking no args
// and returning void
typedef void swiftpy_callback_t();

PyObject* PyInit_swiftpy(void);
void swiftpy_register_callback(const char* name, swiftpy_callback_t* callback);

#endif /* swiftpy_module_h */
