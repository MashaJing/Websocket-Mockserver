from os import environ
from setuptools import find_packages, setup


def find_required():
    with open("requirements.txt") as f:
        return f.read().splitlines()

setup(
    name="websocket-mockserver",
    version=environ.get("VERSION"),
    author="Dmitriy Voroshilov",
    author_email="g.andreevm.d@gmail.com",
    description="Server for mocking websocket messages",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url=environ.get("REPO_URL"),
    packages=find_packages(),
    license="MIT",
    python_requires='>=3.9',
    install_requires=find_required(),
)
