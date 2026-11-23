# Two-letter and subgroup criteria for Aliabadi's Problems 7.4 and 7.6

The posing locator is Mohsen Aliabadi, *A nonabelian twist on differences of
bijections*, arXiv:2605.16478v2, Section 7, page 17.
The general singleton obstruction was proved by Korea Superintelligence Labs
(2026). The note develops its relation to arbitrary two-letter support,
exact permutation counts, and abelian-subgroup block decompositions, with
explicit product-one obstructions in dihedral and dicyclic groups and A4.
The constructions persist in their finite overgroups, including S3×K
for every finite K.
The two-letter formula has a classical circulant-permanent antecedent;
the subgroup decomposition follows from Erdős–Ginzburg–Ziv (1961).
The bibliography and coverage table give the exact scientific attributions.

## Scope of the literature comparison

Aliabadi's publications page, item 31, lists *Quotient-Realizable Multisets
in Finite Groups: Two-Valued Criteria and Enumeration* under Utilitas
Mathematica (2026):
https://mohsenmath88.wixsite.com/mohsenaliabadi/publications

Its full text and individual publication date are unavailable. Its title
indicates possible complete overlap with the two-letter criterion and exact
count; the theorem-level relationship is undetermined.
Donovan, Kenneth Johnson and Wanless, *Permanents and determinants of Latin
squares*, J. Combinatorial Designs 24 (2016), 132–148, first online
19 November 2014, describe two-symbol coefficients through symbol-cycle
lengths in their abstract:
https://doi.org/10.1002/jcd.21418
https://users.monash.edu.au/~iwanless/abstracts/perdetLS.html

Their full article is unavailable, so its exact specialization to the count
in the note remains undetermined. Both sources are credited as potentially
overlapping work. The criterion and count have self-contained proofs here;
neither novelty nor priority is asserted for them.

## Files

- `note.tex` and `note.pdf`: mathematical text and embedded bibliography.
- `metadata.json`: creators, license, sources and statement coverage.
- `verify.py`: standard-library Python 3 finite checks.
- `verification.json`: deterministic finite-check results.
- `SHA256SUMS`: hashes of the source files in `source.zip`.

## Build

Use Tectonic 0.17.0:

```sh
tectonic --untrusted note.tex
```

Or use a LaTeX distribution providing the packages named in `note.tex`:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography is embedded; BibTeX is unnecessary.

## Mathematical coverage

```sh
python3 verify.py --output verification-recomputed.json
cmp verification.json verification-recomputed.json
```

The checker exhausts 720 permutations of S3 and 40,320 permutations of each
of D8 and Q8. It tests all ordered pairs of distinct labels and all
multiplicities, including the exact binomial permutation counts. It also
tests all 1,096 multisets of ambient-group length supported in the abelian
subgroups of those groups, by a separate block-partition recursion.
An S3 label such as `231` lists the images of `1,2,3` in order.

For D6,D8,D10,D12,D14,D16, Dic_2,Dic_3,Dic_4 and A4, the checker exhausts
all maps whose quotient labels lie in the indicated two-element set,
161,344 maps in total. Testing whether their images are distinct identifies
exactly the realizing permutations. It checks the displayed product-one
ordering and the absence of a realizing permutation for each witness.
No factorial search on groups of order greater than eight is needed.

All universal statements have written proofs in the note. The finite
checks illustrate them and are not premises of the general proofs.
The declaration
`D5.S3.FiniteGroups.AliabadiQuotientObstruction.exists_obstructed_multiset`
states the general singleton existence conclusion, with actual
multiplicities, canonical abelianization and two bijections, in:

https://github.com/the-omega-institute/trureturing/blob/1154841a3345ca579e0d56fc4ceebee38814557c/D5/S3/FiniteGroups/AliabadiQuotientObstruction.lean

The other criteria, exact counts and product-one families have the written
proofs specified in the note, rather than being statements of that declaration.

## Creators and license

1. Haobo Ma — ChronoAI Pte Ltd, Singapore.
2. Wenlin Zhang — National University of Singapore; ChronoAI Pte Ltd, Singapore.

CC BY 4.0 (`cc-by-4.0`): https://creativecommons.org/licenses/by/4.0/
