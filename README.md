# loop_submit

Tool to keep expeRT/MITgcm running. Provides a script that will update the data file to the latest available pickup file for continuation of a simulation

## Installation:
```
pip install git+https://github.com/exorad/loop_submit.git
```

Note: If you use anaconda, make sure to be doing this in the environment in which you normally submit your jobs

## Usage

- Go to simulation folder in ssh session.
- Type `update_last_iter` and hit enter.

For an example usage inside a slurm submit file, see `exorad_submit_long2`
