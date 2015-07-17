# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import subprocess

import progressbar


def main(args):
    tests = subprocess.check_output(['testr', 'list-tests'])
    tests = tests.strip().split('\n')

    # find the first test
    i = 0
    for test in tests:
        i += 1
        if 'subunit.run' in test:
            break

    # remove everything up to the first test
    tests = tests[i:]

    isolated_tests = set()

    if args.expanded:
        # add all possible test modules, plus the individual tests
        for test in tests:
            path = test.split('.')
            for x in range(0, len(path)):
                isolated_tests.add('.'.join(path[0:x + 1]))
    else:
        # just use the individual tests
        isolated_tests = set(tests)

    failed_tests = dict()

    widgets = [
        progressbar.Percentage(),
        ' (',
        progressbar.Counter(),
        ' of %d) ' % len(isolated_tests),
        progressbar.Bar(),
        ' ',
        progressbar.ETA(),
    ]
    progress = progressbar.ProgressBar(
        widgets=widgets,
        maxval=len(isolated_tests))
    for test in progress(isolated_tests):
        try:
            subprocess.check_output(
                ['.tox/py27/bin/testr', 'run', test],
                # ['tox', '-e', 'py27', test],
                stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            failed_tests[test] = e.output
            with open('failed-%s' % test, 'w') as f:
                f.write(e.output)

    for test in sorted(failed_tests.keys()):
        print(test)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--expanded', action='store_true',
        help='Run all possible test modules in addition to the individual '
             'tests.')

    args = parser.parse_args()
    main(args)
