import sys

import click
import codecs
import redis

# from .build_licenses import build_spdx_licenses, is_keys_empty,get_url
from expression_parser.scan import Scanner
from spdx_license_matcher.computation import get_close_matches, get_matching_string
from spdx_license_matcher.difference import generate_diff, get_similarity_percent
from spdx_license_matcher.utils import colors, get_spdx_license_text

from dotenv import load_dotenv
import os


# load_dotenv()
#
# @click.command()
# @click.option('--text_file', '-f', required=True, help='The name of the file in which there is the text you want to match against the SPDX License database.')
# @click.option('--threshold', '-t', default=0.9, type = click.FloatRange(0.0, 1.0), help='Confidence threshold below which we just won"t consider it a match.', show_default=True)
# @click.option('--build/--no-build', default=False, help='Builds the SPDX license list in the database. If licenses are already present it will update the redis database.')
from spdx_license_matcher.build_licenses import is_keys_empty, build_spdx_licenses


def matcher(text_file, threshold, build):
    """SPDX License matcher to match license text against the SPDX license list using an algorithm which finds close matches. """

    # For python 3
    inputText = codecs.open(text_file, 'r', encoding='unicode_escape').read()
    print("input")
    # print(inputText)

    if build or is_keys_empty():
        click.echo('Building SPDX License List. This may take a while...')
        build_spdx_licenses()

    r = redis.StrictRedis(host=os.environ.get(key="SPDX_REDIS_HOST", default="localhost"), port=6379, db=0)
    keys = list(r.keys())
    values = r.mget(keys)
    licenseData = dict(list(zip(keys, values)))
    # print('LICENSE1 DATA cache', licenseData)
    matches = get_close_matches(inputText, licenseData, threshold)
    matchingString = get_matching_string(matches, inputText)
    if matchingString == '':
        licenseID = max(matches, key=matches.get)
        spdxLicenseText = get_spdx_license_text(licenseID)
        similarityPercent = get_similarity_percent(spdxLicenseText, inputText)
        click.echo(colors('\nThe given license text matches {}% with that of {} based on Levenstein distance.'.format(
            similarityPercent, licenseID), 94))
        # differences = generate_diff(spdxLicenseText, inputText)
        # for line in differences:
        #     if line[0] == '+':
        #         line = colors(line, 92)
        #     if line[0] == '-':
        #         line = colors(line, 91)
        #     if line[0] == '@':
        #         line = colors(line, 90)
        #     click.echo(line)
    else:
        click.echo(colors(matchingString, 92))

import diff_match_patch as dmp_module



a = '''There are two things that are more difficult than making an after-dinner speech: climbing a wall which is leaning toward you and kissing a girl who is leaning away from you.'''

b = '''`Churchill` talked about climbing a wall which is leaning toward you and kissing a woman who is leaning away from you.'''

# dmp = dmp_module.diff_match_patch()
# print(dmp)
# diff = dmp.patch_make(a, b)
# print(diff)
# # Result: [(-1, "Hell"), (1, "G"), (0, "o"), (1, "odbye"), (0, " World.")]
# dmp.diff_cleanupSemantic(diff)
# # Result: [(-1, "Hello"), (1, "Goodbye"), (0, " World.")]
# print(diff)
#
# print(generate_diff(a, b))
# print('@@ -1,84 +1,28 @@ -There are two things that are more difficult than making an after-dinner speech: +%60Churchill%60 talked about cli @@ -136,12 +80,13 @@ g a -girl +woman who')
# matcher("LICENSE1", 0.5, True)
# matcher("LICENSE2", 0.5, False)
'''
from spdx_license_matcher.matcher import matcher

i = 1
while i <= 10:
    matcher(f"LICENSE{i}", 0.86, False)
    
'''


def run():
    print('Run...')
    sys.stdout = open('log2', 'w')

    i = 2
    build = True
    while i <= 10:
        if i != 2:
            build = False

        matcher(f"LICENSE{i}", 0.86, build)
        i += 1

    sys.stdout.close()


s = Scanner()
# print(s.scan('GPL-2.0 OR MIT'))
print(s.scan('GPL-2.0 OR MIT AND MPL-2.0'))

License indexOf(E element, [int start = 0]);


var li = SPDXLicenseIdentifier();
var licenses = li.detect('./LICENSE', confidence:0.95); // {'licenses: 'MPL-2.0', 'confidence':96.67, 'type':'License ID', 'found': 1}
licenses = li.detectFromSourceCode(); // to detect from source code
li.rebuild(); // rebuilds cache


Detect method

Map detect (
String input,
[float confidence = 0.90]
)

Possible Outputs: