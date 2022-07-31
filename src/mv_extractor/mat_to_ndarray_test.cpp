// g++ -fPIC -Wl,-Bsymbolic `pkg-config --cflags opencv4 python3` src/mat_to_ndarray.cpp src/mat_to_ndarray_test.cpp `pkg-config --libs opencv4 python3`

#include <iostream>
#include <opencv2/imgproc/imgproc.hpp>

#include "mat_to_ndarray.hpp"

// tests the functionality of the cv::Mat -> numpy.ndarray converter
int main(void) {

    Py_Initialize();
    import_array();

    NDArrayConverter cvt;

    cv::Mat img = cv::Mat::zeros(cv::Size(1080, 1920), CV_64FC3);

    std::cout << img.size() << std::endl;

    PyObject* ndarray = cvt.toNDArray(img);

    return 0;
}
