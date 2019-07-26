#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <numpy/arrayobject.h>

#include "video_cap.hpp"

typedef struct {
    PyObject_HEAD
    VideoCap vcap;
} VideoCapObject;


static void
VideoCap_dealloc(VideoCapObject *self)
{
    self->vcap.release();
    Py_TYPE(self)->tp_free((PyObject *) self);
}


static PyObject *
VideoCap_open(VideoCapObject *self, PyObject *args)
{
    const char *url;

    if (!PyArg_ParseTuple(args, "s", &url))
        Py_RETURN_FALSE;

    if (!self->vcap.open(url))
        Py_RETURN_FALSE;

    Py_RETURN_TRUE;
}

static PyObject *
VideoCap_grab(VideoCapObject *self, PyObject *Py_UNUSED(ignored))
{
    if (!self->vcap.grab())
        Py_RETURN_FALSE;

    Py_RETURN_TRUE;
}


static PyObject *
VideoCap_retrieve(VideoCapObject *self, PyObject *Py_UNUSED(ignored))
{
    uint8_t *frame = NULL;
    int width = 0;
    int height = 0;

    MVS_DTYPE *motion_vectors = NULL;
    MVS_DTYPE num_mvs = 0;
    char frame_type[2] = "?";

    double frame_timestamp = 0;

    PyObject *ret = Py_True;

    if (!self->vcap.retrieve(&frame, &width, &height, frame_type, &motion_vectors, &num_mvs, &frame_timestamp)) {
        num_mvs = 0;
        width = 0;
        height = 0;
        frame_timestamp = 0;
        ret = Py_False;
    }

    // To enure that every call of "retrieve" returns a numpy array with it's own
    // underlying data buffer we need to allocate memory for this data buffer
    // and copy the frame buffer into it.
    uint8_t *frame_cp = NULL;
    size_t frame_size = width * height * 3 * sizeof(uint8_t);
    if ((frame_cp = (uint8_t *) malloc(frame_size)))
        memcpy(frame_cp, frame, frame_size);
    else {
        num_mvs = 0;
        width = 0;
        height = 0;
        frame_timestamp = 0;
        ret = Py_False;
    }

    // convert frame buffer into numpy array
    npy_intp dims_frame[3] = {(npy_intp)height, (npy_intp)width, 3};
    PyObject *frame_nd = PyArray_SimpleNewFromData(3, dims_frame, NPY_UINT8, frame_cp);
    PyArray_ENABLEFLAGS((PyArrayObject*)frame_nd, NPY_ARRAY_OWNDATA); // tell numpy it has to free the data

    // convert motion vector buffer into numpy array
    npy_intp dims_mvs[2] = {(npy_intp)num_mvs, 10};
    PyObject *motion_vectors_nd = PyArray_SimpleNewFromData(2, dims_mvs, MVS_DTYPE_NP, motion_vectors);
    PyArray_ENABLEFLAGS((PyArrayObject*)motion_vectors_nd, NPY_ARRAY_OWNDATA);

    return Py_BuildValue("(ONNsd)", ret, frame_nd, motion_vectors_nd, (const char*)frame_type, frame_timestamp);
}


static PyObject *
VideoCap_read(VideoCapObject *self, PyObject *Py_UNUSED(ignored))
{
    uint8_t *frame = NULL;
    int width = 0;
    int height = 0;

    MVS_DTYPE *motion_vectors = NULL;
    MVS_DTYPE num_mvs = 0;
    char frame_type[2] = "?";

    double frame_timestamp = 0;

    PyObject *ret = Py_True;

    if (!self->vcap.read(&frame, &width, &height, frame_type, &motion_vectors, &num_mvs, &frame_timestamp)) {
        num_mvs = 0;
        width = 0;
        height = 0;
        frame_timestamp = 0;
        ret = Py_False;
    }

    // To enure that every call of "retrieve" returns a numpy array with it's own
    // underlying data buffer we need to allocate memory for this data buffer
    // and copy the frame buffer into it.
    uint8_t *frame_cp = NULL;
    size_t frame_size = width * height * 3 * sizeof(uint8_t);
    if ((frame_cp = (uint8_t *) malloc(frame_size)))
        memcpy(frame_cp, frame, frame_size);
    else {
        num_mvs = 0;
        width = 0;
        height = 0;
        frame_timestamp = 0;
        ret = Py_False;
    }

    // convert frame buffer into numpy array
    npy_intp dims_frame[3] = {(npy_intp)height, (npy_intp)width, 3};
    PyObject *frame_nd = PyArray_SimpleNewFromData(3, dims_frame, NPY_UINT8, frame_cp);
    PyArray_ENABLEFLAGS((PyArrayObject*)frame_nd, NPY_ARRAY_OWNDATA); // tell numpy it has to free the data

    // convert motion vector buffer into numpy array
    npy_intp dims_mvs[2] = {(npy_intp)num_mvs, 10};
    PyObject *motion_vectors_nd = PyArray_SimpleNewFromData(2, dims_mvs, MVS_DTYPE_NP, motion_vectors);
    PyArray_ENABLEFLAGS((PyArrayObject*)motion_vectors_nd, NPY_ARRAY_OWNDATA);

    return Py_BuildValue("(ONNsd)", ret, frame_nd, motion_vectors_nd, (const char*)frame_type, frame_timestamp);
}


