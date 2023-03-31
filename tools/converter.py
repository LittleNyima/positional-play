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
class DeletableStream:
    def __init__(self, file, mode, encoding):
        self.stream = open(file=file, mode=mode, encoding=encoding)
        self.buffer = []
    
    def write(self, s):
        self.buffer.append(s)
    
    def flush(self):
        self.stream.write("".join(self.buffer))
        self.buffer.clear()
    
    def close(self):
        self.flush()
        self.stream.close()
    
    def backspace(self, n):
        while self.buffer and n > 0:
            if len(self.buffer[-1]) <= n:
                item = self.buffer.pop()
                n -= len(item)
            else:
                self.buffer[-1] = self.buffer[-1][:-n]
    
    @property
    def closed(self):
        return self.stream.closed


class AbstractWriter(metaclass=ABCMeta):
    def __init__(self, target):
        self.target = target
        self.stream = DeletableStream(self.target, 'w', encoding='utf-8')

    def __enter__(self):
        return self

    def __exit__(self, *_):
        if not self.stream.closed:
            self.stream.close()

    def write(self, k, v, **kwargs):
        if hasattr(self, k):
            write_fn = self.__getattribute__(k)
            write_fn(v, **kwargs)

    def new_line(self):
        self.stream.write('\n\n')


class LatexWriter(AbstractWriter):
    def backspace(self, n):
        self.stream.backspace(n)

    def blockquote(self, content):
        s = f'\\begin{{quote}}\n{content}\n\\end{{quote}}'
        self.stream.write(s)
        self.new_line()

    def chessboard(self, content):
        s = f'''\\chessboard[{content}]'''
        self.stream.write(s)
        self.new_line()

    def h1(self, content, unnumbered=False):
        asterisk = '*' if unnumbered else ''
        s = f'\\chapter{asterisk}{{{content}}}'
        self.stream.write(s)
        self.new_line()

    def h2(self, content, unnumbered=False):
        asterisk = '*' if unnumbered else ''
        s = f'\\section{asterisk}{{{content}}}'
        self.stream.write(s)
        self.new_line()

    def h3(self, content, unnumbered=False):
        asterisk = '*' if unnumbered else ''
        s = f'\\subsection{asterisk}{{{content}}}'
        self.stream.write(s)
        self.new_line()

    def h4(self, content, unnumbered=False):
        asterisk = '*' if unnumbered else ''
        s = f'\\subsubsection{asterisk}{{{content}}}'
        self.stream.write(s)
        self.new_line()

    def h5(self, content, unnumbered=False):
        asterisk = '*' if unnumbered else ''
        s = f'\\paragraph{asterisk}{{{content}}}'
        self.stream.write(s)
        self.new_line()

    def h6(self, content, unnumbered=False):
        asterisk = '*' if unnumbered else ''
        s = f'\\subparagraph{asterisk}{{{content}}}'
        self.stream.write(s)
        self.new_line()

    def include(self, content):
        s = f'\\input{{{strip_ext(content)}.tex}}'
        self.stream.write(s)
        self.new_line()

    def p(self, content):
        self.stream.write(content)
        self.new_line()
    
    def raw(self, content, lang='any'):
        if lang in ['any', 'latex']:
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
