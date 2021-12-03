import os
import re

licenses = []
exceptions = ['h', 'linking-exception', 'some']
for file in os.listdir("../licenses"):
    if file.endswith(".txt"):
        licenses.append(file.split('.txt')[0])

print(len(licenses))

#   .concat(require('spdx-license-ids'))
#   .concat(require('spdx-license-ids/deprecated'))
# var exceptions = require('spdx-exceptions')


class Scanner:
    index = 0
    source = ''

    def hasMore(self):
        return self.index < len(self.source)

    # // `value` can be a regexp or a string.
    # // If it is recognized, the matching source string is returned and
    # // the index is incremented. Otherwise `undefined` is returned.
    def read(self, value, regex=True):
        print('value', value)
        if regex:
            chars = self.source[self.index:]
            print('chars', chars)
            match = re.search(value, chars)
            if match:
                print(match)
                self.index += len(match.group())
                return match.group()
        else:
            # index can throw error if not string not found
            try:
                if self.source.index(value, self.index) == self.index:
                    self.index += len(value)
                    return value
            except:
                return None

    def skipWhitespace(self):
        self.read(r'^(\s+)')

    def operator(self):
        print('Operator')
        string = None
        possibilities = ['WITH', 'AND', 'OR', '(', ')', ':', '+']
        i = 0
        while i < len(possibilities):
            string = self.read(possibilities[i], regex=False)
            if string:
                break
            i += 1
            print(i)

        if string == '+' and self.index > 1 and self.source[self.index - 2] == ' ':
            raise Exception('Space before `+`')  #

        #  return string and {
        if not string:
            return None

        return {
            'type': 'OPERATOR',
            'string': string
        }

    def idstring(self):
        return self.read(r'[a-zA-Z0-9-.]+')

    def expectIdstring(self):
        string = self.idstring()
        if not string:
            raise Exception('Expected idstring at offset ' + str(self.index))
        return string

    def documentRef(self):
        print('documentref')
        if self.read('DocumentRef-', regex=False):
            string = self.expectIdstring()
            return {'type': 'DOCUMENTREF', 'string': string}

    def licenseRef(self):
        print('licenseRef')
        if self.read('LicenseRef-', regex=False):
            string = self.expectIdstring()
            return {'type': 'LICENSEREF', 'string': string}

    def identifier(self):
        print('identifier')
        begin = self.index
        string = self.idstring()
        print(string)

        try:
            if licenses.index(string) > 0:
                return {
                    'type': 'LICENSE',
                    'string': string
                }
        except:
            try:
                if exceptions.index(string) > 0:
                    return {
                        'type': 'EXCEPTION',
                        'string': string
                    }
            except:
                raise Exception('fuck')

        self.index = begin
        return None

        # // Tries to read the next token. Returns `undefined` if no token is
        # // recognized.

    def parseToken(self):
        print('parseToken')
        # Ordering matters
        token = self.operator()
        print('what? ', token)
        if token:
            return token

        token = self.documentRef()
        if token:
            return token

        token = self.licenseRef()
        if token:
            return token

        token = self.identifier()
        if token:
            return token
        #
        # return (
        #         self.operator() or
        #         self.documentRef() or
        #         self.licenseRef() or
        #         self.identifier()
        # )

    def scan(self, source):
        self.source = source
        tokens = []
        while self.hasMore():
            self.skipWhitespace()
            if not self.hasMore():
                break

            token = self.parseToken()
            if not token:
                raise Exception('Unexpected `' + source[self.index] +
                                '` at offset ' + str(self.index))

            tokens.append(token)
        return tokens
