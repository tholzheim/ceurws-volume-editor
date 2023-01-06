from os import path

from setuptools import setup
from collections import OrderedDict
from volumeEditor import VERSION

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements=f.readlines()

setup(name="ceurws-volume-editor",
      version=VERSION,
      description="Provides a web interface to create CEUR-WS volume pages",
      long_description_content_type='text/markdown',
      url='https://github.com/tholzheim/ceurws-volume-editor',
      download_url='https://github.com/tholzheim/ceurws-volume-editor',
      author='tholzheim',
      license='Apache',
      project_urls=OrderedDict(
        (
            ("Code", "https://github.com/tholzheim/ceurws-volume-editor"),
            ("Issue tracker", "https://github.com/tholzheim/ceurws-volume-editorissues"),
        )
      ),
      classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.10'
      ],
      packages=['volumeEditor'],
      package_data={'volumeEditor': ['templates/*.jinja2']},
      install_requires=requirements,
      entry_points={
         'console_scripts': [
             'ceurwsVolumeEditor = volumeEditor.ceurmake:main',
      ],
    },
      zip_safe=False)
