from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in customizations/__init__.py
from customizations import __version__ as version

setup(
	name="customizations",
	version=version,
	description="Customized requirments for Payment Entry , Jornal Entry and Fees Doctypes .",
	author="Sherif Sultan",
	author_email="na",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
