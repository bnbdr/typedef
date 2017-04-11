from distutils.core import setup
import typedef

setup(
    name='typedef',
    packages=['typedef'],
    version=typedef.__version__,
    description=typedef.__description__,
    author='bdr00',
    author_email='bad.32@outlook.com',
    url='https://github.com/bdr00/typedef',
    download_url='https://github.com/bdr00/typedef/archive/v0.9.0.5.tar.gz',
    keywords=['typedef', 'struct', 'union', ' pack', 'unpack', 'binary'],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent'
    ],
    license='MIT'
)
