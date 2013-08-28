###########
hoomanlogic
###########


What is hoomanlogic?
====================

hoomanlogic is a project to a framework to extend code to be used by human-input text-based language.


Installing hoomanlogic
======================

python setup.py install

Python 2.6+ or 2.7+ is required for hoomanlogic v0.1.0+


Running Unit Tests
==================

In the source tree do the following:

    python run_tests.py parsedatetime


Implementing hoomanlogic
========================

How to use hoomanlogic:


    - Decorate functions with @hoomancando to give it a wrapper for building the parameter args based from text-based
      input.
    - Decorate classes with @hoomaninterface that contain functions decorated with @hoomancando. The parent class can
      be decorated to give all inherited classes the necessary attributes and functions.
    - Create a HoomanOperator instance and register instances of the classes with HoomanOperator.register_interface().

Detailed examples can be found in the examples directory.


Documentation
=============

The generated documentation is included by default in the docs
directory and can also be viewed online at

    http://www.hoomanlogic.com/code/hoomanlogic/docs/index.html

The docs can be generated using either of the two commands:

    python setup.py doc
    epydoc --html --config epydoc.conf


Notes
=====

In its current state, it is limited in the recognition of human input, and is more akin to an intuitive command-line
format than actual human language input in full sentence structure, but the framework is built the future of this in
mind, and as the framework becomes more 'intelligent', projects that implement this will need only minimal, if any,
changes to their code.


Preferred Development Stack
===========================

Continuous Integration Server:  **jenkins**
Version Control:                **git**
Documentation:                  **Sphinx**
Testing:                        **pytest**
Mocking:                        **monkeypatch**
Integrated Development Env:     **PyCharm**