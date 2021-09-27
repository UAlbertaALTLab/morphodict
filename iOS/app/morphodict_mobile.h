/// This header exposes all of the following:
///   - Convenience functions that use the C Python API, to be called from Swift
///    code
///   - morphodict_mobile, a python module written in Objective-C that provides:
///      - access to iOS platform features, e.g., logging
///      - the ability to register callbacks from Swift, that Python code can
///       later invoke

#ifndef morphodict_mobile_h
#define morphodict_mobile_h

#include "Python.h"

/// Initialize the python module.
PyObject* PyInit_morphodict_mobile(void);

/// Only currently-supported callback type: function taking no args
/// and returning void.
typedef void morphodict_callback_t();

/// Register a callback function. This can be called from Swift, to register
/// a callback function written in Swift, which Python code can later invoke
/// with `morphodict_mobile.trigger(name)`.
void morphodict_register_callback(const char* name, morphodict_callback_t* callback);

/// Stop the Django server; to be called from a different thread from the server.
void morphodict_stop_server();

/// Resume listening operations for a Django server previously stopped with `morphodict_stop_server`.
void morphodict_resume_server();

#endif /* morphodict_mobile_h */
