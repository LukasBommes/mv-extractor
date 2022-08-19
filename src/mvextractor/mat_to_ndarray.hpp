// Taken from OpenCV master commit e2a5a6a05c7ce64911e1e898e986abe8dd26cab6
// File: opencv/modules/python/cv2.cpp

#include <Python.h>
#include <numpy/ndarrayobject.h>
#include <opencv2/opencv.hpp>
#include "opencv2/core/core.hpp"
#include "opencv2/core/types_c.h"
#include "opencv2/opencv_modules.hpp"
#include "pycompat.hpp"
#include <map>

static PyObject* opencv_error = NULL;

class PyAllowThreads;

class PyEnsureGIL;

#define ERRWRAP2(expr) \
try \
{ \
    PyAllowThreads allowThreads; \
    expr; \
} \
catch (const cv::Exception &e) \
{ \
    PyObject_SetAttrString(opencv_error, "file", PyString_FromString(e.file.c_str())); \
    PyObject_SetAttrString(opencv_error, "func", PyString_FromString(e.func.c_str())); \
    PyObject_SetAttrString(opencv_error, "line", PyInt_FromLong(e.line)); \
    PyObject_SetAttrString(opencv_error, "code", PyInt_FromLong(e.code)); \
    PyObject_SetAttrString(opencv_error, "msg", PyString_FromString(e.msg.c_str())); \
    PyObject_SetAttrString(opencv_error, "err", PyString_FromString(e.err.c_str())); \
    PyErr_SetString(opencv_error, e.what()); \
    return 0; \
}

class NumpyAllocator;

enum { ARG_NONE = 0, ARG_MAT = 1, ARG_SCALAR = 2 };

class NDArrayConverter
{
private:
    int* init();
public:
    NDArrayConverter();
    PyObject* toNDArray(const cv::Mat& m);
};
