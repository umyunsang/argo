#set document(
  title: "장기 자율 연구개발을 위한 대규모 언어모델 에이전트 하네스의 설계와 평가",
  author: "엄윤상",
)
#set text(
  font: ("Times New Roman", "AppleMyungjo"),
  size: 10.5pt,
  lang: "ko",
  top-edge: 0.8em,
  bottom-edge: -0.2em,
)
#set par(justify: true, leading: 1em, spacing: 1em, first-line-indent: 1em)
#set page(
  paper: "a4",
  columns: 1,
  margin: (left: 30mm, right: 29mm, top: 32mm, bottom: 26mm),
  footer: context align(center, text(size: 10pt, counter(page).display("- 1 -"))),
)
#v(28mm)
#align(center)[
  #set par(first-line-indent: 0pt, justify: false, leading: 0.3em)
  #text(size: 16pt)[장기 자율 연구개발을 위한\
  대규모 언어모델 에이전트 하네스의 설계와 평가]
  #v(15mm)
  #text(size: 15.7pt)[Design and evaluation of an LLM agent harness\
  for long-horizon autonomous R&D]
  #v(9mm)
]
#show heading.where(level: 1): heading => block(
  width: 100%, above: 1.3em, below: 0.8em,
  align(center, text(size: 12pt, weight: "bold", heading.body)),
)
#show heading.where(level: 2): heading => block(
  width: 100%, above: 1em, below: 0.6em,
  text(size: 10.5pt, weight: "bold", heading.body),
)
#show figure.where(kind: "quarto-float-fig"): set figure(placement: none, gap: 0.5em)
#show figure.where(kind: "quarto-float-tbl"): set figure(placement: none, gap: 0.5em)
#show figure.where(kind: "quarto-float-tbl"): set text(size: 9.5pt)
#show figure.caption: set text(size: 10pt)
#show figure.caption: set align(left)
#show figure.caption: set par(first-line-indent: 0pt, justify: false)
#set figure.caption(separator: [. ])
#set table(stroke: 0.45pt, fill: none, inset: (x: 5pt, y: 4pt))
#show bibliography: set text(size: 9.5pt)
#show bibliography: set par(first-line-indent: 0pt, hanging-indent: 1.5em)
#show bibliography: entry => {
  show regex("W\\.-tau Yih"): [W.-T. Yih]
  entry
}
