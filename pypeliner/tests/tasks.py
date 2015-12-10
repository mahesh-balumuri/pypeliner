import itertools
import os

import pypeliner
import pypeliner.workflow
import pypeliner.managed as mgd


class stuff:
    def __init__(self, some_string):
        self.some_string = some_string

def read_stuff(filename):
    with open(filename, 'r') as f:
        return stuff(''.join(f.readlines()).rstrip())

def split_stuff(stf):
    return dict([(ind,stuff(value)) for ind,value in enumerate(list(stf.some_string))])

def split_file_byline(in_filename, lines_per_file, out_filename_callback, max_files=None):
    with open(in_filename, 'r') as in_file:
        def line_group(line, line_idx=itertools.count()):
            return int(next(line_idx) / lines_per_file)
        for file_idx, lines in itertools.groupby(in_file, key=line_group):
            if max_files is not None and file_idx >= max_files:
                break
            with open(out_filename_callback(file_idx), 'w') as out_file:
                for line in lines:
                    out_file.write(line)

def do_file_stuff(in_filename, out_filename, toadd):
    with open(in_filename, 'r') as in_file, open(out_filename, 'w') as out_file:
        line_number = 0
        for line in in_file:
            out_file.write(str(line_number) + str(toadd) + line.rstrip() + '\n')
            line_number += 1

def merge_file_byline(in_filenames, out_filename):
    with open(out_filename, 'w') as out_file:
        for id, in_filename in sorted(in_filenames.items()):
            with open(in_filename, 'r') as in_file:
                for line in in_file.readlines():
                    out_file.write(line)

def split_by_line(stf):
    return dict([(ind,stuff(value)) for ind,value in enumerate(stf.some_string.split('\n'))])

def split_by_char(stf):
    return dict([(ind,stuff(value)) for ind,value in enumerate(list(stf.some_string))])

def do_stuff(a):
    return a + '-'

def do_paired_stuff(output_filename, input1_filename, input2_filename):
    os.system('cat ' + input1_filename + ' ' + input2_filename + ' > ' + output_filename)

def dict_arg_stuff(output_filenames, input_filenames):
    append_to_lines(input_filenames['1'], '1', output_filenames['1'])
    append_to_lines(input_filenames['2'], '2', output_filenames['2'])

def merge_stuff(stfs):
    merged = ''
    for split, stf in sorted(stfs.iteritems()):
        merged = merged + stf
    return merged

def write_stuff(a, filename):
    with open(filename, 'w') as f:
        f.write(a)

def append_to_lines(in_filename, append, out_filename):
    with open(in_filename, 'r') as in_file, open(out_filename, 'w') as out_file:
        for line in in_file:
            out_file.write(line.rstrip() + append + '\n')

def append_to_lines_instance(in_filename, instance, out_filename):
    with open(in_filename, 'r') as in_file, open(out_filename, 'w') as out_file:
        for line in in_file:
            out_file.write(line.rstrip() + str(instance) + '\n')

def copy_file(in_filename, out_filename):
    with open(in_filename, 'r') as in_file, open(out_filename, 'w') as out_file:
        for line in in_file:
            out_file.write(line)

def write_list(in_list, out_filename):
    with open(out_filename, 'w') as out_file:
        for a in sorted(in_list):
            out_file.write(str(a[0]))

def do_nothing(*arg):
    pass

def do_assert(*arg):
    assert False

def set_chunks():
    return [1, 2]

def file_transform(in_filename, out_filename, prefix, template_filename, merge_templates):
    with open(template_filename, 'w'):
        pass
    with open(in_filename, 'r') as in_file, open(out_filename, 'w') as out_file:
        for key, value in merge_templates.iteritems():
            out_file.write('{0}\t{1}\n'.format(key, value))
        for line in in_file:
            out_file.write('{0}'.format(prefix) + line)

def write_files(out_filename_callback):
    for chunk in (1, 2):
        with open(out_filename_callback(chunk), 'w') as f:
            f.write('file{0}\n'.format(chunk))

def check_temp(output_filename, temp_filename):
    with open(output_filename, 'w') as output_file:
        output_file.write(temp_filename)

def create_workflow_2(input_filename, output_filename):
    workflow = pypeliner.workflow.Workflow(default_ctx={'mem':1})

    workflow.transform(
        name='dofilestuff1',
        func=do_file_stuff,
        args=(
            mgd.InputFile(input_filename),
            mgd.TempOutputFile('intermediate1'),
            'a'))

    workflow.transform(
        name='dofilestuff2',
        func=do_file_stuff,
        args=(
            mgd.TempInputFile('intermediate1'),
            mgd.OutputFile(output_filename),
            'b'))

    return workflow

def create_workflow_1(input_filename, output_filename):
    workflow = pypeliner.workflow.Workflow(default_ctx={'mem':1})

    # Read data into a managed object
    workflow.transform(
        name='read',
        func=read_stuff,
        ret=mgd.TempOutputObj('input_data'),
        args=(mgd.InputFile(input_filename),))

    # Extract a property of the managed object, modify it
    # and store the result in another managed object
    workflow.transform(
        name='do',
        func=do_stuff,
        ret=mgd.TempOutputObj('output_data'),
        args=(mgd.TempInputObj('input_data').prop('some_string'),))

    # Write the object to an output file
    workflow.transform(
        name='write',
        func=write_stuff,
        args=(
            mgd.TempInputObj('output_data'),
            mgd.TempOutputFile('output_file')))

    # Recursive workflow
    workflow.subworkflow(
        name='sub_workflow_2',
        func=create_workflow_2,
        args=(
            mgd.TempInputFile('output_file'),
            mgd.OutputFile(output_filename)))

    return workflow
