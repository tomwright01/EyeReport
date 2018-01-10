"""
Code to parse an espion mferg export file
"""
from datetime import datetime
import logging
from app.espion_objects import TimeSeries, FileError, Hexagon
from app.utils import as_int, as_float, read_split_line, find_section_col

logger = logging.getLogger(__name__)

def move_top(f, lines):
    """
    Takes an open file and moves to the start of lines
    """
    f.seek(0)
    for i in range(lines - 1):
        f.readline()

def parse_parameters(f):
    logger.debug('Parsing parameters')
    parameters = {}
    move_top(f, 2)
    while True:
        line = f.readline()
        line = line.split('\t')
        if line[0] == '':
            break
        parameters[line[0]] = line[1]
    for parameter in parameters:
        if parameter in ['Test Date', 'DOB']:
            parameters[parameter] = datetime.strptime(parameters[parameter], '%m/%d/%Y')
        if parameter in ['Hexagons', 'Kernel Order', 'Sequence Bits', 'Filler Frames']:
            parameters[parameter] = as_int(parameters[parameter])

    return parameters

def parse_markers(f):
    logger.debug('Parsing markers')
    hexagons = {}

    move_top(f, 1)
    line = read_split_line(f)
    start_col = find_section_col(line, 'Hexagon')
    line = read_split_line(f, start_col=start_col)
    if line[5] == 'Left Eye':
        # both eyes exported
        binocular = True
    else:
        binocular = False
    eye = line[1]

    f.readline()
    while True:
        line = read_split_line(f, start_col=start_col)
        if line[0] == '':
            break
        hexagon1 = Hexagon(eye, line[0])
        hexagon1.n1 = (line[1], line[2])
        hexagon1.p1 = (line[3], line[4])

        if binocular:
            hexagon2 = Hexagon('Left Eye', line[1])
            hexagon2.n1 = (line[5], line[6])
            hexagon2.p1 = (line[7], line[8])
            hexagons[line[0]] = (hexagon1, hexagon2)
        else:
            hexagons[line[0]] = hexagon1
    return hexagons

def parse_dimensions(f):
    logger.debug('Parsing dimensions')
    dimensions = {}
    move_top(f,1)
    line = read_split_line(f)
    start_col = find_section_col(line, 'Dimensions')

    while True:
        line = read_split_line(f, start_col=start_col)
        if line[0] == '':
            break
        dimensions[line[0]] = as_int(line[1])
    return dimensions

def parse_positions(f):
    logger.debug('Parsing positions')
    locations = {}
    move_top(f,1)
    line = read_split_line(f)
    start_col = find_section_col(line, ['Hexagon', 'X'])
    while True:
        line = read_split_line(f, start_col=start_col)
        if not line or line[0] == '':
            break
        hex = line[0]
        x_locs = []
        y_locs = []
        x_locs.append(as_float(line[1]))
        y_locs.append(as_float(line[2]))
        for i in range(6):
            line = read_split_line(f, start_col=start_col)
            x_locs.append(as_float(line[1]))
            y_locs.append(as_float(line[2]))
        locations[hex] = (x_locs, y_locs)
    return locations

def parse_timeseries(f, hexcount):
    logger.debug('Parsing timeseries')
    hexgons = {}
    col_head_raw = 'Hex {} (R)'
    col_head_smooth = 'Hex {} (S)'

    eye_strs = {'left': {'str':'Left Eye (nV)'},
                'right': {'str':'Right Eye (nV)'}}

    move_top(f,1)
    line = read_split_line(f)

    for key, val in eye_strs.items():
        try:
            eye_strs[key]['start_idx'] = find_section_col(line, val['str'])
        except IndexError:
            eye_strs[key]['start_idx'] = None
    line = read_split_line(f)
    time_col = find_section_col(line, 'Time (ms)')
    line = read_split_line(f)
    time_1 = as_float(line[time_col])
    line = read_split_line(f)
    time_2 = as_float(line[time_col])
    delta = time_2 - time_1
    move_top(f, 2)

    # find the column indexes for the raw and smooth data
    # going to populate each item (hexagon) in the dict with the column index
    # and a time series object
    line = read_split_line(f)
    col_idx_raw = {}
    col_idx_smooth = {}
    for hex_id in range(hexcount):
        hex_id = hex_id + 1
        try:
            col_idx_raw[hex_id] = [find_section_col(line, col_head_raw.format(hex_id)),
                                   TimeSeries(start=time_1, delta=delta)]
        except IndexError:
            col_idx_raw[hex_id] = None
        try:
            col_idx_smooth[hex_id] = [find_section_col(line, col_head_smooth.format(hex_id)),
                                      TimeSeries(start=time_1, delta=delta)]
        except IndexError:
            col_idx_smooth[hex_id] = None

    while True:
        line = read_split_line(f)
        if line[time_col] == '':
            break
        for hex_id in range(hexcount):
            # use the column index to read the data and populate the time series
            hex_id = hex_id + 1
            if col_idx_raw[hex_id]:
                col_idx_raw[hex_id][1].values.append(line[col_idx_raw[hex_id][0]])
            if col_idx_smooth[hex_id]:
                col_idx_smooth[hex_id][1].values.append(line[col_idx_smooth[hex_id][0]])
    data_raw = {key: val[1] for key, val in col_idx_raw.items()}
    data_smooth = {key: val[1] for key, val in col_idx_smooth.items()}

    return({'raw': data_raw, 'smooth': data_smooth})

def read_mferg_export_file(filepath):
    with open(filepath, 'r') as f:
        line = f.readline()
        if not line.strip().split('\t')[0] == 'Parameter':
            raise FileError
        f.seek(0)
        parameters = parse_parameters(f)
        hex_count = as_int(parameters['Hexagons'])
        markers = parse_markers(f)
        dimensions = parse_dimensions(f)
        positions = parse_positions(f)
        data = parse_timeseries(f, hex_count)
    return({'params': parameters,
            'markers': markers,
            'dims': dimensions,
            'positions': postitions,
            'data': data})

if __name__=='__main__':
    fname = 'data/mferg-Both Eyes-11.22.2017.TXT'
    read_mferg_export_file(fname)
    import pdb; pdb.set_trace()
