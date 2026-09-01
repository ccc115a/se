import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ai6", # Replace with your own username
    version="1.2.1",
    author="ccckmit",
    author_email="ccckmit@gmail.com",
    description="ai6 -- Artificial Intelligence Example Code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ccc-py/nn6",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)