from distutils.core import setup
import typedef

setup(
    name='typedef',
    packages=['typedef'],
    version=typedef.__version__,
    description=typedef.__description__,
    author='bdr00',
    url='https://github.com/bdr00/typedef',  # use the URL to the github repo
    download_url='https://github.com/peterldowns/mypackage/archive/0.1.tar.gz',  # I'll explain this in a second
    keywords=['typedef', 'struct', 'union', ' pack', 'unpack', 'binary'],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent'
    ],
    license='MIT'
)
