import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='loop_submit',
    version='v0.1',
    packages=setuptools.find_packages(),
    include_package_data=True,
    url='https://github.com/aarondavidschneider/loop_submit',
    license='MIT',
    author='Aaron David Schneider',
    author_email='aaron.schneider@nbi.ku.dk',
    description='simple tool to continuesly submit expeRT jobs on a slurm cluster',
    long_description=long_description,
    long_description_content_type="text/markdown",
    scripts=['scripts/submit_loop'],
    install_requires=[
        "f90nml"
    ]
)