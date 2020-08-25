import setuptools

long_desciption = open('README.md', 'r')

setuptools.setup(
    name="bot_daddy_bot",
    version="2.0.0",
    author="drforse",
    author_email="george.lifeslice@gmail.com",
    description="Telegram bot with many functions",
    long_description=long_desciption,
    long_description_content_type="text/markdown",
    url="https://github.com/drforse/BotDaddy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)