---
title: Smooth Lagrangian Crack Band Model Based on Spress-Sprain Relation and Lagrange
  Multiplier Constraint of Displacement Gradient
authors:
- Anh Tay Nguyen
- Houlin Xu
- Karel Matouš
- Zdeněk P. Bažant
date: '2023-11-01'
publishDate: '2025-01-17T00:43:50.197718Z'
publication_types:
- article-journal
publication: '*Journal of Applied Mechanics*'
doi: 10.1115/1.4063896
abstract: A preceding 2023 study argued that the resistance of a heterogeneous material
  to the curvature of the displacement field is the most physically realistic localization
  limiter for softening damage. The curvature was characterized by the second gradient
  of the displacement vector field, which includes the material rotation gradient,
  and was named the “sprain” tensor, while the term “spress” is here proposed as the
  force variable work-conjugate to “sprain.” The partial derivatives of the associated
  sprain energy density yielded in the preceeding study, sets of curvature resisting
  self-equilibrated nodal sprain forces. However, the fact that the sprain forces
  had to be applied on the adjacent nodes of a finite element greatly complicated
  the programming and extended the simulation time in a commercial code such as abaqus
  by almost two orders of magnitude. In the present model, Smooth Lagrangian Crack
  Band Model (slCBM), these computational obstacles are here overcome by using finite
  elements with linear shape functions for both the displacement vector and for an
  approximate displacement gradient tensor. A crucial feature is that the nodal values
  of the approximate gradient tensor are shared by adjacent finite elements. The actual
  displacement gradient tensor calculated from the nodal displacement vectors is constrained
  to the approximate displacement gradient tensor by means of a Lagrange multiplier
  tensor, either one for each element or one for each node. The gradient tensor of
  the approximate gradient tensor then represents the approximate third-order displacement
  curvature tensor, or Hessian of the displacement field. Importantly, the Lagrange
  multiplier behaves as an externally applied generalized moment density that, similar
  to gravity, does not affect the total strain-plus-sprain energy density of material.
  The Helmholtz free energy of the finite element and its associated stiffness matrix
  are formulated and implemented in a user’s element of abaqus. The conditions of
  stationary values of the total free energy of the structure with respect to the
  nodal degrees-of-freedom yield the set of equilibrium equations of the structure
  for each loading step. One- and two-dimensional examples of crack growth in fracture
  specimens are given. It is demonstrated that the simulation results of the three-point
  bend test are independent of the orientation of a regular square mesh, capture the
  width variation of the crack band, the damage strain profile across the band, and
  converge as the finite element mesh is refined.
links:
- name: URL
  url: https://doi.org/10.1115/1.4063896
---
