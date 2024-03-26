from setuptools import find_packages, setup

REQUIRES = """
numpy>=1.23.4
openai
requests
tqdm
pandas>=1.5.3
tiktoken
rich
portalocker
pillow
matplotlib
seaborn
tabulate
"""


def get_install_requires():
    reqs = [req for req in REQUIRES.split('\n') if len(req) > 0]
    return reqs


with open('README.md') as f:
    readme = f.read()


def do_setup():
    setup(
        name='ada_leval',
        version='0.1.0',
        description='The official implementation for Ada-LEval',
        # url="",
        author="Haodong Duan",
        long_description=readme,
        long_description_content_type='text/markdown',
        cmdclass={},
        install_requires=get_install_requires(),
        setup_requires=[],
        python_requires='>=3.7.0',
        packages=find_packages(exclude=[
            'test*',
            'paper_test*',
        ]),
        keywords=['AI', 'NLP', 'in-context learning'],
        entry_points={
            "console_scripts": []
        },
        classifiers=[
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Intended Audience :: Science/Research',
        ])


if __name__ == '__main__':
    do_setup()
