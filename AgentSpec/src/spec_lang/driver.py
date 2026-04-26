import sys
from antlr4 import *
from AgentSpecLexer import AgentSpecLexer
from AgentSpecParser import AgentSpecParser

def main(argv):
    input_stream = FileStream(argv[1])
    lexer = AgentSpecLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = AgentSpecParser(stream)

    tree = parser.program()
    print(tree.toStringTree(recog=parser))

if __name__ == '__main__':
    main(sys.argv)