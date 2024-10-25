from setuptools import find_packages, setup, Extension
import pkgconfig
import numpy as np


d = pkgconfig.parse('libavformat libswscale opencv4')

print("Numpy dir: ", np.get_include())

mvextractor = Extension('mvextractor.videocap',
    include_dirs = [
        *d['include_dirs'],
        np.get_include()
    ],
    library_dirs = d['library_dirs'],
    libraries = d['libraries'],
    sources = [
        'src/mvextractor/py_video_cap.cpp',
        'src/mvextractor/video_cap.cpp',
        'src/mvextractor/time_cvt.cpp',
        'src/mvextractor/mat_to_ndarray.cpp'
    ],
    extra_compile_args = ['-std=c++11'],
    extra_link_args = ['-fPIC', '-Wl,-Bsymbolic'])

setup(name='motion-vector-extractor',
    author='Lukas Bommes',
    author_email=' ',
    version="1.0.7",
    license='MIT',
    url='https://github.com/LukasBommes/mv-extractor',
    description=('Reads video frames and MPEG-4/H.264 motion vectors.'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: X11 Applications",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Capture",
        "Topic :: Multimedia :: Video :: Display",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: C",
        "Programming Language :: C++",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    keywords=['motion vector', 'video capture', 'mpeg4', 'h.264', 'compressed domain'],
    ext_modules=[mvextractor],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
            'console_scripts': [
                    'extract_mvs=mvextractor.__main__:main',
            ],
    },
    python_requires='>=3.9, <4',
    install_requires=['pkgconfig>=1.5.1', 'numpy>=1.17.0', 'opencv-python>=4.1.0.25,<4.6'])
