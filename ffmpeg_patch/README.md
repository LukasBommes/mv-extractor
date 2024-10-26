# FFMPEG patch

This is a patch for the FFMPEG library, which exposes several fields of the internal RTPDemuxContext class to the AVPacket class which is accessible through public APIs. This allows to read out for example timestamp and sequence number of an RTSP packet.

The following files have been patched:
- libavcodec/avcodec.h
- libavformat/rtpdec.c
- libavformat/utils.c

The original source for this patch is provided in "patch_description.docx".

### Detailled Diffs

The following diffs are obtained with
```
diff -u --color=always <ffmpeg-patched-root-dir>/libavcodec/avcodec.h <ffmpeg-root-dir>/libavcodec/avcodec.h
diff -u --color=always <ffmpeg-patched-root-dir>/libavformat/rtpdec.c <ffmpeg-root-dir>/libavformat/rtpdec.c
diff -u --color=always <ffmpeg-patched-root-dir>/libavformat/utils.c <ffmpeg-root-dir>/libavformat/utils.c
```

#### libavcodec/avcodec.h

```diff
--- ffmpeg-patched/libavcodec/avcodec.h 2024-10-26 12:53:50.142954096 +0000
+++ ffmpeg/libavcodec/avcodec.h 2024-10-26 12:56:09.601592921 +0000
@@ -28,6 +28,7 @@
  */
 
 #include <errno.h>
+#include <stdbool.h>
 #include "libavutil/samplefmt.h"
 #include "libavutil/attributes.h"
 #include "libavutil/avutil.h"
@@ -1464,6 +1465,17 @@
 
     int64_t pos;                            ///< byte position in stream, -1 if unknown
 
+    uint32_t timestamp;
+
+    uint64_t last_rtcp_ntp_time;
+
+    uint32_t last_rtcp_timestamp;
+
+    uint16_t seq;
+
+    bool synced;
+
+
 #if FF_API_CONVERGENCE_DURATION
     /**
      * @deprecated Same as the duration field, but as int64_t. This was required
```

#### libavformat/rtpdec.c

```diff
--- ffmpeg-patched/libavformat/rtpdec.c 2024-10-26 12:53:50.238953178 +0000
+++ ffmpeg/libavformat/rtpdec.c 2024-10-26 12:56:09.629592643 +0000
@@ -19,6 +19,8 @@
  * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
  */
 
+#include <stdbool.h>
+
 #include "libavutil/mathematics.h"
 #include "libavutil/avstring.h"
 #include "libavutil/intreadwrite.h"
@@ -591,6 +593,8 @@
  */
 static void finalize_packet(RTPDemuxContext *s, AVPacket *pkt, uint32_t timestamp)
 {
+    bool synced = false;
+
     if (pkt->pts != AV_NOPTS_VALUE || pkt->dts != AV_NOPTS_VALUE)
         return; /* Timestamp already set by depacketizer */
     if (timestamp == RTP_NOTS_VALUE)
@@ -622,6 +626,21 @@
     s->timestamp = timestamp;
     pkt->pts     = s->unwrapped_timestamp + s->range_start_offset -
                    s->base_timestamp;
+
+    /* export private data (timestamps) into AVPacket */
+    if (s->last_rtcp_ntp_time != AV_NOPTS_VALUE && s->last_rtcp_timestamp) {
+        synced = true;
+       pkt->last_rtcp_ntp_time = s->last_rtcp_ntp_time;
+        pkt->last_rtcp_timestamp = s->last_rtcp_timestamp;
+    }
+    else {
+        pkt->last_rtcp_ntp_time = 0;
+        pkt->last_rtcp_timestamp = 0;
+    }
+
+    pkt->seq = s->seq;
+    pkt->timestamp = s->timestamp;
+    pkt->synced = synced;
 }
 
 static int rtp_parse_packet_internal(RTPDemuxContext *s, AVPacket *pkt,
```

#### libavformat/utils.c

```diff
--- ffmpeg-patched/libavformat/utils.c  2024-10-26 12:53:50.254953026 +0000
+++ ffmpeg/libavformat/utils.c  2024-10-26 12:56:09.641592523 +0000
@@ -21,6 +21,7 @@
 
 #include <stdarg.h>
 #include <stdint.h>
+#include <stdbool.h>
 
 #include "config.h"
 
@@ -1571,6 +1572,11 @@
 {
     int ret = 0, i, got_packet = 0;
     AVDictionary *metadata = NULL;
+    uint32_t timestamp;
+    uint64_t last_rtcp_ntp_time;
+    uint32_t last_rtcp_timestamp;
+    uint16_t seq;
+    bool synced;
 
     av_init_packet(pkt);
 
@@ -1578,6 +1584,13 @@
         AVStream *st;
         AVPacket cur_pkt;
 
+        /* copy over the RTP time stamp */
+       timestamp = cur_pkt.timestamp;
+       last_rtcp_ntp_time = cur_pkt.last_rtcp_ntp_time;
+       last_rtcp_timestamp = cur_pkt.last_rtcp_timestamp;
+       seq = cur_pkt.seq;
+       synced = cur_pkt.synced;
+
         /* read next packet */
         ret = ff_read_packet(s, &cur_pkt);
         if (ret < 0) {
@@ -1762,6 +1775,12 @@
                av_ts2str(pkt->dts),
                pkt->size, pkt->duration, pkt->flags);
 
+    pkt->timestamp = timestamp;
+    pkt->last_rtcp_ntp_time = last_rtcp_ntp_time;
+    pkt->last_rtcp_timestamp = last_rtcp_timestamp;
+    pkt->seq = seq;
+    pkt->synced = synced;
+
     return ret;
 }
```
