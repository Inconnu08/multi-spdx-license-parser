import codecs
import os
import re
from pprint import pprint

import click
import redis

# load_dotenv()
#
# @click.command()
# @click.option('--text_file', '-f', required=True, help='The name of the file in which there is the text you want to match against the SPDX License database.')
# @click.option('--threshold', '-t', default=0.9, type = click.FloatRange(0.0, 1.0), help='Confidence threshold below which we just won"t consider it a match.', show_default=True)
# @click.option('--build/--no-build', default=False, help='Builds the SPDX license list in the database. If licenses are already present it will update the redis database.')
from expression_parser.main import parse_expression
from expression_parser.scan import Scanner
from spdx_license_matcher.build_licenses import is_keys_empty, build_spdx_licenses
from spdx_license_matcher.computation import get_close_matches, get_matching_string
from spdx_license_matcher.difference import get_similarity_percent
from spdx_license_matcher.utils import colors, get_spdx_license_text


# from .build_licenses import build_spdx_licenses, is_keys_empty,get_url

def matcher(text_file, threshold, build):
    """SPDX License matcher to match license text against the SPDX license list using an algorithm which finds close matches. """

    # For python 3
    inputText = codecs.open(text_file, 'r', encoding='unicode_escape').read()
    # print("input")
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


a = '''There are two things that are more difficult than making an after-dinner speech: climbing a wall which is leaning toward you and kissing a girl who is leaning away from you.'''

b = '''`Churchill` talked about climbing a wall which is leaning toward you and kissing a woman who is leaning away from you.'''

import diff_match_patch as dmp_module
dmp = dmp_module.diff_match_patch()
diff = dmp.diff_main(a, b)

dmp.diff_cleanupSemantic(diff)

dmp = dmp.diff_levenshtein(diff)

print(dmp)
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
    # sys.stdout = open('log2', 'w')

    i = 8
    build = True
    while i < 14:
        if i != 1:
            build = False
        print(i)
        matcher(f"./tests/LICENSE{i}", 0.8, build)
        i += 1

    # sys.stdout.close()


# run()


# str = "The rain in SPAIN stays mainly in the plain"
# # pattern = re.compile(r'\s+')
# # matches = pattern.match(str)
# # print(matches)
# # for match in matches:
# #     print(match)
# res = re.match(r'[\s]', str)
# print(res)
# text = 'gfgfdAAA1234ZZZuijjk'
#
# m = re.search('AAA(.+?)ZZZ', text)
# if m:
#     found = m.group(1)
#     print(found)
#
# m = re.search('(\s+)', str)
# if m:
#     print(m)
#     print(m.group())
#     # found = m.group(1)
#     print("found-", m.span()[1])
#
#
# m = re.search('[a-zA-Z0-9-.]+', '$$GPL-2.0%$&*1')
# if m:
#     print(m)
#     print(m.group())
#     # found = m.group(1)
#     print("found-", m.span()[1])
#
# m = re.search('Document', '$$GPL-2.0%Document$&*1')
# if m:
#     print(m)
#     print(m.group())
#     # found = m.group(1)
#     print("found-", m.span()[1])
#
#
# def a():
#     return 'A'
#
# def b():
#     return None
#
# def ab():
#     return (a() or b())
#
#
# print(ab())
#
scanner = Scanner()
# print(scanner.scan('GPL-2.0 OR MIT AND MPL-2.0'))
print(scanner.scan('MIT AND EPL-1.0+ OR MPL-2.0 WITH linking-exception'))
print(parse_expression('MIT AND EPL-1.0+ AND MPL-2.0 WITH linking-exception'))
