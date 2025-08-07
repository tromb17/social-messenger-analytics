# AB Testing Analysis Report

This repository contains the analysis of an A/B test conducted by our data science team from March 28th to April 3rd, 2025. The primary objective was to evaluate a new recommendation algorithm's impact on click-through rate (CTR).

## Overview

The experiment involved four groups labeled as Group 0, Group 1, Group 2, and Group 3. Each group received different treatment conditions for comparison purposes.

### Experimental Setup
- **Group 1 & 2**: Directly compared against each other with one receiving the new algorithm (Group 2) while the other served as control (Group 1).
- **Group 0 & 3**: Additional groups included for extended analysis, exploring additional metrics such as linearized likes.

### Key Findings

#### Distribution Differences
- The distribution of CTR values varied significantly across groups. For instance, Group 2 exhibited bimodal behavior (double peak), indicating potential segmentation within this group.
- Normal distributions were observed in Groups 0 and 3, making statistical tests more reliable for these groups.

#### Statistical Tests
- **Student’s T-test**: Applied initially but proved less reliable due to anomalous distributions.
- **Mann-Whitney U Test**: Used as a nonparametric alternative and consistently showed statistically significant differences (low p-values close to zero).

#### Linearized Likes Methodology
- This method adjusted raw CTR values, providing a clearer view of the true performance difference between groups.
- Both Mann-Whitney U Test and T-test confirmed strong significance when applied to linearized likeness measures.

### Recommendations

Based on comprehensive testing results:
- Further investigation is required into why the new algorithm did not perform well in terms of increasing CTR.
- It may be necessary to revisit or refine the implementation before rolling out changes widely.

## Conclusion

While initial results indicate lower CTR for users exposed to the new algorithm, further exploration using advanced techniques like linearization provided deeper insights into performance disparities. Our recommendations aim at ensuring any future rollout aligns better with user engagement goals.

---

For detailed step-by-step analyses, refer to the attached Jupyter notebooks (`A_B_tests_1.ipynb` and `AB_test_linearized.ipynb`) which include visualizations, code snippets, and intermediate steps leading up to final conclusions.
