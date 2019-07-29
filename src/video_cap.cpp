#include "video_cap.hpp"


VideoCap::VideoCap() {
    this->opts = NULL;
    this->codec = NULL;
    this->fmt_ctx = NULL;
    this->video_dec_ctx = NULL;
    this->video_stream = NULL;
    this->video_stream_idx = -1;
    this->frame = NULL;
    this->img_convert_ctx = NULL;
    this->frame_number = 0;
    this->frame_timestamp = 0.0;
    this->is_rtsp = false;

    memset(&(this->rgb_frame), 0, sizeof(this->rgb_frame));
    memset(&(this->picture), 0, sizeof(this->picture));
    memset(&(this->packet), 0, sizeof(this->packet));
    av_init_packet(&(this->packet));
}


void VideoCap::release(void) {
    if (this->img_convert_ctx != NULL) {
        sws_freeContext(this->img_convert_ctx);
        this->img_convert_ctx = NULL;
    }

    if (this->frame != NULL) {
        av_frame_free(&(this->frame));
        this->frame = NULL;
    }

    av_frame_unref(&(this->rgb_frame));
    memset(&(this->rgb_frame), 0, sizeof(this->rgb_frame));
    memset(&(this->picture), 0, sizeof(this->picture));

    if (this->video_dec_ctx != NULL) {
        avcodec_free_context(&(this->video_dec_ctx));
        this->video_dec_ctx = NULL;
    }

    if (this->fmt_ctx != NULL) {
        avformat_close_input(&(this->fmt_ctx));
        this->fmt_ctx = NULL;
    }

    if (this->opts != NULL) {
        av_dict_free(&(this->opts));
        this->opts = NULL;
    }

    if (this->packet.data) {
        av_packet_unref(&(this->packet));
        this->packet.data = NULL;
    }
    memset(&packet, 0, sizeof(packet));
    av_init_packet(&packet);

    this->codec = NULL;
    this->video_stream = NULL;
    this->video_stream_idx = -1;
    this->frame_number = 0;
    this->frame_timestamp = 0.0;
    this->is_rtsp = false;
}


bool VideoCap::open(const char *url) {

    bool valid = false;
    AVStream *st = NULL;
    int enc_width, enc_height, idx;

    this->release();

    // if another file is already opened
    if (this->fmt_ctx != NULL)
        goto error;

    this->url = url;

    // open RTSP stream with TCP
    av_dict_set(&(this->opts), "rtsp_transport", "tcp", 0);
    av_dict_set(&(this->opts), "stimeout", "5000000", 0); // set timeout to 5 seconds
    if (avformat_open_input(&(this->fmt_ctx), url, NULL, &(this->opts)) < 0)
        goto error;

    // determine if opened stream is RTSP or not (e.g. a video file)
    this->is_rtsp = check_format_rtsp(this->fmt_ctx->iformat->name);

    // read packets of a media file to get stream information.
    if (avformat_find_stream_info(this->fmt_ctx, NULL) < 0)
        goto error;

    // find the most suitable stream of given type (e.g. video) and set the codec accordingly
    idx = av_find_best_stream(this->fmt_ctx, AVMEDIA_TYPE_VIDEO, -1, -1, &(this->codec), 0);
    if (idx < 0)
        goto error;

    // set stream in format context
    this->video_stream_idx = idx;
    st = this->fmt_ctx->streams[this->video_stream_idx];

    // allocate an AVCodecContext and set its fields to default values
    this->video_dec_ctx = avcodec_alloc_context3(this->codec);
    if (!this->video_dec_ctx)
        goto error;

    // fill the codec context based on the values from the supplied codec parameters
    if (avcodec_parameters_to_context(this->video_dec_ctx, st->codecpar) < 0)
        goto error;

    this->video_dec_ctx->thread_count = std::thread::hardware_concurrency();
#ifdef DEBUG
    std::cerr << "Using parallel processing with " << this->video_dec_ctx->thread_count << " threads" << std::endl;
#endif

    // backup encoder's width/height
    enc_width = this->video_dec_ctx->width;
    enc_height = this->video_dec_ctx->height;

    // Init the video decoder with the codec and set additional option to extract motion vectors
    av_dict_set(&(this->opts), "flags2", "+export_mvs", 0);
    if (avcodec_open2(this->video_dec_ctx, this->codec, &(this->opts)) < 0)
        goto error;

    this->video_stream = this->fmt_ctx->streams[this->video_stream_idx];

    // checking width/height (since decoder can sometimes alter it, eg. vp6f)
    if (enc_width && (this->video_dec_ctx->width != enc_width))
        this->video_dec_ctx->width = enc_width;
    if (enc_height && (this->video_dec_ctx->height != enc_height))
        this->video_dec_ctx->height = enc_height;

    this->picture.width = this->video_dec_ctx->width;
    this->picture.height = this->video_dec_ctx->height;
    this->picture.data = NULL;

    // print info (duration, bitrate, streams, container, programs, metadata, side data, codec, time base)
#ifdef DEBUG
    av_dump_format(this->fmt_ctx, 0, url, 0);
#endif

    this->frame = av_frame_alloc();
    if (!this->frame)
        goto error;

    if (this->video_stream_idx >= 0)
        valid = true;

error:

    if (!valid)
        this->release();

    return valid;
}


