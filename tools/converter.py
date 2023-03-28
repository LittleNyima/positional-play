import argparse
import os
import yaml
from abc import ABCMeta


# --- Arguments --------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'source', type=str,
        help='Source file, should be a yaml file in correct format.'
    )
    parser.add_argument(
        'target', type=str,
        help='Target file, should be latex or html file.'
    )
    parser.add_argument(
        '--writer', type=str, required=True, choices=['latex', 'html'],
        help='Target file writer.'
    )
    return parser.parse_args()


# --- Utilities --------------------------------------------------------------
def strip_ext(filename):
    dirname = os.path.dirname(filename)
    basename = os.path.basename(filename)
    parts = basename.split('.')
    if len(parts) > 1:
        parts.pop(-1)
    return os.path.join(dirname, '.'.join(parts))


# --- Writers ----------------------------------------------------------------
class AbstractWriter(metaclass=ABCMeta):
    def __init__(self, target):
        self.target = target
        self.stream = None

    def __enter__(self):
        self.stream = open(self.target, 'w', encoding='utf-8')
        return self

    def __exit__(self, *_):
        if not self.stream.closed:
            self.stream.close()

    def write(self, k, v, **kwargs):
        write_fn = self.__getattribute__(k)
        write_fn(v, **kwargs)

    def new_line(self):
        self.stream.write('\n\n')


class LatexWriter(AbstractWriter):
    def blockquote(self, content):
        s = f'\\begin{{quote}}\n{content}\n\\end{{quote}}'
        self.stream.write(s)
        self.new_line()

    def h1(self, content):
        s = f'\\chapter{{{content}}}'
        self.stream.write(s)
        self.new_line()

    def h2(self, content):
        s = f'\\section{{{content}}}'
        self.stream.write(s)
        self.new_line()

    def h3(self, content):
        s = f'\\subsection{{{content}}}'
        self.stream.write(s)
        self.new_line()

    def h4(self, content):
        s = f'\\subsubsection{{{content}}}'
        self.stream.write(s)
        self.new_line()

    def h5(self, content):
        s = f'\\paragraph{{{content}}}'
        self.stream.write(s)
        self.new_line()

    def h6(self, content):
        s = f'\\subparagraph{{{content}}}'
        self.stream.write(s)
        self.new_line()

    def include(self, content):
        s = f'\\input{{{strip_ext(content)}.tex}}'
        self.stream.write(s)
        self.new_line()

    def p(self, content):
        self.stream.write(content)
        self.new_line()


class HtmlWriter(AbstractWriter):
    pass


def get_writer_class(name):
    if name == 'latex':
        return LatexWriter
    elif name == 'html':
        return HtmlWriter


# --- Parse -------------------------------------------------------------------
def parse_item(item):
    assert isinstance(item, dict), 'Instance must be dict!'
    kwargs = dict()
    for k in list(item.keys()):
        if k.startswith('_'):
            kwargs[k[1:]] = item[k]
            del item[k]
    assert len(item) == 1, 'There must be a unique tag!'
    k = list(item.keys())[0]
    return k, item[k], kwargs


if __name__ == '__main__':
    args = parse_args()

    with open(args.source, 'r', encoding='utf-8') as fp:
        content = yaml.load(fp, yaml.SafeLoader)
    assert isinstance(content, list), 'Content must be List[Dict]!'

    writer_cls = get_writer_class(args.writer)

    with writer_cls(args.target) as writer:
        for item in content:
            k, v, kwargs = parse_item(item)
            writer.write(k, v, **kwargs)
