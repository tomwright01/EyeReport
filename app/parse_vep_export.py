"""
Code to parse an espion VEP export file
"""
from datetime import datetime
import logging
from app.espion_objects import TimeSeries, Result, StepChannel, Step, FileError
from app.utils import as_int, as_float
logger = logging.getLogger(__name__)


def load_file(filepath):
    """
    Load an espion export file, check it's in the correct format.
    Returns a file object or raises a FileError exception.
    """
    with open(filepath, 'r') as f:
        line = f.readline()
        if not line.strip().split('\t')[0] == 'Contents Table':
            raise FileError
    return f

def move_top(f, lines):
    """
    Takes an open file and moves to the start of lines
    """
    f.seek(0)
    for i in range(lines - 1):
        f.readline()

def parse_contents(f, sep):
    """
    Read the contents table from an espion export file.
    Returns a dict with the contents
    """
    start_str = 'Contents Table'
    contents_table = {}

    # skip the next two lines, not important
    f.readline()
    f.readline()
    f.readline()
    while True:
        line = f.readline()
        line = line.split(sep)
        if line[0] == '':
            break
        contents_table[line[0]] = {'left': as_int(line[1]),
                                   'top': as_int(line[2]),
                                   'right': as_int(line[3]),
                                   'bottom': as_int(line[4])}
    return contents_table

def parse_header_section(f, contents, sep):

    if not 'Header Table' in contents.keys():
        raise FileError

    headers = {}

    locations = contents['Header Table']
    # scroll to the top of the section
    move_top(f, locations['top'])

    while True:
        line = f.readline()
        line = line.split(sep)
        values = line[locations['left']-1:locations['right']]
        if ''.join(values) == '':
            break
        headers[values[0]] = values[1]

    for header in headers:
        if header == 'Date performed':
            headers[header] = datetime.strptime(headers[header], '%m/%d/%Y  %I:%M:%S %p')
        elif header in ('Steps', 'Channels'):
            headers[header] = as_int(headers[header])
        elif header == 'DOB':
            headers[header] = datetime.strptime(headers[header], '%m/%d/%Y')

    return(headers)

def parse_marker_section(f, contents, sep):
    if not 'Marker Table' in contents.keys():
        raise FileError

    markers = {}

    locations = contents['Marker Table']
    move_top(f, locations['top'])

    if locations['right'] - locations['left'] == 13:
        has_norms = True
    else:
        has_norms = False

    while True:
        line = f.readline()
        line = line.split(sep)
        values = line[locations['left']-1:locations['right']]
        if ''.join(values) == '':
            break

        step_no = int(values[5])
        if has_norms:
            marker = {'chan':as_int(values[6]),
                      'result':values[7],
                      'eye':values[8],
                      'name':values[9],
                      'amp':as_float(values[10]),
                      'amp_norm':values[11],
                      'time':as_float(values[12]),
                      'time_norm':values[13]}
        else:
            marker = {'chan':as_int(values[6]),
                      'result':values[7],
                      'eye':values[8],
                      'name':values[9],
                      'amp':as_float(values[10]),
                      'time':as_float(values[11])}

        if marker['result'].endswith('A'):
            marker['is_average'] = True
            marker['result'] = as_int(marker['result'][0:-1])
        else:
            marker['is_average'] = False
            marker['result'] = as_int(marker['result'])

        if has_norms:
            for key in ['amp_norm', 'time_norm']:
                try:
                    marker[key] = [as_float(val) for val in marker[key].split('+/-')]
                except ValueError:
                    marker[key] = [None, None]

        try:
            markers[step_no].append(marker)
        except KeyError:
            markers[step_no] = []
            markers[step_no].append(marker)

    return(markers)

def parse_summary_table(f, contents, sep):
    if not 'Summary Table' in contents.keys():
        raise FileError

    steps = {}

    locations = contents['Summary Table']
    move_top(f, locations['top'])

    while True:
        line = f.readline()
        line = line.split(sep)
        values = line[locations['left']-1:locations['right']]
        if ''.join(values) == '':
            break
        step_id = int(values[2])
        step_vals = {'result':int(values[3]),
                     'eye':values[4],
                     'trials':int(values[5]),
                     'rejects':int(values[6]),
                     'comment':values[8]}
        try:
            steps[step_id].append(step_vals)
        except KeyError:
            steps[step_id] = [step_vals]

    return steps

