---
title: "Sprain energy consequences for damage localization and fracture mechanics"
authors:
- admin
- Anh Tay Nguyen
- Zdeněk P. Bažant
date: "2024-09-26T00:00:00Z"
doi: "https://doi.org/10.1073/pnas.2410668121"

# Schedule page publish date (NOT publication's date).
publishDate: "2024-09-26T00:00:00Z"

# Publication type.
# Accepts a single type but formatted as a YAML list (for Hugo requirements).
# Enter a publication type from the CSL standard.
publication_types: ["article-journal"]

# Publication name and optional abbreviated publication name.
publication: "*The Proceedings of the National Academy of Sciences*121 (40) e2410668121"
publication_short: "PNAS"

abstract: The 2023 smooth Lagrangian Crack-Band Model (slCBM), inspired by the 2020 invention of the gap test, prevented spurious damage localization during fracture growth by introducing the second-gradient of the displacement field vector, named the `sprain', as the localization limiter. The key idea was that, in the finite element (FE) implementation, the displacement vector and its gradient should be treated as independent fields with the lowest (C_0) continuity, constrained by a second-order Lagrange multiplier tensor. Coupled with a realistic constitutive law for triaxial softening damage, such as microplane model M7, the known limitations of the classical Crack Band Model (CBM) were eliminated. Here we show that the slCBM closely reproduces the size effect revealed by the gap test at various crack-parallel stresses. To describe it, we present an approximate corrective formula, although a strong loading-path dependence limits its applicability. Except for the rare case of zero crack-parallel stresses, the fracture predictions of the line crack models (LEFM, phase-field, XFEM, cohesive crack models) can be as much as 100\% in error. We argue that the localization limiter concept must be extended by including the resistance to material rotation gradients. We also show that, without this resistance, the existing strain-gradient damage theories may predict a wrong fracture pattern and have, for Mode II and III fractures, a load capacity error as much as 55%. Finally, we argue that the crack-parallel stress effect must occur in all materials, ranging from concrete to atomistically sharp cracks in crystals.

# Summary. An optional shortened abstract.
#summary: Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis posuere tellus ac convallis placerat. Proin tincidunt magna sed ex sollicitudin condimentum.

tags:
- smooth Crack Band Model
featured: false

# links:
# - name: ""
#   url: ""
url_pdf: http://arxiv.org/pdf/1512.04133v1
#url_code: 'https://github.com/HugoBlox/hugo-blox-builder'
url_dataset: ''
url_poster: ''
url_project: ''
url_slides: ''
url_source: ''
url_video: ''

# Featured image
# To use, add an image named `featured.jpg/png` to your page's folder. 
image:
  caption: 'Demonstration of sCBM'
  focal_point: ""
  preview_only: false

# Associated Projects (optional).
#   Associate this publication with one or more of your projects.
#   Simply enter your project's folder or file name without extension.
#   E.g. `internal-project` references `content/project/internal-project/index.md`.
#   Otherwise, set `projects: []`.
projects: []

# Slides (optional).
#   Associate this publication with Markdown slides.
#   Simply enter your slide deck's filename without extension.
#   E.g. `slides: "example"` references `content/slides/example/index.md`.
#   Otherwise, set `slides: ""`.
slides: example
---

{{% callout note %}}
Click the *Cite* button above to demo the feature to enable visitors to import publication metadata into their reference management software.
{{% /callout %}}

{{% callout note %}}
Create your slides in Markdown - click the *Slides* button to check out the example.
{{% /callout %}}

Add the publication's **full text** or **supplementary notes** here. You can use rich formatting such as including [code, math, and images](https://docs.hugoblox.com/content/writing-markdown-latex/).
