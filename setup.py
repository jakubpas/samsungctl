#!/usr/bin/env python

import setuptools

setuptools.setup(
    name="samsungctl",
    version="0.8",
    description="Remote control Samsung televisions via TCP/IP connection",
    url="https://github.com/jakubpas/samsungctl",
    author="Jakub Pas",
    author_email="",
    license="MIT",
    long_description=open("README.md").read(),
    entry_points={
        "console_scripts": ["samsungctl=samsungctl.__main__:main"]
    },
    packages=["samsungctl"],
    install_requires=[
        "requests",
        "websocket-client>=1.9.0",
    ],
    extras_require={
        "interactive_ui": ["curses"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Home Automation",
    ],
)
