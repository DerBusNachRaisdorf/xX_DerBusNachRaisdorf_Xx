import os
import signal
import subprocess
from typing import Tuple
import utility.latex
import string


LEGAL_NON_ASCII: str = 'ßäÄöÖüÜ# \n\t.,:;/\\{-+^_}[]()?!=&%"\'$1234567890|<>`'


"""
Provides various functions and classes for markdown conversion.

TODO: add better documentation
TODO: add markdown qoute-block support
TODO: add better markdown error messages
"""

class MarkdownSyntxError(Exception):
    def __init__(self, error_message, markdown_error_line: str, begin: int, end: int):
        message: str = f'**Markdown Error:** {error_message}\n```\n{markdown_error_line}\n'
        for i in range(len(markdown_error_line)):
            if i >= begin and i < end:
                message += '^'
            else:
                message += ' '
        message += '\n```'
        super().__init__(message)


def get_line_at_char_index(text: str, index: int) -> Tuple[str, int]:
    LINELEN_MAX: int = 25 # maximum number of chracters in one line
    begin: int = index
    end: int = index
    while begin > 0 and index - begin + 4 <= LINELEN_MAX:
        """ find begin of line """
        if begin >= 1 and text[begin-1] == '\n':
            break
        begin -= 1
    while end <= len(text) and index - begin + end - index <= LINELEN_MAX:
        """ find end of line """
        if end < len(text) and text[end] == '\n':
            break
        end += 1
    return text[begin:end], begin


class DocumentElement:
    def to_latex(self) -> str:
        raise NotImplementedError


class Document:
    def __init__(self):
        self.__children: list[DocumentElement] = []

    def add_element(self, element: DocumentElement):
        self.__children.append(element)

    def add_heading(self, heading_level: int, content: str):
        self.add_element(Heading(heading_level, content))

    def to_latex(self) -> str:
        latex_code: str = utility.latex.LATEX_HEAD
        for document_element in self.__children:
            latex_code += document_element.to_latex()
        latex_code += utility.latex.LATEX_TAIL
        return latex_code


class Heading(DocumentElement):
    def __init__(self, heading_level: int = 1, children: list[DocumentElement] = []):
        self.__heading_level: int = heading_level
        self.__children = children

    def to_latex(self) -> str:
        children_latex: str = ''
        for child in self.__children:
            children_latex += child.to_latex()
        return utility.latex.make_heading(self.__heading_level, children_latex, True)

    @property
    def heading_level(self):
        return self.__heading_level

    @heading_level.setter
    def heading_level(self, value):
        if value in [1, 2, 3]:
            self.__heading_level = value

    @property
    def content(self):
        return self.__content

    @content.setter
    def content(self, value):
        if type(value) == type(str):
            self.__content = value


class TextFragment(DocumentElement):
    def __init__(self, text: str):
        self.__text = text

    def to_latex(self) -> str:
        return self.__text


class TextModifier(DocumentElement):
    def __init__(self, is_bold: bool = False, is_italic: bool = False, children: list[DocumentElement] = []):
        self.__children: list[DocumentElement] = children
        self.__is_bold = is_bold
        self.__is_italic = is_italic

    def add_element(self, element: DocumentElement):
        self.__children.append(element)

    def to_latex(self) -> str:
        children_latex: str = ''
        for child in self.__children:
            children_latex += child.to_latex()
        
        if self.__is_bold and self.__is_italic:
            return '\\textbf{\\textit{' + children_latex + '\}\}'
        elif self.__is_bold:
            return '\\textbf{' + children_latex + '}'
        elif self.__is_italic:
            return '\\textit{' + children_latex + '}'
        else:
            return children_latex


class MulitlineMath(DocumentElement):
    def __init__(self, math: str):
        self.__math = math

    def to_latex(self) -> str:
        return f'\n\[{self.__math}\]\n\n'


class InlineMath(DocumentElement):
    def __init__(self, math: str):
        self.__math = math

    def to_latex(self) -> str:
        return f'\({self.__math}\)'


