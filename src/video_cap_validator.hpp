#include "video_cap.hpp"

/*
*    Wrapper around VideoCap which provides a flag `cap_is_valid` to indicate whether
*    the corresponding stream could be opened successfully
*/

class VideoCapWithValidator : public VideoCap {

private:
    bool cap_is_valid;

public:
    VideoCapWithValidator() : VideoCap() {
        this->cap_is_valid = true;
    }

    void mark_valid() {
        this->cap_is_valid = true;
    }

    void mark_invalid() {
        this->cap_is_valid = false;
    }

    bool is_valid() {
        return this->cap_is_valid;
    }
};
