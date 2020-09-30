import Parser
import argparse

class Interpreter:
    def __init__(self, input_file, output_dir):
        self.input_file = input_file
        self.output_dir = output_dir

    def run(self):
        self.parser = Parser.Parser(self.input_file)
        # parse the text
        if self.parser.parse():
            try:
                # interprete the parsed sequence of modules
                self.parser.moduleSequence().execute({}, output_dir)
            except RuntimeError as error:
                print(error)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', metavar='path', required=True,
                        help='The path to the input file to parse.')
    parser.add_argument('--output_dir', metavar='path', required=True,
                        help='The path to the output directory to dump the rendered images.')
    args = parser.parse_args()
    input_file = args.input_file
    output_dir = args.output_dir
    interpreter = Interpreter(input_file, output_dir)
    interpreter.run()