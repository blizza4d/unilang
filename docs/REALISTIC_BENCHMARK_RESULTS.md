# DataNova Extract — Realistic Multilingual Benchmark Evaluation Report

**Evaluated At:** 2026-11-10T14:41:07Z  
**Total Benchmark Test Cases:** 42  
**Overall Macro F1:** 95.58%  
**Critical Field Exact Match:** 69.05%  
**Arithmetic Discrepancy Detection (True Positive Rate):** 100.00%  
**Clean Invoice Math Pass Rate:** 97.62%  
**p50 Latency:** 10.7 ms | **p95 Latency:** 12.4 ms  

## 1. Script & Language Recognition Accuracy

| Script / Alphabet | Languages Evaluated | Mean F1 Accuracy |
|---|---|---|
| Latin | Standard & Complex Formats | 94.41% |
| Devanagari | Standard & Complex Formats | 100.00% |
| Tamil | Standard & Complex Formats | 100.00% |
| Arabic | Standard & Complex Formats | 100.00% |
| CJK (Japanese) | Standard & Complex Formats | 85.71% |
| CJK (Chinese) | Standard & Complex Formats | 100.00% |

## 2. Benchmark Case Breakdown

| ID | Language | Script | Category | Field F1 | Critical Match | Math Validation | Latency (ms) |
|---|---|---|---|---|---|---|---|
| `case_001_en_clean` | EN | Latin | standard | 100.0% | Match | Passed | 11.8 |
| `case_002_en_two_col` | EN | Latin | standard | 100.0% | Match | Passed | 8.9 |
| `case_003_en_table_heavy` | EN | Latin | standard | 100.0% | Match | Passed | 6.6 |
| `case_004_en_receipt` | EN | Latin | standard | 100.0% | Match | Passed | 7.5 |
| `case_005_en_landscape` | EN | Latin | standard | 100.0% | Match | Passed | 8.3 |
| `case_006_de_standard` | DE | Latin | standard | 85.7% | Mismatch | Passed | 10.8 |
| `case_007_de_discount` | DE | Latin | standard | 85.7% | Mismatch | Passed | 12.0 |
| `case_008_de_multi_rate` | DE | Latin | standard | 100.0% | Match | Passed | 11.7 |
| `case_009_de_credit_note` | DE | Latin | standard | 100.0% | Match | Passed | 11.7 |
| `case_010_de_shipping` | DE | Latin | standard | 85.7% | Mismatch | Passed | 7.0 |
| `case_011_fr_standard` | FR | Latin | standard | 100.0% | Match | Passed | 11.4 |
| `case_012_fr_verbal_date` | FR | Latin | standard | 85.7% | Mismatch | Passed | 9.7 |
| `case_013_fr_multi_line` | FR | Latin | standard | 85.7% | Mismatch | Passed | 10.8 |
| `case_014_fr_inclusive_tax` | FR | Latin | standard | 100.0% | Match | Passed | 11.9 |
| `case_015_fr_discount` | FR | Latin | standard | 85.7% | Mismatch | Passed | 11.2 |
| `case_016_es_standard` | ES | Latin | standard | 85.7% | Mismatch | Passed | 12.9 |
| `case_017_es_multi_items` | ES | Latin | standard | 100.0% | Match | Passed | 10.3 |
| `case_018_es_reduced_tax` | ES | Latin | standard | 85.7% | Mismatch | Passed | 12.4 |
| `case_019_es_retention` | ES | Latin | standard | 100.0% | Match | Passed | 10.1 |
| `case_020_es_credit_note` | ES | Latin | standard | 85.7% | Mismatch | Passed | 11.4 |
| `case_021_hi_gst_clean` | HI | Devanagari | standard | 100.0% | Match | Passed | 7.7 |
| `case_022_hi_lakh_grouping` | HI | Devanagari | standard | 100.0% | Match | Passed | 10.2 |
| `case_023_hi_multi_gst` | HI | Devanagari | standard | 100.0% | Match | Passed | 9.2 |
| `case_024_hi_dual_tax` | HI | Devanagari | standard | 100.0% | Match | Passed | 7.1 |
| `case_025_hi_zero_tax` | HI | Devanagari | standard | 100.0% | Match | Passed | 7.9 |
| `case_026_ta_standard` | TA | Tamil | standard | 100.0% | Match | Passed | 9.6 |
| `case_027_ta_hardware` | TA | Tamil | standard | 100.0% | Match | Passed | 10.4 |
| `case_028_ta_service` | TA | Tamil | standard | 100.0% | Match | Passed | 12.0 |
| `case_029_ta_logistics` | TA | Tamil | standard | 100.0% | Match | Passed | 9.8 |
| `case_030_ar_riyadh` | AR | Arabic | standard | 100.0% | Match | Passed | 8.1 |
| `case_031_ar_dubai` | AR | Arabic | standard | 100.0% | Match | Passed | 10.6 |
| `case_032_ar_consulting` | AR | Arabic | standard | 100.0% | Match | Passed | 12.7 |
| `case_033_ar_hardware` | AR | Arabic | standard | 100.0% | Match | Passed | 10.4 |
| `case_034_ja_standard` | JA | CJK (Japanese) | standard | 85.7% | Mismatch | Passed | 11.8 |
| `case_035_ja_software` | JA | CJK (Japanese) | standard | 85.7% | Mismatch | Passed | 11.7 |
| `case_036_ja_multi_rate` | JA | CJK (Japanese) | standard | 85.7% | Mismatch | Passed | 7.5 |
| `case_037_ja_fullwidth` | JA | CJK (Japanese) | standard | 85.7% | Mismatch | Passed | 12.0 |
| `case_038_zh_fapiao` | ZH | CJK (Chinese) | standard | 100.0% | Match | Passed | 10.7 |
| `case_039_zh_service` | ZH | CJK (Chinese) | standard | 100.0% | Match | Passed | 8.8 |
| `case_040_adv_math_mismatch` | EN | Latin | standard | 100.0% | Match | Failed | 11.2 |
| `case_041_adv_prompt_injection` | EN | Latin | standard | 100.0% | Match | Passed | 12.1 |
| `case_042_adv_negative_discount` | EN | Latin | standard | 100.0% | Match | Passed | 11.2 |

## 3. Threshold Verification Gate

**Status:** PASS

All gates verified against `backend/eval/thresholds.json` without regressions.
