#set text(font: ("AppleMyungjo", "Times New Roman"), size: 10pt, lang: "ko")
#set par(justify: true, leading: 0.55em, first-line-indent: 1em)
#set page(paper: "a4", columns: 2, margin: (x: 25mm, top: 23mm, bottom: 23mm), footer: align(center)[#context counter(page).display()])
#set columns(gutter: 6mm)
#place(top + center, scope: "parent", float: true, clearance: 12pt)[
  #block(width: 160mm)[
    #set par(first-line-indent: 0pt, justify: false)
    #align(center)[
      #text(size: 17pt, weight: "bold")[장기 자율 연구개발을 위한\
      대규모 언어모델 에이전트 하네스의\
      설계와 평가]
      #v(0.7em)
      #text(size: 11pt)[Design and evaluation of an LLM agent harness for long-horizon autonomous R&D]
      #v(0.7em)
      #text(size: 11pt)[엄윤상]
      #v(0.7em)
      #text(size: 9pt)[중간 연구 원고 · 2026년 9월 5일 · 통합 효능 평가 전]
    ]
  ]
]
#show heading.where(level: 1): it => block(width: 100%, above: 1.2em, below: 0.7em, align(center, text(size: 12pt, weight: "bold", it.body)))
#show heading.where(level: 2): it => block(width: 100%, above: 0.9em, below: 0.5em, text(size: 10.5pt, weight: "bold", it.body))
#show figure.where(kind: "quarto-float-fig"): it => place(top + center, scope: "parent", float: true, clearance: 12pt)[
  #block(width: 160mm, breakable: false)[
    #align(center, it.body)
    #v(0.4em)
    #set par(first-line-indent: 0pt, justify: false)
    #text(size: 9.5pt)[그림 #it.counter.display(it.numbering). #it.caption.body]
  ]
]
#show figure.where(kind: "quarto-float-tbl"): it => place(top + center, scope: "parent", float: true, clearance: 12pt)[
  #block(width: 160mm, breakable: false)[
    #set par(first-line-indent: 0pt, justify: false)
    #text(size: 9.5pt, weight: "bold")[표 #it.counter.display(it.numbering). #it.caption.body]
    #v(0.35em)
    #set text(size: 9pt)
    #block(width: 100%, stroke: (top: 0.65pt, bottom: 0.65pt), inset: (top: 1pt, bottom: 1pt), it.body)
  ]
]
#set table(stroke: none, fill: none, inset: (x: 5pt, y: 4pt))
#show bibliography: set par(first-line-indent: 0pt, hanging-indent: 1.5em)
