#!/usr/bin/python

import Parser


class Interpreter:
    def __init__(self, file):
        self.file = file

    def run(self):
        self.parser = Parser.Parser(self.file)
        # parse the text
        if self.parser.parse():
            try:
                # interprete the parsed sequence of modules
                self.parser.moduleSequence().execute({})
            except RuntimeError as  error:
                print(error)



if __name__ == '__main__':

    input_file = "tests/script1"
    interpreter = Interpreter(input_file)
    interpreter.run()
    