from setuptools import setup, find_packages

setup(name='ortho_correct',
      version='0.0.5',
      description='a spell checker',
      author='Mathilde, Xin',
      author_email="carolina.maeghan@gmail.com, chenxin9812@gmail.com",
      url='https://github.com/pypa/sampleproject',
      packages=find_packages(),
      install_requires=[
            'Spacy',
            'requests'
      ]
      )
