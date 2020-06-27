import setuptools
import constants

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="ArgConfigParse",
    version=constants.ARGCONFIGPARSE_VERSION,
    author="Aaron Ciuffo",
    author_email="aaron.ciuffo@gmail.com",
    description=("Merge multiple configuraton files and command line arguments into a single configuration"),
    license="GP",
    keywords="argparse config",
    url="https://github.com/txoof/ArgConfigParse",
    packages=setuptools.find_packages(),
    install_requires=[],
    long_description = long_description,
    long_description_content_type = "text/markdown",
    classifiers=[
	"Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
	"License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
	"Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>3.6'
)
