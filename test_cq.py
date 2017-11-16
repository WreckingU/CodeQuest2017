#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_cq.py:
Testing module used to easily test answers to Code Quest
challenges through the use of unittest. When run, this will
go through the working directory looking for a group of files
that follow the naming scheme:
    'Prob(xx).in.txt'  - Input to solution script
    'Prob(xx).out.txt' - Expected output to solution script
    'Prob(xx).py' 		- Solution script
where (xx) is a two digit number representing the problem's
number. When all three of these files are found for a problem,
a test method will be created (and added to a testing class) that
will run the solution script with the input and check if
the output is equivalent to the expected output. As soon
as all test functions are created, unittest will be run and
return the results.

---------- BEGIN LICENSE [MIT] ----------
Copyright 2017 Ryan Drew

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
---------- END LICENSE [MIT] ----------
"""

import sys
import os
import subprocess
import logging
import shutil
import tempfile
import re
import difflib
import unittest


REGEX_PATTERN = "Prob[0-9]{2}\.((in|out)\.txt|py)"
LOG_FORMAT = \
    "%(asctime)s;FUNC:(%(funcName)s);LINENO:(%(lineno)d);%(levelname)s: %(message)s"
# setup file logging
# do basic config that includes logging to file 'test_cq.log' and to stream
# if -v arg is passed level will be changed to INFO
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)


def log_func_decorator(func):
    """
    Decorator to log the execution of a function: its start, end, output and execptions
    """

    logger = logging.getLogger()

    def wrapper(*args, **kwargs):
        logger.info(
            'Executing function "{}" (args: {}, kwargs: {})'.format(
                func.__name__, args, kwargs)
        )

        try:
            func_output = func(*args, **kwargs)
        except Exception as e:  # except any exception, log it than raise it
            logger.warning(
                'While executing function "{}", ' \
                'exception was raised: "{}".'.format(func.__name__, str(e))
            )
            raise e
        else:
            logger.info(
                'Function "{}" execute successfully with ' \
                'output: "{!r}"'.format(func.__name__, func_output)
            )
            return func_output

    return wrapper


@log_func_decorator
def get_cq_files(target_dir):
    """
    Find all files in target_dir that are named: 'Prob(xx).in.txt',
    'Prob(xx).out.txt' and 'Prob(xx).py' where (xx) is a two digit number.
    :param target_dir: File path to a directory on the system.
    :return: set() of the full paths to each file.
    """

    # get logger
    logger = logging.getLogger()

    # param checking
    if not (os.path.exists(target_dir) and os.path.isdir(target_dir)):
        raise OSError("Given target directory '{}' either does not" \
                      "exist or is not a directory.".format(target_dir))
    # if param checks out, then keep going

    # setup regular expression object
    logger.debug('Using regex pattern: "{}"'.format(REGEX_PATTERN))
    reg_pattern = re.compile(REGEX_PATTERN)

    # return all matches as a set
    """
    This is cool, but can't log anything :(
    return {  # a '/' works on both linux and windows
        "{}/{}".format(target_dir, f) for f in os.listdir(target_dir) if \
        reg_pattern.match(f)
    }
    """

    matched = set()
    for f in os.listdir(target_dir):
        if reg_pattern.match(f):
            logger.debug('Matched regex: "{}"'.format(f))
            matched.add(f)
        else:
            logger.debug('Did not match regex: "{}"'.format(f))
    return matched


@log_func_decorator
def group_cq_files(cq_files):
    """
    Groups the three different types of code quest files by their problem
    number into a dictionary. The keys are integears representing the problem
    number, the values are a list of the associated files.
    :param cq_files: Iterator of Code Quest files.
    :return: {int(Problem number): [(Prob(xx).in.txt), (Prob(xx).out.txt),
            (Prob(xx).py)]}
    """

    # get logger
    logger = logging.getLogger()

    # x will be file path, so get the filename and then find the problem number
    # at indexes 4-5.
    get_prob_num = lambda x: os.path.basename(x)[4:6]
    grouped = dict()
    for cq_file in cq_files:
        _prob_num = int(get_prob_num(cq_file))
        logger.debug(
            "Placing '{}' (problem number: {})".format(cq_file, _prob_num)
        )
        try:
            grouped.get(_prob_num).append(cq_file)
        except:
            grouped[_prob_num] = [cq_file]
            logger.debug(
                "Created new list for problem number {}".format(_prob_num)
            )

    return grouped


@log_func_decorator
def check_solution(in_file, out_file, solution_file):
    """
    Runs the given solution file, passing it the input of in_file
    and asserting its output to the contents of out_file. Each file
    should include the full path to the file
    :param in_file: Program input file for solution file (Prob(xx).in.txt)
    :param out_file: Expected output for solution file (Prob(xx).out.txt)
    :param solution_file: Solution to Code Quest problem (Prob(xx).py)
    :return: No return: AssertionError raised if the expected output is
            incorrect, otherwise None.
    """

    # get logger and log arguments
    logger = logging.getLogger()
    logger.info('Solution file: "{}"'.format(solution_file))
    for file_name, file in (("Input", in_file), ("Expected out", out_file)):
        with open(file, 'r') as f:
            # reading the input in as lines makes it easier to work with
            # the out files have \r in them at the end of every newline
            # remove them because they are annoying and break correct
            # solutions
            f_contents = f.read().replace('\r', '').splitlines(True)
            logger.debug('{} file contents:\n{!r}'.format(file_name,
                                                          f_contents))
            if file == out_file:  # we want to save this for later
                expected_out = f_contents
    # in_file and solution_file must be in the same directory, so if they
    # aren't then create a temporary directory and move them both there
    if os.path.dirname(in_file) != os.path.dirname(solution_file):
        # define tmpdir outside of manager, so the directory isn't destroyed
        tmpdir = tempfile.TemporaryDirectory()
        with tempfile.TemporaryDirectory() as tmpdirname:
            for file in (in_file, out_file):
                shutil.copyfile(file, tmpdirname)
            in_file = "{}/{}".format(os.path.basename(in_file), tmpdirname)
            solution_file = "{}/{}".format(os.path.basename(solution_file),
                                           tmpdirname)

    # run the solution file using subprocess and then catch its output
    path_to_python = sys.executable
    logger.info("Using python interpreter at: '{}'".format(path_to_python))
    logger.info(
        "Executing solution file '{}'".format(os.path.basename(solution_file))
    )
    p = subprocess.Popen('"{}" {}'.format(path_to_python, solution_file),
                         shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    # returned from the read is a bytes string so decode it.
    out, err = (x.decode('utf-8') for x in p.communicate())
    if len(err) != 0:  # if an error was raised
        raise Exception(
            "An error occurred while executing '{}': '{}'".format(
                os.path.basename(solution_file), err)
        )
    else:
        out = out.replace('\r', '').splitlines(True)
        logger.debug('Got output:\n{!r}'.format(out))

        # find differences between retrieved output and expected output
        logger.info("Comparing output to expected output.")
        diffs = difflib.Differ().compare(out, expected_out)
        for line_no, diff in enumerate(diffs, 1):  # starts coutning line number at 1

            if not diff.startswith(" "):  # if the lines differ in some way:
                error_file = in_file.replace("in", "error")
                logger.error(
                    "Difference found at line {}, writing output to disk " \
                    "at: {}".format(line_no, error_file)
                )

                with open(error_file, 'w') as f:
                    f.write(''.join(out))

                """
                it's worth mentioning that whenever a difference is found
                using difflib this format is used:
                ' - (output from solution)'
                ' ? (location of difference)'
                ' + (expected output)'
                NOTE: (sometimes the ? and + lines are switched)
                In the below error, all spaces in the + and ? lines are
                replaced with ^s for readability
                """
                raise AssertionError(
                    "Solution '{}' failed at line {}: {!r} (difference: " \
                    " {!r}, expected: {!r}). Wrote incorrect output " \
                    "to {}".format(
                        os.path.basename(solution_file), line_no, diff,
                        next(diffs).replace(" ", "^"),
                        next(diffs).replace(" ", "^"),
                        error_file
                    )
                )
        logger.info(
            "Success! {} passed".format(os.path.basename(solution_file))
        )


class TestSolutions(unittest.TestCase):
    pass


@log_func_decorator
def create_test_funcs(grouped_cq_files):
    """
    Creates the test functions that will be picked up by pytest in order
    to test the solutions to Code Quest problems. The test functions
    will be added as methods into the TestSolutions class.
    """

    def _create_test_method(cq_files):
        def check_solution_method(self):
            check_solution(*cq_files)
        return check_solution_method

    for prob_num, cq_files in grouped_cq_files.items():
        # in file, out file, solution file
        if len(cq_files) == 3:
            cq_files = sorted(cq_files)
            logging.getLogger().info(cq_files)

            setattr(
                TestSolutions, "test_prob{:02d}".format(prob_num), _create_test_method(cq_files)
            )


def main():
    cq_files = get_cq_files(os.getcwd())
    grouped = group_cq_files(cq_files)
    create_test_funcs(grouped)
    unittest.main()


if __name__ == "__main__":
    main()
