from setuptools import setup, find_packages

setup(
    name='viskillz-glb',
    version='0.1.0',
    namespace_packages=['viskillz'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/viskillz/viskillz-glb',
    license='APACHE LICENSE, VERSION 2.0',
    author='Róbert Tóth',
    author_email='toth.robert@inf.unideb.hu',
    description='',
    python_requires='>=3.10.0',
    install_requires=[
        "wakepy",
        "viskillz-common"
    ],
    entry_points={
        'console_scripts': [
            'viskillz-glb = viskillz.mct.glb:run',
        ]
    }
)