bool VideoCap::grab(void) {

    bool valid = false;
    int got_frame;

    int count_errs = 0;
    const int max_number_of_attempts = 512;

    // make sure file is opened
    if (!this->fmt_ctx || !this->video_stream)
        return false;

    // check if there is a frame left in the stream
    if (this->fmt_ctx->streams[this->video_stream_idx]->nb_frames > 0 &&
        this->frame_number > this->fmt_ctx->streams[this->video_stream_idx]->nb_frames)
        return false;

    // loop over different streams (video, audio) in the file
    while(!valid) {
        av_packet_unref(&(this->packet));

        // read next packet from the stream
        int ret = av_read_frame(this->fmt_ctx, &(this->packet));

        if (ret == AVERROR(EAGAIN))
            continue;

        // if the packet is not from the video stream don't do anything and get next packet
        if (this->packet.stream_index != this->video_stream_idx) {
            av_packet_unref(&(this->packet));
            count_errs++;
            if (count_errs > max_number_of_attempts)
                break;
            continue;
        }

        // decode the video frame
        avcodec_decode_video2(this->video_dec_ctx, this->frame, &got_frame, &(this->packet));

        if(got_frame) {
#ifdef DEBUG
            // get timestamps of packet from RTPS stream
            std::cerr << "### Frame No. " <<  this->frame_number << " ###" << std::endl;
            std::cerr << "synced: " << packet.synced << std::endl;
            std::cerr << "seq: " << packet.seq << std::endl;
            std::cerr << "timestamp: " << packet.timestamp << std::endl;
            std::cerr << "last_rtcp_ntp_time (NTP): " << packet.last_rtcp_ntp_time << std::endl;
            struct timeval last_rtcp_ntp_time_unix;
            ntp2tv(&packet.last_rtcp_ntp_time, &last_rtcp_ntp_time_unix);
            std::cerr << "last_rtcp_ntp_time (UNIX): ";
            printf("%ld.%06ld\n", last_rtcp_ntp_time_unix.tv_sec, last_rtcp_ntp_time_unix.tv_usec);
            std::cerr << "last_rtcp_timestamp: " << packet.last_rtcp_timestamp << std::endl;
#endif

            // wait for the first RTCP sender report containing RTP timestamp <-> NTP walltime mapping,
            // before this no reliable frame timestmap can be computed
            if (this->is_rtsp && packet.synced) {
                // compute absolute UNIX timestamp for each frame as follows (90 kHz clock as in RTP spec):
                // frame_time_unix = last_rtcp_ntp_time_unix + (timestamp - last_rtcp_timestamp) / 90000
                struct timeval tv;
                ntp2tv(&packet.last_rtcp_ntp_time, &tv);
                double rtp_diff = (double)(packet.timestamp - packet.last_rtcp_timestamp) / 90000.0;
                this->frame_timestamp = (double)tv.tv_sec + (double)tv.tv_usec / 1000000.0 + rtp_diff;
#ifdef DEBUG
                std::cerr << "frame_timestamp (UNIX): " << std::fixed << this->frame_timestamp << std::endl;
#endif
            }
            // if no RTSP is used or no RTP timestamp <-> NTP walltime mapping is received, make timestamp from local system time
            else {
                auto now = std::chrono::system_clock::now();
                this->frame_timestamp = std::chrono::duration<double>(now.time_since_epoch()).count();
            }

            this->frame_number++;
            valid = true;

        }
        else {
            count_errs++;
            if (count_errs > max_number_of_attempts)
                break;
        }

    }

    return valid;
}