def parse_stimulus_table(f, contents, sep):
    if not 'Stimulus Table' in contents.keys():
        raise FileError('Stimulus table not found')

    stimuli = {}

    locations = contents['Stimulus Table']
    move_top(f, locations['top'])

    while True:
        line = f.readline()
        line = line.split(sep)
        values = line[locations['left']-1:locations['right']]
        if ''.join(values) == '':
            break
        step_id = int(values[0])
        step_vals = {'description': values[1],
                     'stim': values[2]}
        stimuli[step_id] = step_vals

    return stimuli

def parse_data_table(f, contents, sep):
    if not 'Data Table' in contents.keys():
        raise FileError('Data table not found')

    data = {}
    # data will end up with structure
    # step
    #    channel
    #        result
    #            trials

    locations = contents['Data Table']
    move_top(f, locations['top'])

    # parse the data summary table to find locations for the trials etc.
    while True:
        line = f.readline()
        line = line.split(sep)
        # ERG step summary info has 5 columns
        values = line[locations['left']-1:locations['left'] + 5]
        if ''.join(values) == '':
            break
        step_no = int(values[0])
        step_col = int(values[1])
        chan_no = int(values[2])
        result_no = int(values[3])
        result_col = int(values[4])
        trial_count = int(values[5])

        try:
            data[step_no].add_channel(chan_no)
        except KeyError:
            data[step_no] = Step(step_no)
            data[step_no].add_channel(chan_no)


        data[step_no].column = step_col

        logger.debug('Adding result: {} to channel:{} of step:{}'
                     .format(result_no, chan_no, step_no))
        try:
            data[step_no].channels[chan_no].results[result_no].column = result_col
        except KeyError:
            data[step_no].channels[chan_no].add_result(result_no)
            data[step_no].channels[chan_no].results[result_no].column = result_col

        data[step_no].channels[chan_no].results[result_no].trial_count = trial_count

    # start reading the real data
    move_top(f, locations['top'])

    # need firt two lines to determine timeseries parameters
    line_one = f.readline()
    line_one = line_one.split(sep)
    line_two = f.readline()
    line_two = line_two.split(sep)

    for step_id, step in data.items():
        time_start = float(line_one[step.column - 1])
        time_delta = float(line_two[step.column - 1]) - time_start
        for channel_id, channel in step.channels.items():
            for result_id, result in channel.results.items():
                result.data = TimeSeries(time_start, time_delta)
                result.data.values.append(float(line_one[result.column - 1]))
                result.data.values.append(float(line_two[result.column - 1]))

                for trial_no in range(result.trial_count):
                    result.trials.append(TimeSeries(time_start, time_delta))
                    result.trials[trial_no].values.append(float(line_one[result.column + trial_no]))
                    result.trials[trial_no].values.append(float(line_two[result.column + trial_no]))

    while True:
        values = f.readline()
        values = values.split(sep)
        if ''.join(values) == '':
            break
        for step_id, step in data.items():
            for channel_id, channel in step.channels.items():
                for result_id, result in channel.results.items():
                    result.data.values.append(float(values[result.column - 1]))
                    for trial_no in range(result.trial_count):
                        result.trials[trial_no].values.append(float(values[result.column + trial_no]))
    return(data)

def read_export_file(filepath, sep='\t'):
    with open(filepath, 'r') as f:
        line = f.readline()
        if not line.strip().split(sep)[0] == 'Contents Table':
            raise FileError
        f.seek(0)
        contents = parse_contents(f)
        header = parse_header_section(f, contents)
        markers = parse_marker_section(f, contents)
        summary = parse_summary_table(f, contents)
        stimuli = parse_stimulus_table(f, contents)
        data = parse_data_table(f, contents)
    return({'contents':contents,
            'headers':header,
            'markers':markers,
            'summary':summary,
            'stimuli':stimuli,
            'data':data})


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    filepath = 'data/vep_export_full.tsv'
    read_export_file(filepath)
