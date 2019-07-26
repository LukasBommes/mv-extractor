from distutils.core import setup, Extension
import pkgconfig
import numpy as np

d = pkgconfig.parse('libavformat libswscale opencv4')

video_cap = Extension('video_cap',
                    include_dirs = ['/home/ffmpeg_sources/ffmpeg',
                                    *d['include_dirs'],
                                    np.get_include()],
                    library_dirs = d['library_dirs'],
                    libraries = d['libraries'],
                    sources = ['src/py_video_cap.cpp',
                               'src/video_cap.cpp',
                               'src/time_cvt.cpp'],
                    extra_compile_args = ['-std=c++11'],
                    extra_link_args = ['-fPIC', '-Wl,-Bsymbolic'])

setup (name = 'video_cap',
       version = '1.0',
       description = 'Reads video frames and H264 motion vectors.',
       ext_modules = [video_cap])
