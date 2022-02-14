import subprocess
import glob
import os
from datetime import datetime
import time
from f90nml import Parser

SBATCH = 'sbatch'
SLEEP_TIME = 600  # time between individual checks
REMAINING_TIME_GRACE = 60
FIRST_GRACEPERIOD = 24 * 3600  # time before end of job, when checking begins
SECOND_GRACEPERIOD = 5 * 3600  # time before end of job, when checking begins
DATAFILE = 'input/data'


class MITgcmDataParser(Parser):
    def __init__(self):
        super().__init__()
        self.comment_tokens += '#'
        self.end_comma = True
        self.indent = " "
        self.column_width = 72
        self.sparse_arrays = True


def loop_command(args):
    """
    One iteration of the loop
    """

    print("INFO: NEW ROUND")

    if not os.path.exists(DATAFILE):
        raise FileNotFoundError(f'we need to have a datafile in {DATAFILE}!')

    print("INFO: updating to latest iternumber")
    timestamp, iternumber = get_latest_timestamp()
    change_data_file(iternumber)
    print(f"INFO: completed. Latest iternumber is {iternumber}")

    print("INFO: starting a new job")
    jobid = run_command(args)
    print(f"INFO: id of new job: {jobid}. Going to sleep.")

    time.sleep(REMAINING_TIME_GRACE)

    remaining_time = get_remaing_time(jobid)
    print(f"INFO: remaining time: {remaining_time}")
    time.sleep(remaining_time.total_seconds() - FIRST_GRACEPERIOD)

    remaining_time = get_remaing_time(jobid)
    time.sleep(remaining_time.total_seconds() - SECOND_GRACEPERIOD)
    print(f"INFO: remaining time: {remaining_time}")

    # Begin waiting for a final output to be created
    while True:
        timestamp, iternumber = get_latest_timestamp()
        time_since_latest_file = datetime.now() - timestamp

        if time_since_latest_file.total_seconds() > SLEEP_TIME:
            time.sleep(SLEEP_TIME)
        else:
            break

    print(f"INFO: canceling job and updating datafile")
    cancel_job(jobid)
    change_data_file(iternumber)


def change_data_file(iternumber):
    """
    Function to parse the MITgcm 'data' file and return the parameter values
    of the given specific keyword.

    Parameters
    ----------
    datafile: string
        Full path to the MITgcm data file.
    Returns
    ----------
    dict
        dictionary of the datafile
    """
    parser = MITgcmDataParser()
    data = parser.read(DATAFILE)

    data["parm03"]["niter0"] = int(iternumber)

    os.remove(DATAFILE)
    data.write(DATAFILE)


def cancel_job(jobid):
    args = ['scancel', str(jobid)]
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()


def get_remaing_time(jobid):
    args = ['squeue', '-h', '-j', str(jobid), '-o', '%e']
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()

    endtime = datetime.fromisoformat(output.decode("utf-8").replace('\n',''))
    now = datetime.now()

    remaining_time = endtime - now

    return remaining_time


def run_command(args):
    p = subprocess.Popen([SBATCH, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    jobid = output.decode("utf-8").replace('\n','').split(' ')[-1]
    return jobid


def get_latest_timestamp():
    list_of_files = glob.glob('run/pickup.*.data')
    latest_file = max(list_of_files, key=os.path.getctime)
    iternumber = int(latest_file.split('.')[-2])
    timestamp = os.path.getctime(latest_file)
    return datetime.fromtimestamp(timestamp), iternumber



