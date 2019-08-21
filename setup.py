import setuptools
from distutils.core import setup, Extension
import pkgconfig
import numpy as np

d = pkgconfig.parse('libavformat libswscale')

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
       version = '1.1.0',
       author='Lukas Bommes',
       author_email=' ',
       license='MIT',
       url='https://github.com/LukasBommes/sfmt-videocap',
       description = ('Reads video frames and H264 motion vectors. '
                      'See documentation at https://github.com/LukasBommes/sfmt-videocap.'),
       keywords=['motion vector', 'video capture', 'h.264'],
       ext_modules = [video_cap],
       python_requires='>=3.6, <3.8',
       setup_requires=['wheel==0.33.6', 'numpy==1.17.0'],
       install_requires=['numpy==1.17.0', 'opencv-python==4.1.0.25'])
