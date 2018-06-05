from distutils.core import setup
import typedef

author='bnbdr'
setup(
    name='typedef',
    packages=['typedef'],
    version=typedef.__version__,
    description=typedef.__description__,
    author=author,
    author_email='bad.32@outlook.com',
    url='https://github.com/{}/typedef',
    download_url='https://github.com/{}/typedef/archive/v{}.tar.gz'.format(author, typedef.__version__),
    keywords=['typedef', 'struct', 'union', ' pack', 'unpack', 'binary'],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent'
    ],
    license='MIT'
)
