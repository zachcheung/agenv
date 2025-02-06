from setuptools import setup, find_packages

setup(
    name="agenv",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["python-dotenv"],
    description="Load environment variables from age-encrypted files",
    author="Zach Cheung",
    author_email="kuroro.zhang@gmail.com",
    url="https://github.com/zachcheung/agenv",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
