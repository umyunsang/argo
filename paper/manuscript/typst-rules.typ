
#set text(font: ("AppleMyungjo", "Times New Roman"), size: 10.5pt, lang: "ko")
#set par(justify: true, leading: 1.15em, first-line-indent: 1.5em)
#set page(
  paper: "a4",
  margin: (x: 25mm, top: 25mm, bottom: 25mm),
  footer: align(center)[#text(size: 10pt)[\- #context counter(page).display() \-]]
)

// Title block matching template Page 2 (top of Page 1)
#align(center)[
  #v(0.5em)
  #text(size: 18pt, weight: "bold")[장기 자율 연구개발을 위한 대규모 언어모델 에이전트 하네스의 설계와 평가]
  #v(1.0em)
  #text(size: 13pt)[Design and evaluation of an LLM agent harness for long-horizon autonomous R&D]
  #v(1.0em)
  #text(size: 11pt)[엄 윤 상 (동아대학교 AI학과)]
  #v(1.5em)
]

// Level 1: Centered Bold Roman matching template Page 2 & 3
#show heading.where(level: 1): it => {
  let title_text = if it.body == [국문요약] [Abstract] else { it.body }
  block(
    width: 100%,
    align(center)[
      #v(1.6em)
      #text(size: 13pt, weight: "bold")[#title_text]
      #v(0.9em)
    ]
  )
}

// Level 2: Left-aligned Bold Arabic matching template Page 2
#show heading.where(level: 2): it => block(
  width: 100%,
  [
    #v(1.0em)
    #text(size: 11pt, weight: "bold")[#it.body]
    #v(0.5em)
  ]
)

// Level 3: Left-aligned Bold
#show heading.where(level: 3): it => block(
  width: 100%,
  [
    #v(0.8em)
    #text(size: 10.5pt, weight: "bold")[#it.body]
    #v(0.4em)
  ]
)

// Figure styling: image centered, caption centered below matching template Page 3
#show figure.where(kind: image): it => block(
  width: 100%,
  align(center)[
    #v(0.6em)
    #it.body
    #v(0.4em)
    #text(size: 10pt)[그림 #it.counter.display(it.numbering). #it.caption.body]
    #v(0.8em)
  ]
)

// Table styling: caption left-aligned above table, compact 8.5pt text, centered matching template Page 3
#show figure.where(kind: table): it => block(
  width: 100%,
  [
    #v(0.6em)
    #text(size: 9.5pt, weight: "bold")[표 #it.counter.display(it.numbering)  #it.caption.body]
    #v(0.25em)
    #align(center)[
      #set text(size: 8.5pt)
      #it.body
    ]
    #v(0.6em)
  ]
)

// Table rules: 3-line academic booktabs stroke style matching template Page 3
#set table(
  stroke: (x, y) => if y == 0 { (bottom: 1.2pt, top: 1.2pt) } else if y == 1 { (bottom: 0.8pt) } else { none },
  fill: none,
  inset: (x: 5pt, y: 3.5pt),
)

// Keyword block un-indented
#show "Keyword :": it => [
  #v(0.5em)
  #h(-1.5em)
  #text(size: 10pt)[#it]
]

// Reference entries hanging indent matching template Page 3
#show bibliography: set par(first-line-indent: 0pt, hanging-indent: 2em)
