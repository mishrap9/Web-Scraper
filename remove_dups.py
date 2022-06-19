import codecs


def dedupe(input_file, output_file):
    with codecs.open(input_file, 'r', encoding='utf-8', errors='ignore') as input:
        new_lines = []
        for line in input:
            line = line.strip()
            if line not in new_lines:
                new_lines.append(line)
    with codecs.open(output_file, 'w', encoding='utf-8', errors='ignore') as output:
        output.write('\n'.join(new_lines))


dedupe('all_output.txt', 'output.txt')