bool VideoCap::retrieve(uint8_t **frame, int *width, int *height, char *frame_type, MVS_DTYPE **motion_vectors, MVS_DTYPE *num_mvs, double *frame_timestamp) {

    if (!this->video_stream || !(this->frame->data[0]))
        return false;

    if (this->img_convert_ctx == NULL ||
        this->picture.width != this->video_dec_ctx->width ||
        this->picture.height != this->video_dec_ctx->height ||
        this->picture.data == NULL) {

        // Some sws_scale optimizations have some assumptions about alignment of data/step/width/height
        // Also we use coded_width/height to workaround problem with legacy ffmpeg versions (like n0.8)
        int buffer_width = this->video_dec_ctx->coded_width;
        int buffer_height = this->video_dec_ctx->coded_height;

        this->img_convert_ctx = sws_getCachedContext(
                this->img_convert_ctx,
                buffer_width, buffer_height,
                this->video_dec_ctx->pix_fmt,
                buffer_width, buffer_height,
                AV_PIX_FMT_BGR24,
                SWS_BICUBIC,
                NULL, NULL, NULL
                );

        if (this->img_convert_ctx == NULL)
            return false;

        av_frame_unref(&(this->rgb_frame));
        this->rgb_frame.format = AV_PIX_FMT_BGR24;
        this->rgb_frame.width = buffer_width;
        this->rgb_frame.height = buffer_height;
        if (0 != av_frame_get_buffer(&(this->rgb_frame), 32))
            return false;

        this->picture.width = this->video_dec_ctx->width;
        this->picture.height = this->video_dec_ctx->height;
        this->picture.data = this->rgb_frame.data[0];
    }

    // change color space of frame
    sws_scale(
        this->img_convert_ctx,
        this->frame->data,
        this->frame->linesize,
        0, this->video_dec_ctx->coded_height,
        this->rgb_frame.data,
        this->rgb_frame.linesize
        );

    *frame = this->picture.data;
    *width = this->picture.width;
    *height = this->picture.height;

    // get motion vectors
    AVFrameSideData *sd = av_frame_get_side_data(this->frame, AV_FRAME_DATA_MOTION_VECTORS);
    if (sd) {
        AVMotionVector *mvs = (AVMotionVector *)sd->data;

        *num_mvs = sd->size / sizeof(*mvs);

        if (*num_mvs > 0) {

            // allocate memory for motion vectors as 1D array
            if (!(*motion_vectors = (MVS_DTYPE *) malloc(*num_mvs * 10 * sizeof(MVS_DTYPE))))
                return false;

            // store the motion vectors in the allocated memory (C contiguous)
            for (MVS_DTYPE i = 0; i < *num_mvs; ++i) {
                *(*motion_vectors + i*10     ) = static_cast<MVS_DTYPE>(mvs[i].source);
                *(*motion_vectors + i*10 +  1) = static_cast<MVS_DTYPE>(mvs[i].w);
                *(*motion_vectors + i*10 +  2) = static_cast<MVS_DTYPE>(mvs[i].h);
                *(*motion_vectors + i*10 +  3) = static_cast<MVS_DTYPE>(mvs[i].src_x);
                *(*motion_vectors + i*10 +  4) = static_cast<MVS_DTYPE>(mvs[i].src_y);
                *(*motion_vectors + i*10 +  5) = static_cast<MVS_DTYPE>(mvs[i].dst_x);
                *(*motion_vectors + i*10 +  6) = static_cast<MVS_DTYPE>(mvs[i].dst_y);
                *(*motion_vectors + i*10 +  7) = static_cast<MVS_DTYPE>(mvs[i].motion_x);
                *(*motion_vectors + i*10 +  8) = static_cast<MVS_DTYPE>(mvs[i].motion_y);
                *(*motion_vectors + i*10 +  9) = static_cast<MVS_DTYPE>(mvs[i].motion_scale);
                //*(*motion_vectors + i*11 + 10) = static_cast<MVS_DTYPE>(mvs[i].flags);
            }
        }
    }

    // get frame type (I, P, B, etc.) and create a null terminated c-string
    frame_type[0] = av_get_picture_type_char(this->frame->pict_type);
    frame_type[1] = '\0';

    // return the timestamp which was computed previously in grab()
    *frame_timestamp = this->frame_timestamp;

    return true;
}


bool VideoCap::read(uint8_t **frame, int *width, int *height, char *frame_type, MVS_DTYPE **motion_vectors, MVS_DTYPE *num_mvs, double *frame_timestamp) {
    bool ret = this->grab();
    if (ret)
        ret = this->retrieve(frame, width, height, frame_type, motion_vectors, num_mvs, frame_timestamp);
    return ret;
}


// Returns true if the comma-separated list of format names contains "rtsp"
bool VideoCap::check_format_rtsp(const char *format_names) {

    char str[strlen(format_names) + 1];
    strcpy(str, format_names);

    char *format_name;
    char *buffer = str;

    while ((format_name = strtok_r(buffer, ",", &buffer))) {

        if (strcmp(format_name, "rtsp") == 0)
            return true;
    }

    return false;
}
