---
# Leave the homepage title empty to use the site title
title: ""
date: 2022-10-24
type: landing

design:
  # Default section spacing
  spacing: "6rem"

sections:
  - block: resume-biography-3
    content:
      # Choose a user profile to display (a folder name within `content/authors/`)
      username: admin
      text: ""
      # Show a call-to-action button under your biography? (optional)
      button:
        text: Download CV
        url: uploads/resume.pdf
    design:
      css_class: dark
      background:
        color: black
        image:
          # Add your image background to `assets/media/`.
          filename: alternating-arrowhead.svg
          filters:
            brightness: 1.0
          size: cover
          position: center
          parallax: false
  - block: features
    id: research-pillars
    content:
      title: Research
      subtitle: Three pillars, one thesis
      items:
        - name: Learning constitutive behavior
          icon: brain
          icon_pack: fas
          description: Physics-constrained machine learning for quasibrittle constitutive relations.
        - name: Modeling fracture and localization
          icon: bolt
          icon_pack: fas
          description: Smooth crack band and sprain-energy formulations for damage localization.
        - name: Quantifying failure risk
          icon: chart-line
          icon_pack: fas
          description: Probabilistic modeling and scale effects to predict structural failure.
        - name: Subsurface fracture and CO2 storage
          icon: water
          icon_pack: fas
          description: Multiphysics models of hydraulic fracture branching for carbon sequestration.
    design:
      columns: '4'
  - block: markdown
    id: current-work
    content:
      title: Current Work
      subtitle: ''
      text: |-
        - Mechanics-informed constitutive learning for quasibrittle materials
        - Machine learning surrogates for material failure models
        - Open to collaboration on fracture mechanics, risk assessment and ML for materials science
    design:
      columns: '1'
  - block: markdown
    content:
      title: '📚 My Research'
      subtitle: ''
      text: |-
        The broad objective of my research plan is to advance the state-of-the-art in fracture mechanics and probabilistic modeling to enhance material failure prediction and structural risk assessment. I intend to employ modern high-performance computing, statistical and machine learning tools to address critical challenges in these areas by focusing on (i) the development of innovative computational models for accurate failure analysis, and (ii) the integration of uncertainties in material behavior and loading conditions.
        
        Please reach out to collaborate! 😃
    design:
      columns: '1'
  - block: collection
    id: papers
    content:
      title: Featured Publications
      filters:
        folders:
          - publication
        featured_only: true
    design:
      view: article-grid
      columns: 2
  - block: collection
    content:
      title: Recent Publications
      text: ""
      filters:
        folders:
          - publication
        exclude_featured: false
    design:
      view: citation
---
