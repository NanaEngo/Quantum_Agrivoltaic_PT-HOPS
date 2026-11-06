%% iopart.cls --- IOP Publishing journal document class
%%
\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{iopart}[2008/01/21 v2.4 IOP Publishing journal document class]

\DeclareOption{10pt}{\def\iopt@fontsize{10pt}}
\DeclareOption{12pt}{\def\iopt@fontsize{12pt}}
\DeclareOption{11pt}{\def\iopt@fontsize{11pt}}
\DeclareOption{draft}{\PassOptionsToClass{draft}{article}}
\DeclareOption{final}{\PassOptionsToClass{final}{article}}
\DeclareOption{onecolumn}{\PassOptionsToClass{onecolumn}{article}}
\DeclareOption{twocolumn}{\PassOptionsToClass{twocolumn}{article}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}

\ExecuteOptions{12pt,onecolumn,final}
\ProcessOptions\relax

\LoadClass[12pt,a4paper]{article}

\RequirePackage{geometry}
\geometry{margin=2.5cm}

% IOP title and metadata definitions
\def\@shorttitle{}
\renewcommand{\title}[2][]{%
  \def\@shorttitle{#1}%
  \def\@title{#2}%
}

\def\address#1{\gdef\@address{#1}}
\def\@address{}
\def\ead#1{\gdef\@ead{#1}}
\def\@ead{}
\def\eads#1{\gdef\@eads{#1}}
\def\@eads{}
\def\pacs#1{\gdef\@pacs{#1}}
\def\@pacs{}
\def\submitto#1{\gdef\@submitto{#1}}
\def\@submitto{Quantum Science and Technology}

\def\keywords#1{\gdef\@keywords{#1}}
\def\@keywords{}

\renewcommand{\maketitle}{%
  \begin{center}%
    \let\footnote\thanks
    {\Large\bfseries \@title \par}%
    \vskip 1.5em%
    {\large
      \lineskip .5em%
      \begin{trivlist}\item[]\centering \@author\end{trivlist}%
    }%
    \vskip 1em%
    {\small \@address \par}%
    \ifx\@ead\@empty\else
      \vskip 0.5em%
      {\small E-mail: \texttt{\@ead}\par}%
    \fi
    \ifx\@eads\@empty\else
      \vskip 0.5em%
      {\small E-mail: \texttt{\@eads}\par}%
    \fi
    \ifx\@submitto\@empty\else
      \vskip 1em%
      {\small Submitted to: {\itshape \@submitto}\par}%
    \fi
  \end{center}%
  \par
  \vskip 1.5em
}

\renewenvironment{abstract}{%
  \vskip 1em
  \begin{center}%
    {\bfseries Abstract\vspace{-.5em}\vspace{0pt}}%
  \end{center}%
  \quotation
}{%
  \ifx\@keywords\@empty\else
    \vskip 1em
    \noindent{\it Keywords\/}: \@keywords\par
  \fi
  \endquotation
  \vskip 1.5em
}

\def\numrefs#1{}
\def\endnumrefs{}

\endinput
