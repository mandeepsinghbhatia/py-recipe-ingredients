from setuptools import setup, find_packages

APP = ['recipe-get-ingredients.py']
OPTIONS = {
    "argv_emulation": True,
}
DATA_FILES = [("",["recipe-ingredients.db"])]
setup(app=APP,
      name="recipe-get-ingredients",
      version="0.1.0",
      author="Mandeep Singh Bhatia",
      options={"py2app": OPTIONS},
      setup_requires=["py2app"],
      data_files=DATA_FILES
      )