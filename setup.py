from setuptools import setup

setup(
    name='dnsovertlsproxy',
    version='0.1.0',
    author='Matheus Bessa',
    author_email='matheusbpf@gmail.com',
    description='Python DNS over TLS proxy',
    classifiers=["Development Status :: 3 - Alpha",
                 "Environment :: Console",
                 "Topic :: Utilities"],
    packages=['dnsovertlsproxy'],
    python_requires='>=3.2',
    entry_points={
        'console_scripts': [
            'dnsovertlsproxy = dnsovertlsproxy.dnsovertlsproxy:run',
        ],
    },
)
