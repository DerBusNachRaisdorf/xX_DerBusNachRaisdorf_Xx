ILLEGAL_ALPHA: dict[str, str] = {
    'ü': 'ue',
    'ä': 'ae',
    'ö': 'oe',
    'ß': 'ss'
}

def make_heading(heading_level: int, content: str, link: bool = True) -> str:
    result: str = ''
    """ link """
    heading_link_name: str = __make_link_target_nake(content)
    if link:
        result += '\\hypertarget{' + heading_link_name + '}{%\n'
    """ heading itself """
    if heading_level == 1:
        result += '\\section{' + content + '}'
    elif heading_level == 2:
        result += '\\subsection{' + content + '}'
    else:
        result += '\\subsubsection{' + content + '}'
    """ link """
    if link:
        result += '\\label{' + heading_link_name + '}}\n'
    
    return result


def __make_link_target_nake(content: str) -> str:
    result: str = ''
    for c in content:
        c: str = c
        if c.isspace():
            result += '_'
        elif c.isalpha():
            if c.lower() in ILLEGAL_ALPHA.keys():
                result += ILLEGAL_ALPHA[c.lower()]
            else:
                result += c.lower()
    return result


LATEX_HEAD: str = """
% Options for packages loaded elsewhere
\\PassOptionsToPackage{unicode}{hyperref}
\\PassOptionsToPackage{hyphens}{url}
%
\\documentclass[
]{article}
\\author{}
\\date{}

\\usepackage{amsmath,amssymb}
\\usepackage{lmodern}
\\usepackage{iftex}
\\ifPDFTeX
  \\usepackage[T1]{fontenc}
  \\usepackage[utf8]{inputenc}
  \\usepackage{textcomp} % provide euro and other symbols
\\else % if luatex or xetex
  \\usepackage{unicode-math}
  \\defaultfontfeatures{Scale=MatchLowercase}
  \\defaultfontfeatures[\\rmfamily]{Ligatures=TeX,Scale=1}
\\fi
% Use upquote if available, for straight quotes in verbatim environments
\\IfFileExists{upquote.sty}{\\usepackage{upquote}}{}
\\IfFileExists{microtype.sty}{% use microtype if available
  \\usepackage[]{microtype}
  \\UseMicrotypeSet[protrusion]{basicmath} % disable protrusion for tt fonts
}{}
\\makeatletter
\\@ifundefined{KOMAClassName}{% if non-KOMA class
  \\IfFileExists{parskip.sty}{%
    \\usepackage{parskip}
  }{% else
    \\setlength{\\parindent}{0pt}
    \\setlength{\\parskip}{6pt plus 2pt minus 1pt}}
}{% if KOMA class
  \\KOMAoptions{parskip=half}}
\\makeatother
\\usepackage{xcolor}
\\IfFileExists{xurl.sty}{\\usepackage{xurl}}{} % add URL line breaks if available
\\IfFileExists{bookmark.sty}{\\usepackage{bookmark}}{\\usepackage{hyperref}}
\\hypersetup{
  hidelinks,
  pdfcreator={LaTeX via pandoc}}
\\urlstyle{same} % disable monospaced font for URLs
\\setlength{\\emergencystretch}{3em} % prevent overfull lines
\\providecommand{\\tightlist}{%
  \\setlength{\\itemsep}{0pt}\\setlength{\\parskip}{0pt}}
\\setcounter{secnumdepth}{-\\maxdimen} % remove section numbering
\\ifLuaTeX
  \\usepackage{selnolig}  % disable illegal ligatures
\\fi

\\begin{document}
"""

LATEX_TAIL: str = """
\\end{document}
"""