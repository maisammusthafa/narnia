#!/usr/bin/env python

import distutils.core
import os.path

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

def _findall(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) \
            if os.path.isfile(os.path.join(directory, f))]

if __name__ == '__main__':
    distutils.core.setup(
        name='narnia',
        version='1.0.0',

        description='A curses-based console client for aria2',
        long_description=long_description,
        keywords='aria2 rpc curses cli console',

        author='Maisam Musthafa',
        author_email='maisam.musthafa@gmail.com',

        license='MIT',
        url='http://bitbucket.org/maisammusthafa/narnia',

        classifiers=[
                'Development Status :: 3 - Alpha',
                'Intended Audience :: End Users/Desktop',
                'Topic :: Internet',
                'License :: OSI Approved :: MIT License',
                'Programming Language :: Python :: 3 :: Only',
        ],

        scripts=['scripts/narnia'],

        data_files=[
            ('share/doc/narnia/config', _findall('doc/config'),
            ('share/doc/narnia',
                ['README.md',
                 'LICENSE.md']))
        ],

        packages=['narnia'])
