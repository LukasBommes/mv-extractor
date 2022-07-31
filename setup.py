from setuptools import find_packages, setup, Extension
import pkgconfig
import numpy as np

d = pkgconfig.parse('libavformat libswscale opencv4')

print("Numpy dir: ", np.get_include())

mv_extractor = Extension('mv_extractor.videocap',
       include_dirs = [
              *d['include_dirs'],
              np.get_include()
       ],
       library_dirs = d['library_dirs'],
       libraries = d['libraries'],
       sources = [
              'src/mv_extractor/py_video_cap.cpp',
              'src/mv_extractor/video_cap.cpp',
              'src/mv_extractor/time_cvt.cpp',
              'src/mv_extractor/mat_to_ndarray.cpp'
       ],
       extra_compile_args = ['-std=c++11'],
       extra_link_args = ['-fPIC', '-Wl,-Bsymbolic'])

setup(name='mv_extractor',
       author='Lukas Bommes',
       author_email=' ',
       version="1.0.5",
       license='MIT',
       url='https://github.com/LukasBommes/mv-extractor',
       description=('Reads video frames and MPEG-4/H.264 motion vectors.'),
       keywords=['motion vector', 'video capture', 'mpeg4', 'h.264', 'compressed domain'],
       ext_modules=[mv_extractor],
       packages=find_packages(where='src'),
       package_dir={'': 'src'},
       #package_dir={'mv_extractor': 'src'},
       #package_data={
       #       'mv_extractor': [
       #              'vid.mp4',
       #              ''
       #       ],
       #},
       entry_points={
              'console_scripts': [
                     'extract_mvs=mv_extractor.__main__:main',
              ],
       },
       python_requires='>=3.8, <4',
       install_requires=['pkgconfig>=1.5.1', 'numpy>=1.17.0', 'opencv-python>=4.1.0.25,<4.6'])
