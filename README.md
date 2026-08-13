# Appalachian English Existential Construction Pipeline
Scripts to preprocess, code, and summarize text search output of existential constructions from the Audio-Aligned and Parsed Corpus of Appalachian English (AAPCAppE) for statistical analysis.

## Requirements
Packages: `openpyxl` to edit .xlsx files with italic formatting for existential hits. 

Install with:

`pip install openpyxl`

## Workflow
The workflow consists of three stages:
* `filter_italics.py`: Filter exported search results from the AAPCAppE interface to retain only italicized hits of existential constructions.
* `count_existentials.py`: Automatically code linguistic variables for each existential token and produce a token-level dataset suitable for statistical analysis.
* `summarize_existentials.py`: Generate descriptive summary statistics to CSV.

The resulting dataset can be imported directly into statistical software such as Jamovi, R, or Python for chi-square tests, logistic regression, and mixed-effects modeling.

## Specifications
### Recognized token features
The script recognizes the following features of Appalachian English: 
* Existential markers: _they_, _there_, _it_
* Finite forms of BE: _is_, _are_, _was_, _were_, _'s_, _'re_, _isn't_, _aren't_, _wasn't_, _weren't_, _ain't_, _hain't_

Tokens containing _ain't_ or _hain't_ are retained descriptively but excluded from binary logistic regression because they do not overtly encode grammatical number.

### Automatically coded variables:
* speaker ID
* existential marker 
* verb form
* construction
* tense (present/past)
* agreement (singular/plural)
* polarity (affirmative/negative)
* contraction (contracted/uncontracted)

The dependent variable `outcome_singular` is coded as 1 (singular agreement), 0 (plural agreement), and blank	(unmarked).

### Summary variables reported:
* variable (from above)
* category
* count
* percent

## Repository Structure
```
.
├── filter_italics.py
├── count_existentials.py
├── summarize_existentials.py
└── README.md
```

**Citations:**
Tortora, Christina & Santorini, Beatrice & Blanchette, Frances & Diertani, C.E.A. 2017. *The Audio-Aligned and Parsed Corpus of Appalachian English* (AAPCAppE). www.aapcappe.org
