from setuptools import setup, find_packages

setup(
    name="subtranslator",
    version="0.1.0",
    description="AI-powered subtitle localization tool using Google Gemini models",
    author="",
    author_email="",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "google-generativeai",
        "pysrt",
        "cryptography",
        "pytest"
    ],
    entry_points={
        "console_scripts": [
            "subtranslator = subtranslator.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.7',
)
