#
# 'use strict'
#
# // The ABNF grammar in the spec is totally ambiguous.
# //
# // This parser follows the operator precedence defined in the
# // `Order of Precedence and Parentheses` section.

# module.exports = function (tokens) {
class Parser:
    index = 0
    tokens = []

    def hasMore(self):
        return self.index < len(self.tokens)

    def token(self):
        if self.hasMore():
            print(self.tokens[self.index])
            return self.tokens[self.index]
        else:
            return None

    def next(self):
        if not self.hasMore():
            raise Exception

        self.index += 1

    def parseOperator(self, operator):
        t = self.token()
        if t and t['type'] == 'OPERATOR' and operator == t['string']:
            self.next()
            return t['string']

    def parseWith(self):
        if self.parseOperator('WITH'):
            t = self.token()
            if t and t['type'] == 'EXCEPTION':
                self.next()
                return t['string']

            raise Exception('Expected exception after `WITH`')

    def parseLicenseRef(self):
        # TODO: Actually, everything is concatenated into one string for backward-compatibility but it could be better to return a nice structure.
        begin = self.index
        string = ''
        t = self.token()
        if t['type'] == 'DOCUMENTREF':
            self.next()
            string += 'DocumentRef-' + t['string'] + ':'
            if not self.parseOperator(':'):
                raise Exception('Expected `:` after `DocumentRef-...`')

        t = self.token()
        if t['type'] == 'LICENSEREF':
            self.next()
            string += 'LicenseRef-' + t['string']
            return {'license': string}

        self.index = begin

    def parseLicense(self):
        t = self.token()
        print(t)
        if t['type'] == 'LICENSE':
            self.next()
            node = {'license': t['string']}
            if self.parseOperator('+'):
                node['plus'] = True

            exception = self.parseWith()
            if exception:
                node['exception'] = exception

            return node

    def parseParenthesizedExpression(self):
        left = self.parseOperator('(')
        if not left:
            return

        expr = self.parseExpression()

        if not self.parseOperator(')'):
            raise Exception('Expected `)`')

        return expr

    def parseAtom(self):
        return (
                self.parseParenthesizedExpression() or
                self.parseLicenseRef() or
                self.parseLicense()
        )

    def makeBinaryOpParser(self, operator, nextParser):
        def parseBinaryOp():
            # print('================>', nextParser)

            if type(nextParser) != dict:
                left = nextParser()
            else:
                left = nextParser
            if not left:
                return

            if not self.parseOperator(operator):
                return left

            right = parseBinaryOp()
            if not right:
                raise Exception('Expected expression')

            return {
                'left': left,
                'conjunction': operator.lower(),
                'right': right
            }

        return parseBinaryOp()

    def parse(self, tokens):
        self.tokens = tokens
        # print(tokens)
        parseAnd = self.makeBinaryOpParser('AND', self.parseAtom)
        print('parseand', parseAnd)
        parseExpression = self.makeBinaryOpParser('OR', parseAnd)

        node = parseExpression
        print(node)
        if not node:
            raise Exception('Syntax error')

        return node

