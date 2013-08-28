from distutils.core import setup

VERSION = '0.1.0'
desc    = """Framework for building interfaces that accept text-based human language input.

In its current state, it is limited in the recognition of human input, and is more akin to an intuitive command-line
format than actual human language input in full sentence structure, but the framework is built the future of this in
mind, and as the framework becomes more 'intelligent', projects that implement this will need only minimal, if any,
changes to their code.

How to use hoomanlogic:


    - Decorate functions with @hoomancando to give it a wrapper for building the parameter args based from text-based
      input.
    - Decorate classes with @hoomaninterface that contain functions decorated with @hoomancando. The parent class can
      be decorated to give all inherited classes the necessary attributes and functions.
    - Create a HoomanOperator instance and register instances of the classes with HoomanOperator.register_interface().

Detailed examples can be found in the examples directory.
"""

setup(name='hoomanlogic',
        version=VERSION, 
        author='Geoffrey Floyd',
        author_email='geoffrey.floyd@hoomanlogic.com',
        url='http://github.com/hoomanlogic/hoomanlogic/',
        download_url='https://pypi.python.org/pypi/hoomanlogic/',
        description='Framework for building interfaces that accept text-based human language input.',
        license='http://www.apache.org/licenses/LICENSE-2.0',
        packages=['hoomanlogic'],
        platforms=['Any'],
        long_description=desc,
        classifiers=['Development Status :: 4 - Beta',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: Apache Software License',
                     'Operating System :: OS Independent',
                     'Topic :: Text Processing',
                     'Topic :: Software Development :: Libraries :: Python Modules',
                     'Programming Language :: Python :: 2.6',
                     'Programming Language :: Python :: 2.7'
                    ]
        )