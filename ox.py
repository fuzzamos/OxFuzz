#   Domato - main generator script
#   -------------------------------
#
#   Written and maintained by Ivan Fratric <ifratric@google.com>
#
#   Copyright 2017 Google Inc. All Rights Reserved.
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from __future__ import print_function
import os
import re
import random
import sys

from grammar import Grammar

_N_MAIN_LINES = 9
_N_EVENTHANDLER_LINES = 500

_N_ADDITIONAL_HTMLVARS = 0

_INTERNAL_TEMPLATE_PATH = '.\\ox_template.html'
_INTERNAL_SYNTAX_PATH = '.\\oxjs.txt'


def check_grammar(grammar):
    """Checks if grammar has errors and if so outputs them.

    Args:
      grammar: The grammar to check.
    """

    for rule in grammar._all_rules:
        for part in rule['parts']:
            if part['type'] == 'text':
                continue
            tagname = part['tagname']
            # print tagname
            if tagname not in grammar._creators:
                print('No creators for type ' + tagname)


def generate_new_sample(template,jsgrammar):
    """Parses grammar rules from string.

    Args:
      template: A template string.
      jsgrammar: Grammar for generating JS code.

    Returns:
      A string containing sample data.
    """

    result = template
    numlines = _N_MAIN_LINES
    result = result.replace(
            '<jsfuzzer>',
            jsgrammar._generate_code(numlines),
            1
        )

    return result

def generate_samples_internal(numbers):
    
    samples=[]

    f = open(_INTERNAL_TEMPLATE_PATH)
    template = f.read()
    f.close()
   
    jsgrammar = Grammar()
    err = jsgrammar.parse_from_file(_INTERNAL_SYNTAX_PATH)
   
    if err > 0:
        print('There were errors parsing grammar')
        return

    for i in range(numbers):
        result=generate_new_sample(template,jsgrammar)

        if result is not None:
            samples.append(result)
            print('Write sample No.'+str(i))

    return samples       


def generate_samples(grammar_dir, outfiles):
    """Generates a set of samples and writes them to the output files.

    Args:
      grammar_dir: directory to load grammar files from.
      outfiles: A list of output filenames.
    """

    f = open(os.path.join(grammar_dir, 'ox_template.html'))
    template = f.read()
    f.close()
   
    jsgrammar = Grammar()
    err = jsgrammar.parse_from_file(os.path.join(grammar_dir, 'oxjs.txt'))
   
    if err > 0:
        print('There were errors parsing grammar')
        return

    for outfile in outfiles:
        result = generate_new_sample(template,jsgrammar)

        if result is not None:
            print('Writing a sample to ' + outfile)
            try:
                f = open(outfile, 'w')
                f.write(result)
                f.close()
            except IOError:
                print('Error writing to output')


def get_option(option_name):
    for i in range(len(sys.argv)):
        if (sys.argv[i] == option_name) and ((i + 1) < len(sys.argv)):
            return sys.argv[i + 1]
        elif sys.argv[i].startswith(option_name + '='):
            return sys.argv[i][len(option_name) + 1:]
    return None


def main():

    fuzzer_dir = os.path.dirname(__file__)

    multiple_samples = False

    for a in sys.argv:
        if a.startswith('-out='):
            multiple_samples = True

    if '-out' in sys.argv:
        multiple_samples = True

    if multiple_samples:
        print('Running on ClusterFuzz')
        out_dir = get_option('-out')
        nsamples = int(get_option('-num'))
        print('Output directory: ' + out_dir)
        print('Number of samples: ' + str(nsamples))

        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        outfiles = []
        for i in range(nsamples):
            outfiles.append(os.path.join(out_dir, 'fuzz-' + str(i) + '.html'))

        generate_samples(fuzzer_dir, outfiles)

    elif len(sys.argv) > 1:
        outfile = sys.argv[1]
        generate_samples(fuzzer_dir, [outfile])

    else:
        print('Arguments missing')
        print("Usage:")
        print("\tpython ox.py <output file name>")
        print("\tpython ox.py -out <output directory> -num <number of output files>")


if __name__ == '__main__':
    main()