def parse_markdown(markdown: str) -> list[DocumentElement]:
    """ check for illegal chars """
    illegal = 0
    try:
        illegal = next(i for i,j in enumerate(markdown) if j not in string.ascii_letters and j not in LEGAL_NON_ASCII)
    except:
        pass
    
    if markdown[illegal] not in string.ascii_letters and markdown[illegal] not in LEGAL_NON_ASCII:
        error_line, error_line_begin = get_line_at_char_index(markdown, illegal)
        raise MarkdownSyntxError(
            f'Illegal Character found! {markdown[illegal]}.', 
            error_line,
            illegal - error_line_begin,
            illegal + 1 - error_line_begin
        )

    result: list[DocumentElement] = []
    buffer: str = ''
    i: int = 0
    while i < len(markdown):
        if markdown[i] == '#':
            """ headings """
            heading_level: int = 0
            heading_text: str = ''
            while i < len(markdown) and markdown[i] == '#':
                """ get heading level """
                heading_level += 1
                i += 1
            while i < len(markdown) and markdown[i] == ' ':
                """ skip whitespaces """
                i += 1
            while i < len(markdown) and markdown[i] != '\n':
                """ get heading text """
                heading_text += markdown[i]
                i += 1
            """ append heading to latex document """
            heading_children: list[DocumentElement] = parse_markdown(heading_text)
            result.append(Heading(heading_level, heading_children))
        elif markdown[i] == '*' or markdown[i] == '_':
            if len(buffer) != 0:
                """ add buffered markdown as plain text """
                result.append(TextFragment(buffer))
                buffer = ''
            """ text modifier """
            token_begin_index: int = i # just for error throwing
            inner_markdown: str = ''
            char: str = markdown[i]
            num: int = 0
            while i < len(markdown) and markdown[i] == char:
                """ count number of *s or _s """
                num += 1
                i += 1
            while i < len(markdown) and markdown[i] != char:
                """ inner markdown """
                inner_markdown += markdown[i]
                i += 1
            closing_num: int = 0
            while i < len(markdown) and markdown[i] == char and closing_num < num:
                """ end text modifier """
                closing_num += 1
                i += 1
            if closing_num != num:
                """ missing a closing * or _ """
                error_line, error_line_begin = get_line_at_char_index(markdown, i)
                raise MarkdownSyntxError(
                    f'Expected {char}.', 
                    error_line,
                    token_begin_index - error_line_begin,
                    i - error_line_begin
                )
            """ parse inner markdown and add to document """
            result.append(
                TextModifier(
                    True if num == 2 or num == 3 else False, 
                    True if num == 1 or num == 3 else False,
                    parse_markdown(inner_markdown)
                )
            )
        elif markdown[i] == '$':
            if len(buffer) != 0:
                """ add buffered markdown as plain text """
                result.append(TextFragment(buffer))
                buffer = ''
            """ math """
            token_begin_index: int = i # just for error throwing
            i += 1
            multiline: bool = False
            math: str = ''
            if len(markdown) <= i+1:
                error_line, error_line_begin = get_line_at_char_index(markdown, i)
                raise MarkdownSyntxError(
                    f'Expected $.', 
                    error_line,
                    token_begin_index - error_line_begin,
                    i - error_line_begin
                )
            elif markdown[i] == '$':
                """ multiline math """
                multiline = True
                i += 1
            while i < len(markdown) and markdown[i] != '$':
                """ get math code """
                math += markdown[i]
                i += 1
            if multiline:
                if i+1 < len(markdown) and markdown[i+1] == '$':
                    """ multiline math must end with two $. """
                    i += 1
                else:
                    error_line, error_line_begin = get_line_at_char_index(markdown, i)
                    raise MarkdownSyntxError(
                        f'Expected $.', 
                        error_line,
                        token_begin_index - error_line_begin,
                        i - error_line_begin
                    )
            """ add math to result """
            if multiline:
                result.append(MulitlineMath(math))
            else:
                result.append(InlineMath(math))
        else:
            """ text """
            buffer += markdown[i]
        
        i += 1

    if len(buffer) != 0:
        """ add buffered markdown as plain text """
        result.append(TextFragment(buffer))
        buffer = ''

    return result


def read_markdown_document(markdown: str) -> Document:
    document: Document = Document()
    
    for document_elem in parse_markdown(markdown):
        document.add_element(document_elem)

    return document


class PdfLaTeXError(Exception):
    def __init__(self, pdflatex_exit_code: int, pdflatex_log: list[str]):
        self.pdflatex_exit_code: int = pdflatex_exit_code
        self.pdflatex_log: list[str] = pdflatex_log
        n = '\n'
        pdflatex_log_str: str = n.join(pdflatex_log)
        too_long: bool = False
        if len(pdflatex_log_str) >= 1000:
            too_long = True
            pdflatex_log_str = pdflatex_log_str[len(pdflatex_log_str)-1000:len(pdflatex_log_str)]
        error_message: str = f'**Error:** pdflatex exited with code {pdflatex_exit_code}.\n\n**Output:**\n```{pdflatex_log_str}```'
        if too_long:
            error_message += '\n\n**Output was longer than 1000 characters. Removed the first lines.**'
        super().__init__(error_message)


def markdown_to_pdf(md_path: str) -> str:
    """ Converts a Markdown document to a PDF document.

        texlive must be installed on the system for this to work.
    """
    latex_code: str = ''
    
    if os.path.isfile(md_path):
        """ read markdown file """
        md_file = open(md_path, "r")
        data = md_file.read()
        md_file.close()
        """ convert markdown to latex """
        latex_code = read_markdown_document(data).to_latex()
    else:
        """ markdown file does not exist """
        raise FileNotFoundError()
    
    with open(f'{md_path}.tex', "w") as latex_file:
        """ write latex file """
        latex_file.write(latex_code)
    
    """ convert latex file to pdf using pdflatex """
    cmd = ['pdflatex', '-halt-on-error', '-interaction=nonstopmode','--output-directory=tmp',  f'{md_path}.tex']
    
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        out = p.communicate()[0].decode("utf-8")
        err = p.communicate()[1].decode("utf-8")

        """ capture pdflatex output """
        #pdflatex_output: list[str] = []
        #for line in p.stdout:
        #    print(line)
        #    pdflatex_output.append(line)

        """ wait for pdflatex to finish """
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        print(f'pdflatex timed out.')
        print(out)
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        raise PdfLaTeXError(999, [out, err])

    exitcode: int = p.returncode

    if exitcode != 0:
        """ pdflatex error """
        raise PdfLaTeXError(exitcode, [out, err])

    return f'{md_path}.pdf'
