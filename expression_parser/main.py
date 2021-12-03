from expression_parser.parse import Parser
from expression_parser.scan import Scanner


def parse_expression(source):
    scanner = Scanner()
    parser = Parser()
    return parser.parse(scanner.scan(source))

