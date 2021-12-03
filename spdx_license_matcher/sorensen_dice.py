import timeit

import diff_match_patch as dmp_module


# diffRatio calculates the ratio of the length of s1 and s2, returned as a
# percentage of the length of the longer string. E.g., diffLength("abcd", "e")
# would return 0.25 because "e" is 25% of the size of "abcd". Comparing
# strings of equal length will return 1.
from spdx_license_matcher.difference import get_similarity_percent


def diffRatio(s1, s2):
    x, y = len(s1), len(s2)
    if x == 0 and y == 0:
        # // Both strings are zero length
        return 1.0

    if x < y:
        return float(x) / float(y)

    return float(y) / float(x)


# // unknownTextLength returns the length of the unknown text based on the diff range.
def unknownTextLength(unknown, diffs):
    # print('unknownTextLength diffs', diffs)
    last = len(diffs) - 1
    while last >= 0:
        # print(diffs[last][0])
        if diffs[last][0] == dmp_module.diff_match_patch.DIFF_EQUAL:
            break

        last -= 1

    ulen = 0
    i = 0
    while i < last + 1:
        if diffs[i][0] == dmp_module.diff_match_patch.DIFF_EQUAL or diffs[i][
            0] == dmp_module.diff_match_patch.DIFF_DELETE:
            ulen += len(diffs[i][1])

        i += 1
    # print('unknownTextLength', ulen)
    return ulen


# // diffRangeEnd returns the end index for the "Diff" objects that constructs
# // (or nearly constructs) the "known" value.
def diffRangeEnd(known, diffs):
    seen = ''
    end = 0
    while end < len(diffs):
        if seen == known:
            # Once we've constructed the "known" value, then we've
            # reached the point in the diff list where more
            # "Diff"s would just make the Levenshtein Distance
            # less valid. There shouldn't be further "DiffEqual"
            # nodes, because there's nothing further to match in
            # the "known" text.
            break

        if diffs[end][0] == dmp_module.diff_match_patch.DIFF_EQUAL or diffs[end][
            0] == dmp_module.diff_match_patch.DIFF_INSERT:
            seen += diffs[end][1]

        end += 1

    return end


def confidencePercentage(ulen, klen, distance):
    if ulen == 0 and klen == 0:
        return 1.0

    # print('case', distance > ulen and distance > klen)
    if ulen == 0 or klen == 0 or (distance > ulen and distance > klen):
        # print('here')
        return 0.0

    return 1.0 - float(distance) / float(max(ulen, klen))


def levDist(unknown, known):
    # print('length', len(unknown), len(known))

    if len(known) == 0 or len(unknown) == 0:
        # print('levDist 0 this')
        # print(f"Zero-sized texts in Levenshtein Distance algorithm: known=={len(known)}, unknown=={len(unknown)}")
        # print('known', known)
        # print('unknown', unknown)
        return 0.0

    # diffs = dmp.DiffMain(unknown, known, false)
    dmp = dmp_module.diff_match_patch()
    diffs = dmp.diff_main(unknown, known, checklines=False)
    end = diffRangeEnd(known, diffs)

    distance = dmp.diff_levenshtein(diffs[:end])
    # print('dis', distance)
    return confidencePercentage(unknownTextLength(unknown, diffs), len(known), distance)


# Code from https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Dice%27s_coefficient
def get_dice_coefficient(a_license, b_license, type):
    """Sorensen dice coefficient may be calculated for two strings,
    x and y for the purpose of string similarity measure. Dice coefficient
    is defined as 2nt/(na + nb), where nt is the number of character bigrams
    found in both strings, na is the number of bigrams in string a and nb
    is the number of bigrams in string b.

    Arguments:
        a_license {string} --  Normalized license text a.
        b_license {string} -- Normalized license text b.

    Return:
        float -- A statistic used to gauge the similarity of two license texts.
    """
    if type == 1:
        start = timeit.timeit()
        r = levDist(a_license, b_license)
        end = timeit.timeit()
        print('lapse', end - start, r)
        return r

    if type == 2:
        start = timeit.timeit()
        r = get_similarity_percent(a_license, b_license)
        end = timeit.timeit()
        print('lapse', end - start, r)
        return r/100
    # dmp = dmp_module.diff_match_patch()
    # diff = dmp.diff_main(a_license, b_license)
    #
    # # dmp.diff_cleanupSemantic(diff)
    #
    # dmp = dmp.diff_levenshtein(diff)
    # print(dmp, dmp / 100)
    # return dmp / 100

    start = timeit.timeit()
    # Case for empty license text
    if not len(a_license) or not len(b_license):
        return 0.0

    # Case for true duplicates
    if a_license == b_license:
        return 1.0

    # If a != b, and a or b are single chars, then they can't possibly match
    if len(a_license) == 1 or len(b_license) == 1:
        return 0.0

    # Create bigrams
    a_bigram_list = [a_license[i:i + 2] for i in range(len(a_license) - 1)]
    b_bigram_list = [b_license[i:i + 2] for i in range(len(b_license) - 1)]
    # print('a bigram list', a_bigram_list)
    # print('b bigram list', b_bigram_list)

    a_bigram_list.sort()
    b_bigram_list.sort()
    # print('a sorted bigram', '->', a_bigram_list)

    # Assignments to save function calls
    lena = len(a_bigram_list)
    lenb = len(b_bigram_list)

    # Matches is used to count the matches between a_bigram_list and b_bigram_list
    matches = i = j = 0
    while (i < lena and j < lenb):
        if a_bigram_list[i] == b_bigram_list[j]:
            matches += 1
            i += 1
            j += 1
        elif a_bigram_list[i] < b_bigram_list[j]:
            i += 1
        else:
            j += 1

    score = float(2 * matches) / float(lena + lenb)
    # print('soren co dice score', score)
    end = timeit.timeit()
    print('lapse', end - start, score)
    return score