static PyObject *
VideoCap_release(VideoCapObject *self, PyObject *Py_UNUSED(ignored))
{
    self->vcap.release();
    Py_RETURN_NONE;
}


static PyMethodDef VideoCap_methods[] = {
    {"open", (PyCFunction) VideoCap_open, METH_VARARGS, "Open a video file or device with given filename/url"},
    {"read", (PyCFunction) VideoCap_read, METH_NOARGS, "Grab and decode the next frame and motion vectors"},
    {"grab", (PyCFunction) VideoCap_grab, METH_NOARGS, "Grab the next frame and motion vectors from the stream"},
    {"retrieve", (PyCFunction) VideoCap_retrieve, METH_NOARGS, "Decode the grabbed frame and motion vectors"},
    {"release", (PyCFunction) VideoCap_release, METH_NOARGS, "Release the video device and free ressources"},
    {NULL}  /* Sentinel */
};


static PyTypeObject VideoCapType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "h264extract.VideoCap",
    .tp_basicsize = sizeof(VideoCapObject),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor) VideoCap_dealloc,
    .tp_print = NULL,
    .tp_getattr = NULL,
    .tp_setattr = NULL,
    .tp_as_async = NULL,
    .tp_repr = NULL,
    .tp_as_number = NULL,
    .tp_as_sequence = NULL,
    .tp_as_mapping = NULL,
    .tp_hash = NULL,
    .tp_call = NULL,
    .tp_str = NULL,
    .tp_getattro = NULL,
    .tp_setattro = NULL,
    .tp_as_buffer = NULL,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = "Video Capture Object",
    .tp_traverse = NULL,
    .tp_clear = NULL,
    .tp_richcompare = NULL,
    .tp_weaklistoffset = 0,
    .tp_iter = NULL,
    .tp_iternext = NULL,
    .tp_methods = VideoCap_methods,
    .tp_members = NULL,
    .tp_getset = NULL,
    .tp_base = NULL,
    .tp_dict = NULL,
    .tp_descr_get = NULL,
    .tp_descr_set = NULL,
    .tp_dictoffset = 0,
    .tp_init = NULL,
    .tp_alloc = NULL,
    .tp_new = PyType_GenericNew,
    .tp_free = NULL,
    .tp_is_gc = NULL,
    .tp_bases = NULL,
    .tp_mro = NULL,
    .tp_cache = NULL,
    .tp_subclasses = NULL,
    .tp_weaklist = NULL,
    .tp_del = NULL,
    .tp_version_tag = 0,
    .tp_finalize  = NULL,
};


static PyModuleDef videocapmodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "video_cap",
    .m_doc = "Capture video frames and motion vectors from a H264 encoded stream.",
    .m_size = -1,
};


PyMODINIT_FUNC
PyInit_video_cap(void)
{
    import_array();

    PyObject *m;
    if (PyType_Ready(&VideoCapType) < 0)
        return NULL;

    m = PyModule_Create(&videocapmodule);
    if (m == NULL)
        return NULL;

    Py_INCREF(&VideoCapType);
    PyModule_AddObject(m, "VideoCap", (PyObject *) &VideoCapType);
    return m;
}
