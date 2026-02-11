# Codex Reliability Evaluation Report Under Large-Scale Context (Complete Edition, Single Markdown)

- Generated at (UTC): 2026-02-11T04:58:42Z
- Report characteristics: self-contained single file, validation data included, personally identifiable information and absolute paths removed from the body
- Model: gpt-5.3-codex (from environment manifest) [S7]

## Executive Summary
This report quantitatively evaluates two practical bottlenecks in Codex operations: (i) final-recall reliability in continuous multi-turn dialogue, and (ii) strict extraction accuracy and processing time with ultra-long inputs. Evaluation was conducted with a reproducible deterministic protocol, and results were judged by strict exact match. [S1][S4][S8][S9]

The main results are as follows.
1. 20/30/40 turns achieved strict 100% (however, uncertainty is wide because n=1). [S1][S2]
2. 50 turns succeeded in 2 of 3 trials (66.7%). The failure occurred at final recall as a recency slip returning `ACK_49` instead of the expected token. [S1]
3. Long-text extraction (5,000→300,000 chars) succeeded 2/2 (100%) under all conditions, with processing times in the 8-11 second range. [S4][S5]
4. Context usage rose sharply in the final multi-turn step, with mean final input at 50 turns reaching about 7.81M tokens. [S3]

This report extends these findings to mechanism-level hypotheses from the perspectives of when failures are likely, why they occur, and what should be validated next.

## 1. Research Objective and Research Questions
### 1.1 Research Objective
To build a reproducible quality gate for production operations, this study clarifies the following:
- RQ1: How far can multi-turn memory reliability be maintained within 50 turns?
- RQ2: Are strict extraction accuracy and latency for 300,000-char class inputs within practical bounds?
- RQ3: Are failures random breakdowns or structured (explainable) error patterns?

### 1.2 Prior Hypotheses (Working Hypotheses)
- H1: 20-40 turns pass at >=95%.
- H2: 50 turns also maintain >=80%.
- H3: As input length increases, higher latency and lower accuracy become apparent.

## 2. Experimental Method
### 2.1 Multi-turn Memory Test (Primary endpoint: <=50 turns)
Protocol:
1. Turn 0: Store a unique token and require an exact `STORED` response.
2. Turn 1..(N-2): Require exact `ACK_t` responses.
3. Turn N-1: Respond with only the initially stored token (final recall).

Judgment:
- strict_pass: exact match.
- semantic_pass: normalized match (auxiliary).
- failure_stage: init / mid_turn / final_recall。

### 2.2 Long-text Extraction Test (5,000-300,000 chars)
Protocol:
1. Embed `<<TOKEN:...>>` in the long text body.
2. Require a response containing only the token value.
3. Two trials per length.

Judgment: strict match, duration, and input/cached/output token usage.

### 2.3 Statistical Methods
- Success-rate interval: Wilson 95% CI.
- Auxiliary hypothesis check for 50-turn: one-sided binomial tail probability `P(X<=k | n, p0)`.
- Descriptive regression: linear regression (for explanation, not causal inference).

## 3. Aggregated Results (Summary)
### 3.1 Multi-turn（<=50 turns）
| turns | n | strict_pass | strict_rate | 95% CI (Wilson) | avg_duration_sec | std_duration_sec |
|---|---|---|---|---|---|---|
| 20 | 1 | 1 | 100.0% | 20.7-100.0% | 211.0 | 0.00 |
| 30 | 1 | 1 | 100.0% | 20.7-100.0% | 242.0 | 0.00 |
| 40 | 1 | 1 | 100.0% | 20.7-100.0% | 339.0 | 0.00 |
| 50 | 3 | 2 | 66.7% | 20.8-93.9% | 471.7 | 9.74 |

### 3.2 Long-context（5,000-300,000 chars）
| length_chars | n | pass | pass_rate | 95% CI (Wilson) | avg_duration_sec | std_duration_sec | avg_input_tokens | avg_cached_input_tokens | avg_output_tokens |
|---|---|---|---|---|---|---|---|---|---|
| 5,000 | 2 | 2 | 100.0% | 34.2-100.0% | 10.0 | 0.00 | 18,219.0 | 10,112.0 | 140.5 |
| 10,000 | 2 | 2 | 100.0% | 34.2-100.0% | 10.0 | 0.00 | 19,156.0 | 10,112.0 | 101.5 |
| 15,000 | 2 | 2 | 100.0% | 34.2-100.0% | 9.5 | 0.50 | 20,094.0 | 3,456.0 | 131.0 |
| 20,000 | 2 | 2 | 100.0% | 34.2-100.0% | 9.0 | 1.00 | 21,031.0 | 16,768.0 | 112.0 |
| 300,000 | 2 | 2 | 100.0% | 34.2-100.0% | 10.0 | 1.00 | 73,531.0 | 3,456.0 | 166.0 |

## 4. Detailed Analysis of Context Usage
### 4.1 Multi-turn init/final usage
| turns | n | avg_init_input | avg_init_cached | avg_init_output | avg_final_input | avg_final_cached | avg_final_output | final_cached/input |
|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 19,050.0 | 3,456.0 | 188.0 | 1,830,699.0 | 1,547,136.0 | 2,126.0 | 0.8451 |
| 30 | 1 | 19,050.0 | 17,152.0 | 190.0 | 3,890,549.0 | 3,641,856.0 | 1,908.0 | 0.9361 |
| 40 | 1 | 19,050.0 | 16,768.0 | 84.0 | 5,817,242.0 | 5,283,712.0 | 2,605.0 | 0.9083 |
| 50 | 3 | 19,049.3 | 3,456.0 | 197.7 | 7,811,960.0 | 7,131,221.3 | 3,136.7 | 0.9129 |

Observation: final input tokens increase sharply with turns, reaching about 7.81M tokens at 50 turns. This is about 4.27x the 20-turn value. [S3]

### 4.2 Long-context usage
| length_chars | n | avg_input_tokens | avg_cached_input_tokens | avg_output_tokens |
|---|---|---|---|---|
| 5,000 | 2 | 18,219.0 | 10,112.0 | 140.5 |
| 10,000 | 2 | 19,156.0 | 10,112.0 | 101.5 |
| 15,000 | 2 | 20,094.0 | 3,456.0 | 131.0 |
| 20,000 | 2 | 21,031.0 | 16,768.0 | 112.0 |
| 300,000 | 2 | 73,531.0 | 3,456.0 | 166.0 |

Observation: mean input at 300,000 chars is 73,531 tokens. Cached tokens are affected by run conditions and are not monotonically proportional to length. [S6]

## 5. Gap Analysis: Hypotheses vs Observations
- H1 (20-40 turns >=95%): supported. Observed value is 100%. [S2]
- H2 (50 turns >=80%): not supported. Observed value is 66.7% (gap: -13.3pt). [S2]
- H3 (degradation with longer inputs): not supported in this task (no failures observed, and latency increase is weak). [S5]
- Auxiliary 50-turn calculation: P(X<=2|n=3,p=0.8)=0.488. With such a small sample, this is not strong rejection evidence, but it shows thin margin against the 80% design target. [S1]
- For long-text runs (n=10, 0 failures), the rule-of-three upper failure-rate bound is about 30.0%. The apparent 100% success should not be overtrusted. [S4]

## 6. Descriptive Regression and Scaling
### 6.1 Multi-turn final input vs turns
- Regression equation: `final_input_tokens = 198,704.76 * turns + (-2,117,054.10)`
- Coefficient of determination: `R^2 = 0.999844`
- Descriptive prediction (55 turns): `8,811,707.7` tokens

### 6.2 Long input_tokens vs chars
- Regression equation: `input_tokens = 0.187499094 * chars + (17,281.2634)`
- Coefficient of determination: `R^2 = 0.999999999895`
- Descriptive prediction (500k chars): `111,030.8` tokens
- Descriptive prediction (1M chars): `204,780.4` tokens

### 6.3 duration vs chars
- Regression equation: `duration_sec = 0.000001169811 * chars + (9.6181)`
- Coefficient of determination: `R^2 = 0.113325`
Interpretation: Within this range, time contribution from length alone is weak; task complexity and runtime environment factors appear dominant.

## 7. Failure Mechanism Details
| fail_stage | note | count |
|---|---|---|
| final_recall | final_recall_semantic_mismatch_or_timeout | 1 |

The only observed failure occurred at final_recall, where the response was `ACK_49`. This was not a collapse into unrelated tokens, but a final-reference error under sequence retention, suggesting a pull toward recency (recency attractor). [S1][S10]

## 8. Long-text Test Efficiency Metrics (By Trial)
| length_chars | trial | input_tokens/char | chars/sec | duration_sec | input_tokens | cached_input_tokens | output_tokens |
|---|---|---|---|---|---|---|---|
| 5,000 | 1 | 3.6438 | 500.00 | 10 | 18219 | 3456 | 131 |
| 5,000 | 2 | 3.6438 | 500.00 | 10 | 18219 | 16768 | 150 |
| 10,000 | 1 | 1.9156 | 1000.00 | 10 | 19156 | 3456 | 91 |
| 10,000 | 2 | 1.9156 | 1000.00 | 10 | 19156 | 16768 | 112 |
| 15,000 | 1 | 1.3396 | 1666.67 | 9 | 20094 | 3456 | 141 |
| 15,000 | 2 | 1.3396 | 1500.00 | 10 | 20094 | 3456 | 121 |
| 20,000 | 1 | 1.0515 | 2500.00 | 8 | 21031 | 16768 | 71 |
| 20,000 | 2 | 1.0515 | 2000.00 | 10 | 21031 | 16768 | 153 |
| 300,000 | 1 | 0.2451 | 33333.33 | 9 | 73531 | 3456 | 150 |
| 300,000 | 2 | 0.2451 | 27272.73 | 11 | 73531 | 3456 | 182 |

## 9. Raw Data (Fully Expanded in Main Text)
### 9.1 Multi-turn（<=50） raw records
| ts | phase | turns | trial | duration_sec | init_ec | final_ec | strict_pass | semantic_pass | fail_stage | fail_turn | expected | actual | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-02-11T03:05:28Z | coarse | 20 | 1 | 211 | 0 | 0 | true | true | none | 0 | CP_coarse_20_1_20260211 | CP_coarse_20_1_20260211 | ok |
| 2026-02-11T03:08:59Z | coarse | 30 | 1 | 242 | 0 | 0 | true | true | none | 0 | CP_coarse_30_1_20260211 | CP_coarse_30_1_20260211 | ok |
| 2026-02-11T03:13:01Z | coarse | 40 | 1 | 339 | 0 | 0 | true | true | none | 0 | CP_coarse_40_1_20260211 | CP_coarse_40_1_20260211 | ok |
| 2026-02-11T03:18:40Z | coarse | 50 | 1 | 477 | 0 | 0 | true | true | none | 0 | CP_coarse_50_1_20260211 | CP_coarse_50_1_20260211 | ok |
| 2026-02-11T03:36:50Z | focus | 50 | 2 | 458 | 0 | 0 | true | true | none | 0 | CP_focus_50_2_20260211 | CP_focus_50_2_20260211 | ok |
| 2026-02-11T03:44:28Z | focus | 50 | 3 | 480 | 0 | 0 | false | false | final_recall | 49 | CP_focus_50_3_20260211 | ACK_49 | final_recall_semantic_mismatch_or_timeout |

### 9.2 Long-context raw records
| ts | length_chars | trial | timeout_sec | duration_sec | exit_code | strict_pass | expected | actual | input_tokens | cached_input_tokens | output_tokens | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-02-11T04:17:26Z | 5,000 | 1 | 300 | 10 | 0 | true | LT_5000_1_20260211 | LT_5000_1_20260211 | 18219 | 3456 | 131 | ok |
| 2026-02-11T04:17:36Z | 5,000 | 2 | 300 | 10 | 0 | true | LT_5000_2_20260211 | LT_5000_2_20260211 | 18219 | 16768 | 150 | ok |
| 2026-02-11T04:17:46Z | 10,000 | 1 | 300 | 10 | 0 | true | LT_10000_1_20260211 | LT_10000_1_20260211 | 19156 | 3456 | 91 | ok |
| 2026-02-11T04:17:56Z | 10,000 | 2 | 300 | 10 | 0 | true | LT_10000_2_20260211 | LT_10000_2_20260211 | 19156 | 16768 | 112 | ok |
| 2026-02-11T04:18:06Z | 15,000 | 1 | 300 | 9 | 0 | true | LT_15000_1_20260211 | LT_15000_1_20260211 | 20094 | 3456 | 141 | ok |
| 2026-02-11T04:18:15Z | 15,000 | 2 | 300 | 10 | 0 | true | LT_15000_2_20260211 | LT_15000_2_20260211 | 20094 | 3456 | 121 | ok |
| 2026-02-11T04:18:25Z | 20,000 | 1 | 300 | 8 | 0 | true | LT_20000_1_20260211 | LT_20000_1_20260211 | 21031 | 16768 | 71 | ok |
| 2026-02-11T04:18:33Z | 20,000 | 2 | 300 | 10 | 0 | true | LT_20000_2_20260211 | LT_20000_2_20260211 | 21031 | 16768 | 153 | ok |
| 2026-02-11T04:18:43Z | 300,000 | 1 | 900 | 9 | 0 | true | LT_300000_1_20260211 | LT_300000_1_20260211 | 73531 | 3456 | 150 | ok |
| 2026-02-11T04:18:52Z | 300,000 | 2 | 900 | 11 | 0 | true | LT_300000_2_20260211 | LT_300000_2_20260211 | 73531 | 3456 | 182 | ok |

## 10. Per-turn Trajectories for Three 50-turn Runs (150 rows)
Note: `TOKEN` in the expected column means the stored token is expected in the final recall turn.

### R50-A per-turn log
| turn | expected | actual | completed | input_tokens | cached_input_tokens | output_tokens | delta_input_tokens |
|---|---|---|---|---|---|---|---|
| 0 | STORED | STORED | True | 19050 | 3456 | 138 | - |
| 1 | ACK_1 | ACK_1 | True | 45730 | 22400 | 299 | +26680 |
| 2 | ACK_2 | ACK_2 | True | 80040 | 49024 | 423 | +34310 |
| 3 | ACK_3 | ACK_3 | True | 121980 | 83200 | 526 | +41940 |
| 4 | ACK_4 | ACK_4 | True | 171550 | 125056 | 605 | +49570 |
| 5 | ACK_5 | ACK_5 | True | 228750 | 174592 | 631 | +57200 |
| 6 | ACK_6 | ACK_6 | True | 293580 | 231680 | 717 | +64830 |
| 7 | ACK_7 | ACK_7 | True | 366040 | 296448 | 806 | +72460 |
| 8 | ACK_8 | ACK_8 | True | 446130 | 368768 | 908 | +80090 |
| 9 | ACK_9 | ACK_9 | True | 533850 | 448768 | 1047 | +87720 |
| 10 | ACK_10 | ACK_10 | True | 629200 | 536448 | 1128 | +95350 |
| 11 | ACK_11 | ACK_11 | True | 732180 | 631680 | 1211 | +102980 |
| 12 | ACK_12 | ACK_12 | True | 842790 | 734592 | 1262 | +110610 |
| 13 | ACK_13 | ACK_13 | True | 961030 | 845184 | 1378 | +118240 |
| 14 | ACK_14 | ACK_14 | True | 1086900 | 963328 | 1484 | +125870 |
| 15 | ACK_15 | ACK_15 | True | 1220400 | 1089152 | 1513 | +133500 |
| 16 | ACK_16 | ACK_16 | True | 1361530 | 1222528 | 1611 | +141130 |
| 17 | ACK_17 | ACK_17 | True | 1510290 | 1363584 | 1724 | +148760 |
| 18 | ACK_18 | ACK_18 | True | 1666680 | 1512320 | 1731 | +156390 |
| 19 | ACK_19 | ACK_19 | True | 1830700 | 1668608 | 1738 | +164020 |
| 20 | ACK_20 | ACK_20 | True | 2002350 | 1832576 | 1831 | +171650 |
| 21 | ACK_21 | ACK_21 | True | 2181630 | 2004096 | 1914 | +179280 |
| 22 | ACK_22 | ACK_22 | True | 2368540 | 2183296 | 1945 | +186910 |
| 23 | ACK_23 | ACK_23 | True | 2563080 | 2370176 | 1952 | +194540 |
| 24 | ACK_24 | ACK_24 | True | 2765250 | 2564608 | 1959 | +202170 |
| 25 | ACK_25 | ACK_25 | True | 2975050 | 2766720 | 2065 | +209800 |
| 26 | ACK_26 | ACK_26 | True | 3192480 | 2976384 | 2072 | +217430 |
| 27 | ACK_27 | ACK_27 | True | 3417540 | 3193728 | 2260 | +225060 |
| 28 | ACK_28 | ACK_28 | True | 3650230 | 3418752 | 2267 | +232690 |
| 29 | ACK_29 | ACK_29 | True | 3890550 | 3651328 | 2274 | +240320 |
| 30 | ACK_30 | ACK_30 | True | 4138500 | 3891584 | 2364 | +247950 |
| 31 | ACK_31 | ACK_31 | True | 4294532 | 3895040 | 2466 | +156032 |
| 32 | ACK_32 | ACK_32 | True | 4458194 | 4050944 | 2473 | +163662 |
| 33 | ACK_33 | ACK_33 | True | 4629486 | 4214528 | 2496 | +171292 |
| 34 | ACK_34 | ACK_34 | True | 4808408 | 4385792 | 2503 | +178922 |
| 35 | ACK_35 | ACK_35 | True | 4994960 | 4564608 | 2539 | +186552 |
| 36 | ACK_36 | ACK_36 | True | 5189142 | 4751104 | 2546 | +194182 |
| 37 | ACK_37 | ACK_37 | True | 5390954 | 4945152 | 2553 | +201812 |
| 38 | ACK_38 | ACK_38 | True | 5600396 | 5146880 | 2560 | +209442 |
| 39 | ACK_39 | ACK_39 | True | 5817468 | 5356288 | 2567 | +217072 |
| 40 | ACK_40 | ACK_40 | True | 6042170 | 5573248 | 2574 | +224702 |
| 41 | ACK_41 | ACK_41 | True | 6274502 | 5797888 | 2581 | +232332 |
| 42 | ACK_42 | ACK_42 | True | 6514464 | 6030080 | 2588 | +239962 |
| 43 | ACK_43 | ACK_43 | True | 6762056 | 6269952 | 2595 | +247592 |
| 44 | ACK_44 | ACK_44 | True | 6918048 | 6273408 | 2620 | +155992 |
| 45 | ACK_45 | ACK_45 | True | 7081670 | 6429312 | 2627 | +163622 |
| 46 | ACK_46 | ACK_46 | True | 7252922 | 6592896 | 2650 | +171252 |
| 47 | ACK_47 | ACK_47 | True | 7431804 | 6764032 | 2673 | +178882 |
| 48 | ACK_48 | ACK_48 | True | 7618316 | 6942848 | 2759 | +186512 |
| 49 | TOKEN | CP_coarse_50_1_20260211 | True | 7812457 | 7129216 | 2863 | +194141 |

### R50-B per-turn log
| turn | expected | actual | completed | input_tokens | cached_input_tokens | output_tokens | delta_input_tokens |
|---|---|---|---|---|---|---|---|
| 0 | STORED | STORED | True | 19049 | 3456 | 176 | - |
| 1 | ACK_1 | ACK_1 | True | 45728 | 22400 | 340 | +26679 |
| 2 | ACK_2 | ACK_2 | True | 80037 | 49024 | 430 | +34309 |
| 3 | ACK_3 | ACK_3 | True | 121976 | 83200 | 499 | +41939 |
| 4 | ACK_4 | ACK_4 | True | 171545 | 125056 | 630 | +49569 |
| 5 | ACK_5 | ACK_5 | True | 228744 | 174592 | 722 | +57199 |
| 6 | ACK_6 | ACK_6 | True | 293573 | 231680 | 758 | +64829 |
| 7 | ACK_7 | ACK_7 | True | 366032 | 296448 | 814 | +72459 |
| 8 | ACK_8 | ACK_8 | True | 446121 | 368768 | 849 | +80089 |
| 9 | ACK_9 | ACK_9 | True | 533840 | 448768 | 932 | +87719 |
| 10 | ACK_10 | ACK_10 | True | 629189 | 536448 | 991 | +95349 |
| 11 | ACK_11 | ACK_11 | True | 732168 | 631680 | 1079 | +102979 |
| 12 | ACK_12 | ACK_12 | True | 842777 | 734592 | 1159 | +110609 |
| 13 | ACK_13 | ACK_13 | True | 961016 | 845056 | 1211 | +118239 |
| 14 | ACK_14 | ACK_14 | True | 1086885 | 963200 | 1218 | +125869 |
| 15 | ACK_15 | ACK_15 | True | 1220384 | 1089024 | 1308 | +133499 |
| 16 | ACK_16 | ACK_16 | True | 1361513 | 1222400 | 1404 | +141129 |
| 17 | ACK_17 | ACK_17 | True | 1510272 | 1363456 | 1465 | +148759 |
| 18 | ACK_18 | ACK_18 | True | 1666661 | 1512192 | 1531 | +156389 |
| 19 | ACK_19 | ACK_19 | True | 1830680 | 1668480 | 1642 | +164019 |
| 20 | ACK_20 | ACK_20 | True | 2002329 | 1832448 | 1685 | +171649 |
| 21 | ACK_21 | ACK_21 | True | 2181608 | 2003968 | 1692 | +179279 |
| 22 | ACK_22 | ACK_22 | True | 2368517 | 2183168 | 1782 | +186909 |
| 23 | ACK_23 | ACK_23 | True | 2563056 | 2370048 | 1825 | +194539 |
| 24 | ACK_24 | ACK_24 | True | 2765225 | 2564480 | 1901 | +202169 |
| 25 | ACK_25 | ACK_25 | True | 2975024 | 2766592 | 2022 | +209799 |
| 26 | ACK_26 | ACK_26 | True | 3192453 | 2976256 | 2048 | +217429 |
| 27 | ACK_27 | ACK_27 | True | 3417512 | 3193600 | 2055 | +225059 |
| 28 | ACK_28 | ACK_28 | True | 3650201 | 3418624 | 2062 | +232689 |
| 29 | ACK_29 | ACK_29 | True | 3890520 | 3651200 | 2069 | +240319 |
| 30 | ACK_30 | ACK_30 | True | 4138469 | 3891456 | 2145 | +247949 |
| 31 | ACK_31 | ACK_31 | True | 4294449 | 3894912 | 2191 | +155980 |
| 32 | ACK_32 | ACK_32 | True | 4458059 | 4050816 | 2221 | +163610 |
| 33 | ACK_33 | ACK_33 | True | 4629299 | 4214400 | 2252 | +171240 |
| 34 | ACK_34 | ACK_34 | True | 4808169 | 4385536 | 2280 | +178870 |
| 35 | ACK_35 | ACK_35 | True | 4994669 | 4564352 | 2315 | +186500 |
| 36 | ACK_36 | ACK_36 | True | 5188799 | 4750720 | 2349 | +194130 |
| 37 | ACK_37 | ACK_37 | True | 5390559 | 4944768 | 2356 | +201760 |
| 38 | ACK_38 | ACK_38 | True | 5599949 | 5146496 | 2363 | +209390 |
| 39 | ACK_39 | ACK_39 | True | 5816969 | 5355776 | 2370 | +217020 |
| 40 | ACK_40 | ACK_40 | True | 6041619 | 5572736 | 2377 | +224650 |
| 41 | ACK_41 | ACK_41 | True | 6273899 | 5797248 | 2384 | +232280 |
| 42 | ACK_42 | ACK_42 | True | 6513809 | 6029440 | 2391 | +239910 |
| 43 | ACK_43 | ACK_43 | True | 6761349 | 6269312 | 2398 | +247540 |
| 44 | ACK_44 | ACK_44 | True | 6917328 | 6272768 | 2491 | +155979 |
| 45 | ACK_45 | ACK_45 | True | 7080937 | 6428672 | 2562 | +163609 |
| 46 | ACK_46 | ACK_46 | True | 7252176 | 6592256 | 2604 | +171239 |
| 47 | ACK_47 | ACK_47 | True | 7431045 | 6763392 | 2611 | +178869 |
| 48 | ACK_48 | ACK_48 | True | 7617544 | 6942208 | 2649 | +186499 |
| 49 | TOKEN | CP_focus_50_2_20260211 | True | 7811672 | 7128576 | 2816 | +194128 |

### R50-C per-turn log
| turn | expected | actual | completed | input_tokens | cached_input_tokens | output_tokens | delta_input_tokens |
|---|---|---|---|---|---|---|---|
| 0 | STORED | STORED | True | 19049 | 3456 | 279 | - |
| 1 | ACK_1 | ACK_1 | True | 45728 | 22400 | 440 | +26679 |
| 2 | ACK_2 | ACK_2 | True | 80037 | 49024 | 496 | +34309 |
| 3 | ACK_3 | ACK_3 | True | 121976 | 83200 | 607 | +41939 |
| 4 | ACK_4 | ACK_4 | True | 171545 | 125056 | 681 | +49569 |
| 5 | ACK_5 | ACK_5 | True | 228744 | 174592 | 734 | +57199 |
| 6 | ACK_6 | ACK_6 | True | 293573 | 231680 | 792 | +64829 |
| 7 | ACK_7 | ACK_7 | True | 366032 | 296448 | 835 | +72459 |
| 8 | ACK_8 | ACK_8 | True | 446121 | 368768 | 913 | +80089 |
| 9 | ACK_9 | ACK_9 | True | 533840 | 448768 | 997 | +87719 |
| 10 | ACK_10 | ACK_10 | True | 629189 | 536448 | 1066 | +95349 |
| 11 | ACK_11 | ACK_11 | True | 732168 | 631680 | 1138 | +102979 |
| 12 | ACK_12 | ACK_12 | True | 842777 | 734592 | 1255 | +110609 |
| 13 | ACK_13 | ACK_13 | True | 961016 | 845056 | 1341 | +118239 |
| 14 | ACK_14 | ACK_14 | True | 1086885 | 963200 | 1402 | +125869 |
| 15 | ACK_15 | ACK_15 | True | 1220384 | 1089024 | 1467 | +133499 |
| 16 | ACK_16 | ACK_16 | True | 1361513 | 1222400 | 1474 | +141129 |
| 17 | ACK_17 | ACK_17 | True | 1510272 | 1363456 | 1520 | +148759 |
| 18 | ACK_18 | ACK_18 | True | 1666661 | 1512192 | 1527 | +156389 |
| 19 | ACK_19 | ACK_19 | True | 1830680 | 1668480 | 1595 | +164019 |
| 20 | ACK_20 | ACK_20 | True | 2002329 | 1832448 | 1769 | +171649 |
| 21 | ACK_21 | ACK_21 | True | 2181608 | 2003968 | 1802 | +179279 |
| 22 | ACK_22 | ACK_22 | True | 2368517 | 2183168 | 1809 | +186909 |
| 23 | ACK_23 | ACK_23 | True | 2563056 | 2370048 | 1816 | +194539 |
| 24 | ACK_24 | ACK_24 | True | 2765225 | 2564480 | 1914 | +202169 |
| 25 | ACK_25 | ACK_25 | True | 2975024 | 2766592 | 2003 | +209799 |
| 26 | ACK_26 | ACK_26 | True | 3192453 | 2976256 | 2133 | +217429 |
| 27 | ACK_27 | ACK_27 | True | 3417512 | 3193600 | 2140 | +225059 |
| 28 | ACK_28 | ACK_28 | True | 3650201 | 3418624 | 2147 | +232689 |
| 29 | ACK_29 | ACK_29 | True | 3890520 | 3651200 | 2154 | +240319 |
| 30 | ACK_30 | ACK_30 | True | 4138469 | 3891456 | 2234 | +247949 |
| 31 | ACK_31 | ACK_31 | True | 4294468 | 3894912 | 2342 | +155999 |
| 32 | ACK_32 | ACK_32 | True | 4458097 | 4050816 | 2367 | +163629 |
| 33 | ACK_33 | ACK_33 | True | 4629356 | 4214400 | 2397 | +171259 |
| 34 | ACK_34 | ACK_34 | True | 4808245 | 4385536 | 2442 | +178889 |
| 35 | ACK_35 | ACK_35 | True | 4994764 | 4564352 | 2449 | +186519 |
| 36 | ACK_36 | ACK_36 | True | 5188913 | 4750848 | 2480 | +194149 |
| 37 | ACK_37 | ACK_37 | True | 5390692 | 4944896 | 2487 | +201779 |
| 38 | ACK_38 | ACK_38 | True | 5600101 | 5146624 | 2494 | +209409 |
| 39 | ACK_39 | ACK_39 | True | 5817140 | 5355904 | 2501 | +217039 |
| 40 | ACK_40 | ACK_40 | True | 6041809 | 5572864 | 2570 | +224669 |
| 41 | ACK_41 | ACK_41 | True | 6274108 | 5797504 | 2597 | +232299 |
| 42 | ACK_42 | ACK_42 | True | 6514037 | 6029696 | 2604 | +239929 |
| 43 | ACK_43 | ACK_43 | True | 6761596 | 6269568 | 2611 | +247559 |
| 44 | ACK_44 | ACK_44 | True | 6917547 | 6280192 | 2638 | +155951 |
| 45 | ACK_45 | ACK_45 | True | 7081128 | 6436096 | 2661 | +163581 |
| 46 | ACK_46 | ACK_46 | True | 7252339 | 6599552 | 2668 | +171211 |
| 47 | ACK_47 | ACK_47 | True | 7431180 | 6770688 | 2675 | +178841 |
| 48 | ACK_48 | ACK_48 | True | 7617651 | 6949504 | 2682 | +186471 |
| 49 | TOKEN | ACK_49 | True | 7811751 | 7135872 | 3731 | +194100 |

## 11. Validity and Limitations
1. Trial counts per condition are small (n=1-3, n=2), so confidence intervals are wide.
2. Long-text tasks are extraction-centric; extrapolation to inference-centric tasks should be cautious.
3. Cached tokens depend on session state and are not uniquely determined by input length alone.
4. Regressions in this report are descriptive models and are not intended for causal interpretation.

## 12. Practical Implications and Next-stage Plan
### 12.1 Practical Implications
- Safe zone: treat <=40 turns as the baseline operating range.
- 50-turn operation: reproducibility risk exists without interventions such as checkpoint/restate.
- 300k long text: high practical viability for extraction tasks, but additional validation is mandatory for complex inference tasks.

### 12.2 Next-stage Experiments (Higher Precision)
1. Boundary sharpening: 42/45/48/50/52 turns, each with N>=20.
2. Intervention comparison: A/B test with and without checkpoint/restate every 10 turns.
3. Complexity ladder: extraction -> constrained search -> 2-hop reference -> multi-constraint reasoning.
4. Token-budget manipulation: keep turns fixed, vary redundant information volume, and estimate the failure-rate curve.

## 13. Sources (Anonymized IDs)
- [S1] MT-50-CAPPED-RAW-v1（multi-turn raw records, extracted 2026-02-11）
- [S2] MT-50-CAPPED-SUMMARY-v1（multi-turn aggregated table, extracted 2026-02-11）
- [S3] MT-50-CAPPED-CONTEXT-v1（multi-turn context usage, extracted 2026-02-11）
- [S4] LT-RAW-v1（long-context raw records, extracted 2026-02-11）
- [S5] LT-SUMMARY-v1（long-context aggregated table, extracted 2026-02-11）
- [S6] LT-CONTEXT-v1（long-context context usage, extracted 2026-02-11）
- [S7] ENV-MODEL-MANIFEST-v1（model/runtime metadata, extracted 2026-02-11）
- [S8] PROTOCOL-MULTITURN-v1（multi-turn script logic, extracted 2026-02-11）
- [S9] PROTOCOL-LONGTEXT-v1（long-text script logic, extracted 2026-02-11）
- [S10] TURN-TRACE-50-v1（per-turn JSON usage traces for 50-turn runs, extracted 2026-02-11）

## 14. Appendix A: Verbatim Turn-by-turn Interpretation for Three 50-turn Runs (Detailed Log Commentary)
This section explains each turn in natural language, one line per turn, to make manual verification of table values easier.
It explicitly highlights, by trial, aspects that are easy to miss in tables alone: increment fluctuation, final-turn retrieval behavior, and continuity of response patterns.

### R50-A Detailed Verbatim Log
- R50-A / Turn 00: expected=STORED, actual=STORED, completed=True, input_tokens=19050, cached_input_tokens=3456, output_tokens=138, delta_input=initial, judgment=match.
- R50-A / Turn 01: expected=ACK_1, actual=ACK_1, completed=True, input_tokens=45730, cached_input_tokens=22400, output_tokens=299, delta_input=+26,680, judgment=match.
- R50-A / Turn 02: expected=ACK_2, actual=ACK_2, completed=True, input_tokens=80040, cached_input_tokens=49024, output_tokens=423, delta_input=+34,310, judgment=match.
- R50-A / Turn 03: expected=ACK_3, actual=ACK_3, completed=True, input_tokens=121980, cached_input_tokens=83200, output_tokens=526, delta_input=+41,940, judgment=match.
- R50-A / Turn 04: expected=ACK_4, actual=ACK_4, completed=True, input_tokens=171550, cached_input_tokens=125056, output_tokens=605, delta_input=+49,570, judgment=match.
- R50-A / Turn 05: expected=ACK_5, actual=ACK_5, completed=True, input_tokens=228750, cached_input_tokens=174592, output_tokens=631, delta_input=+57,200, judgment=match.
- R50-A / Turn 06: expected=ACK_6, actual=ACK_6, completed=True, input_tokens=293580, cached_input_tokens=231680, output_tokens=717, delta_input=+64,830, judgment=match.
- R50-A / Turn 07: expected=ACK_7, actual=ACK_7, completed=True, input_tokens=366040, cached_input_tokens=296448, output_tokens=806, delta_input=+72,460, judgment=match.
- R50-A / Turn 08: expected=ACK_8, actual=ACK_8, completed=True, input_tokens=446130, cached_input_tokens=368768, output_tokens=908, delta_input=+80,090, judgment=match.
- R50-A / Turn 09: expected=ACK_9, actual=ACK_9, completed=True, input_tokens=533850, cached_input_tokens=448768, output_tokens=1047, delta_input=+87,720, judgment=match.
- R50-A / Turn 10: expected=ACK_10, actual=ACK_10, completed=True, input_tokens=629200, cached_input_tokens=536448, output_tokens=1128, delta_input=+95,350, judgment=match.
- R50-A / Turn 11: expected=ACK_11, actual=ACK_11, completed=True, input_tokens=732180, cached_input_tokens=631680, output_tokens=1211, delta_input=+102,980, judgment=match.
- R50-A / Turn 12: expected=ACK_12, actual=ACK_12, completed=True, input_tokens=842790, cached_input_tokens=734592, output_tokens=1262, delta_input=+110,610, judgment=match.
- R50-A / Turn 13: expected=ACK_13, actual=ACK_13, completed=True, input_tokens=961030, cached_input_tokens=845184, output_tokens=1378, delta_input=+118,240, judgment=match.
- R50-A / Turn 14: expected=ACK_14, actual=ACK_14, completed=True, input_tokens=1086900, cached_input_tokens=963328, output_tokens=1484, delta_input=+125,870, judgment=match.
- R50-A / Turn 15: expected=ACK_15, actual=ACK_15, completed=True, input_tokens=1220400, cached_input_tokens=1089152, output_tokens=1513, delta_input=+133,500, judgment=match.
- R50-A / Turn 16: expected=ACK_16, actual=ACK_16, completed=True, input_tokens=1361530, cached_input_tokens=1222528, output_tokens=1611, delta_input=+141,130, judgment=match.
- R50-A / Turn 17: expected=ACK_17, actual=ACK_17, completed=True, input_tokens=1510290, cached_input_tokens=1363584, output_tokens=1724, delta_input=+148,760, judgment=match.
- R50-A / Turn 18: expected=ACK_18, actual=ACK_18, completed=True, input_tokens=1666680, cached_input_tokens=1512320, output_tokens=1731, delta_input=+156,390, judgment=match.
- R50-A / Turn 19: expected=ACK_19, actual=ACK_19, completed=True, input_tokens=1830700, cached_input_tokens=1668608, output_tokens=1738, delta_input=+164,020, judgment=match.
- R50-A / Turn 20: expected=ACK_20, actual=ACK_20, completed=True, input_tokens=2002350, cached_input_tokens=1832576, output_tokens=1831, delta_input=+171,650, judgment=match.
- R50-A / Turn 21: expected=ACK_21, actual=ACK_21, completed=True, input_tokens=2181630, cached_input_tokens=2004096, output_tokens=1914, delta_input=+179,280, judgment=match.
- R50-A / Turn 22: expected=ACK_22, actual=ACK_22, completed=True, input_tokens=2368540, cached_input_tokens=2183296, output_tokens=1945, delta_input=+186,910, judgment=match.
- R50-A / Turn 23: expected=ACK_23, actual=ACK_23, completed=True, input_tokens=2563080, cached_input_tokens=2370176, output_tokens=1952, delta_input=+194,540, judgment=match.
- R50-A / Turn 24: expected=ACK_24, actual=ACK_24, completed=True, input_tokens=2765250, cached_input_tokens=2564608, output_tokens=1959, delta_input=+202,170, judgment=match.
- R50-A / Turn 25: expected=ACK_25, actual=ACK_25, completed=True, input_tokens=2975050, cached_input_tokens=2766720, output_tokens=2065, delta_input=+209,800, judgment=match.
- R50-A / Turn 26: expected=ACK_26, actual=ACK_26, completed=True, input_tokens=3192480, cached_input_tokens=2976384, output_tokens=2072, delta_input=+217,430, judgment=match.
- R50-A / Turn 27: expected=ACK_27, actual=ACK_27, completed=True, input_tokens=3417540, cached_input_tokens=3193728, output_tokens=2260, delta_input=+225,060, judgment=match.
- R50-A / Turn 28: expected=ACK_28, actual=ACK_28, completed=True, input_tokens=3650230, cached_input_tokens=3418752, output_tokens=2267, delta_input=+232,690, judgment=match.
- R50-A / Turn 29: expected=ACK_29, actual=ACK_29, completed=True, input_tokens=3890550, cached_input_tokens=3651328, output_tokens=2274, delta_input=+240,320, judgment=match.
- R50-A / Turn 30: expected=ACK_30, actual=ACK_30, completed=True, input_tokens=4138500, cached_input_tokens=3891584, output_tokens=2364, delta_input=+247,950, judgment=match.
- R50-A / Turn 31: expected=ACK_31, actual=ACK_31, completed=True, input_tokens=4294532, cached_input_tokens=3895040, output_tokens=2466, delta_input=+156,032, judgment=match.
- R50-A / Turn 32: expected=ACK_32, actual=ACK_32, completed=True, input_tokens=4458194, cached_input_tokens=4050944, output_tokens=2473, delta_input=+163,662, judgment=match.
- R50-A / Turn 33: expected=ACK_33, actual=ACK_33, completed=True, input_tokens=4629486, cached_input_tokens=4214528, output_tokens=2496, delta_input=+171,292, judgment=match.
- R50-A / Turn 34: expected=ACK_34, actual=ACK_34, completed=True, input_tokens=4808408, cached_input_tokens=4385792, output_tokens=2503, delta_input=+178,922, judgment=match.
- R50-A / Turn 35: expected=ACK_35, actual=ACK_35, completed=True, input_tokens=4994960, cached_input_tokens=4564608, output_tokens=2539, delta_input=+186,552, judgment=match.
- R50-A / Turn 36: expected=ACK_36, actual=ACK_36, completed=True, input_tokens=5189142, cached_input_tokens=4751104, output_tokens=2546, delta_input=+194,182, judgment=match.
- R50-A / Turn 37: expected=ACK_37, actual=ACK_37, completed=True, input_tokens=5390954, cached_input_tokens=4945152, output_tokens=2553, delta_input=+201,812, judgment=match.
- R50-A / Turn 38: expected=ACK_38, actual=ACK_38, completed=True, input_tokens=5600396, cached_input_tokens=5146880, output_tokens=2560, delta_input=+209,442, judgment=match.
- R50-A / Turn 39: expected=ACK_39, actual=ACK_39, completed=True, input_tokens=5817468, cached_input_tokens=5356288, output_tokens=2567, delta_input=+217,072, judgment=match.
- R50-A / Turn 40: expected=ACK_40, actual=ACK_40, completed=True, input_tokens=6042170, cached_input_tokens=5573248, output_tokens=2574, delta_input=+224,702, judgment=match.
- R50-A / Turn 41: expected=ACK_41, actual=ACK_41, completed=True, input_tokens=6274502, cached_input_tokens=5797888, output_tokens=2581, delta_input=+232,332, judgment=match.
- R50-A / Turn 42: expected=ACK_42, actual=ACK_42, completed=True, input_tokens=6514464, cached_input_tokens=6030080, output_tokens=2588, delta_input=+239,962, judgment=match.
- R50-A / Turn 43: expected=ACK_43, actual=ACK_43, completed=True, input_tokens=6762056, cached_input_tokens=6269952, output_tokens=2595, delta_input=+247,592, judgment=match.
- R50-A / Turn 44: expected=ACK_44, actual=ACK_44, completed=True, input_tokens=6918048, cached_input_tokens=6273408, output_tokens=2620, delta_input=+155,992, judgment=match.
- R50-A / Turn 45: expected=ACK_45, actual=ACK_45, completed=True, input_tokens=7081670, cached_input_tokens=6429312, output_tokens=2627, delta_input=+163,622, judgment=match.
- R50-A / Turn 46: expected=ACK_46, actual=ACK_46, completed=True, input_tokens=7252922, cached_input_tokens=6592896, output_tokens=2650, delta_input=+171,252, judgment=match.
- R50-A / Turn 47: expected=ACK_47, actual=ACK_47, completed=True, input_tokens=7431804, cached_input_tokens=6764032, output_tokens=2673, delta_input=+178,882, judgment=match.
- R50-A / Turn 48: expected=ACK_48, actual=ACK_48, completed=True, input_tokens=7618316, cached_input_tokens=6942848, output_tokens=2759, delta_input=+186,512, judgment=match.
- R50-A / Turn 49: expected=TOKEN, actual=CP_coarse_50_1_20260211, completed=True, input_tokens=7812457, cached_input_tokens=7129216, output_tokens=2863, delta_input=+194,141, judgment=match.

### R50-B Detailed Verbatim Log
- R50-B / Turn 00: expected=STORED, actual=STORED, completed=True, input_tokens=19049, cached_input_tokens=3456, output_tokens=176, delta_input=initial, judgment=match.
- R50-B / Turn 01: expected=ACK_1, actual=ACK_1, completed=True, input_tokens=45728, cached_input_tokens=22400, output_tokens=340, delta_input=+26,679, judgment=match.
- R50-B / Turn 02: expected=ACK_2, actual=ACK_2, completed=True, input_tokens=80037, cached_input_tokens=49024, output_tokens=430, delta_input=+34,309, judgment=match.
- R50-B / Turn 03: expected=ACK_3, actual=ACK_3, completed=True, input_tokens=121976, cached_input_tokens=83200, output_tokens=499, delta_input=+41,939, judgment=match.
- R50-B / Turn 04: expected=ACK_4, actual=ACK_4, completed=True, input_tokens=171545, cached_input_tokens=125056, output_tokens=630, delta_input=+49,569, judgment=match.
- R50-B / Turn 05: expected=ACK_5, actual=ACK_5, completed=True, input_tokens=228744, cached_input_tokens=174592, output_tokens=722, delta_input=+57,199, judgment=match.
- R50-B / Turn 06: expected=ACK_6, actual=ACK_6, completed=True, input_tokens=293573, cached_input_tokens=231680, output_tokens=758, delta_input=+64,829, judgment=match.
- R50-B / Turn 07: expected=ACK_7, actual=ACK_7, completed=True, input_tokens=366032, cached_input_tokens=296448, output_tokens=814, delta_input=+72,459, judgment=match.
- R50-B / Turn 08: expected=ACK_8, actual=ACK_8, completed=True, input_tokens=446121, cached_input_tokens=368768, output_tokens=849, delta_input=+80,089, judgment=match.
- R50-B / Turn 09: expected=ACK_9, actual=ACK_9, completed=True, input_tokens=533840, cached_input_tokens=448768, output_tokens=932, delta_input=+87,719, judgment=match.
- R50-B / Turn 10: expected=ACK_10, actual=ACK_10, completed=True, input_tokens=629189, cached_input_tokens=536448, output_tokens=991, delta_input=+95,349, judgment=match.
- R50-B / Turn 11: expected=ACK_11, actual=ACK_11, completed=True, input_tokens=732168, cached_input_tokens=631680, output_tokens=1079, delta_input=+102,979, judgment=match.
- R50-B / Turn 12: expected=ACK_12, actual=ACK_12, completed=True, input_tokens=842777, cached_input_tokens=734592, output_tokens=1159, delta_input=+110,609, judgment=match.
- R50-B / Turn 13: expected=ACK_13, actual=ACK_13, completed=True, input_tokens=961016, cached_input_tokens=845056, output_tokens=1211, delta_input=+118,239, judgment=match.
- R50-B / Turn 14: expected=ACK_14, actual=ACK_14, completed=True, input_tokens=1086885, cached_input_tokens=963200, output_tokens=1218, delta_input=+125,869, judgment=match.
- R50-B / Turn 15: expected=ACK_15, actual=ACK_15, completed=True, input_tokens=1220384, cached_input_tokens=1089024, output_tokens=1308, delta_input=+133,499, judgment=match.
- R50-B / Turn 16: expected=ACK_16, actual=ACK_16, completed=True, input_tokens=1361513, cached_input_tokens=1222400, output_tokens=1404, delta_input=+141,129, judgment=match.
- R50-B / Turn 17: expected=ACK_17, actual=ACK_17, completed=True, input_tokens=1510272, cached_input_tokens=1363456, output_tokens=1465, delta_input=+148,759, judgment=match.
- R50-B / Turn 18: expected=ACK_18, actual=ACK_18, completed=True, input_tokens=1666661, cached_input_tokens=1512192, output_tokens=1531, delta_input=+156,389, judgment=match.
- R50-B / Turn 19: expected=ACK_19, actual=ACK_19, completed=True, input_tokens=1830680, cached_input_tokens=1668480, output_tokens=1642, delta_input=+164,019, judgment=match.
- R50-B / Turn 20: expected=ACK_20, actual=ACK_20, completed=True, input_tokens=2002329, cached_input_tokens=1832448, output_tokens=1685, delta_input=+171,649, judgment=match.
- R50-B / Turn 21: expected=ACK_21, actual=ACK_21, completed=True, input_tokens=2181608, cached_input_tokens=2003968, output_tokens=1692, delta_input=+179,279, judgment=match.
- R50-B / Turn 22: expected=ACK_22, actual=ACK_22, completed=True, input_tokens=2368517, cached_input_tokens=2183168, output_tokens=1782, delta_input=+186,909, judgment=match.
- R50-B / Turn 23: expected=ACK_23, actual=ACK_23, completed=True, input_tokens=2563056, cached_input_tokens=2370048, output_tokens=1825, delta_input=+194,539, judgment=match.
- R50-B / Turn 24: expected=ACK_24, actual=ACK_24, completed=True, input_tokens=2765225, cached_input_tokens=2564480, output_tokens=1901, delta_input=+202,169, judgment=match.
- R50-B / Turn 25: expected=ACK_25, actual=ACK_25, completed=True, input_tokens=2975024, cached_input_tokens=2766592, output_tokens=2022, delta_input=+209,799, judgment=match.
- R50-B / Turn 26: expected=ACK_26, actual=ACK_26, completed=True, input_tokens=3192453, cached_input_tokens=2976256, output_tokens=2048, delta_input=+217,429, judgment=match.
- R50-B / Turn 27: expected=ACK_27, actual=ACK_27, completed=True, input_tokens=3417512, cached_input_tokens=3193600, output_tokens=2055, delta_input=+225,059, judgment=match.
- R50-B / Turn 28: expected=ACK_28, actual=ACK_28, completed=True, input_tokens=3650201, cached_input_tokens=3418624, output_tokens=2062, delta_input=+232,689, judgment=match.
- R50-B / Turn 29: expected=ACK_29, actual=ACK_29, completed=True, input_tokens=3890520, cached_input_tokens=3651200, output_tokens=2069, delta_input=+240,319, judgment=match.
- R50-B / Turn 30: expected=ACK_30, actual=ACK_30, completed=True, input_tokens=4138469, cached_input_tokens=3891456, output_tokens=2145, delta_input=+247,949, judgment=match.
- R50-B / Turn 31: expected=ACK_31, actual=ACK_31, completed=True, input_tokens=4294449, cached_input_tokens=3894912, output_tokens=2191, delta_input=+155,980, judgment=match.
- R50-B / Turn 32: expected=ACK_32, actual=ACK_32, completed=True, input_tokens=4458059, cached_input_tokens=4050816, output_tokens=2221, delta_input=+163,610, judgment=match.
- R50-B / Turn 33: expected=ACK_33, actual=ACK_33, completed=True, input_tokens=4629299, cached_input_tokens=4214400, output_tokens=2252, delta_input=+171,240, judgment=match.
- R50-B / Turn 34: expected=ACK_34, actual=ACK_34, completed=True, input_tokens=4808169, cached_input_tokens=4385536, output_tokens=2280, delta_input=+178,870, judgment=match.
- R50-B / Turn 35: expected=ACK_35, actual=ACK_35, completed=True, input_tokens=4994669, cached_input_tokens=4564352, output_tokens=2315, delta_input=+186,500, judgment=match.
- R50-B / Turn 36: expected=ACK_36, actual=ACK_36, completed=True, input_tokens=5188799, cached_input_tokens=4750720, output_tokens=2349, delta_input=+194,130, judgment=match.
- R50-B / Turn 37: expected=ACK_37, actual=ACK_37, completed=True, input_tokens=5390559, cached_input_tokens=4944768, output_tokens=2356, delta_input=+201,760, judgment=match.
- R50-B / Turn 38: expected=ACK_38, actual=ACK_38, completed=True, input_tokens=5599949, cached_input_tokens=5146496, output_tokens=2363, delta_input=+209,390, judgment=match.
- R50-B / Turn 39: expected=ACK_39, actual=ACK_39, completed=True, input_tokens=5816969, cached_input_tokens=5355776, output_tokens=2370, delta_input=+217,020, judgment=match.
- R50-B / Turn 40: expected=ACK_40, actual=ACK_40, completed=True, input_tokens=6041619, cached_input_tokens=5572736, output_tokens=2377, delta_input=+224,650, judgment=match.
- R50-B / Turn 41: expected=ACK_41, actual=ACK_41, completed=True, input_tokens=6273899, cached_input_tokens=5797248, output_tokens=2384, delta_input=+232,280, judgment=match.
- R50-B / Turn 42: expected=ACK_42, actual=ACK_42, completed=True, input_tokens=6513809, cached_input_tokens=6029440, output_tokens=2391, delta_input=+239,910, judgment=match.
- R50-B / Turn 43: expected=ACK_43, actual=ACK_43, completed=True, input_tokens=6761349, cached_input_tokens=6269312, output_tokens=2398, delta_input=+247,540, judgment=match.
- R50-B / Turn 44: expected=ACK_44, actual=ACK_44, completed=True, input_tokens=6917328, cached_input_tokens=6272768, output_tokens=2491, delta_input=+155,979, judgment=match.
- R50-B / Turn 45: expected=ACK_45, actual=ACK_45, completed=True, input_tokens=7080937, cached_input_tokens=6428672, output_tokens=2562, delta_input=+163,609, judgment=match.
- R50-B / Turn 46: expected=ACK_46, actual=ACK_46, completed=True, input_tokens=7252176, cached_input_tokens=6592256, output_tokens=2604, delta_input=+171,239, judgment=match.
- R50-B / Turn 47: expected=ACK_47, actual=ACK_47, completed=True, input_tokens=7431045, cached_input_tokens=6763392, output_tokens=2611, delta_input=+178,869, judgment=match.
- R50-B / Turn 48: expected=ACK_48, actual=ACK_48, completed=True, input_tokens=7617544, cached_input_tokens=6942208, output_tokens=2649, delta_input=+186,499, judgment=match.
- R50-B / Turn 49: expected=TOKEN, actual=CP_focus_50_2_20260211, completed=True, input_tokens=7811672, cached_input_tokens=7128576, output_tokens=2816, delta_input=+194,128, judgment=match.

### R50-C Detailed Verbatim Log
- R50-C / Turn 00: expected=STORED, actual=STORED, completed=True, input_tokens=19049, cached_input_tokens=3456, output_tokens=279, delta_input=initial, judgment=match.
- R50-C / Turn 01: expected=ACK_1, actual=ACK_1, completed=True, input_tokens=45728, cached_input_tokens=22400, output_tokens=440, delta_input=+26,679, judgment=match.
- R50-C / Turn 02: expected=ACK_2, actual=ACK_2, completed=True, input_tokens=80037, cached_input_tokens=49024, output_tokens=496, delta_input=+34,309, judgment=match.
- R50-C / Turn 03: expected=ACK_3, actual=ACK_3, completed=True, input_tokens=121976, cached_input_tokens=83200, output_tokens=607, delta_input=+41,939, judgment=match.
- R50-C / Turn 04: expected=ACK_4, actual=ACK_4, completed=True, input_tokens=171545, cached_input_tokens=125056, output_tokens=681, delta_input=+49,569, judgment=match.
- R50-C / Turn 05: expected=ACK_5, actual=ACK_5, completed=True, input_tokens=228744, cached_input_tokens=174592, output_tokens=734, delta_input=+57,199, judgment=match.
- R50-C / Turn 06: expected=ACK_6, actual=ACK_6, completed=True, input_tokens=293573, cached_input_tokens=231680, output_tokens=792, delta_input=+64,829, judgment=match.
- R50-C / Turn 07: expected=ACK_7, actual=ACK_7, completed=True, input_tokens=366032, cached_input_tokens=296448, output_tokens=835, delta_input=+72,459, judgment=match.
- R50-C / Turn 08: expected=ACK_8, actual=ACK_8, completed=True, input_tokens=446121, cached_input_tokens=368768, output_tokens=913, delta_input=+80,089, judgment=match.
- R50-C / Turn 09: expected=ACK_9, actual=ACK_9, completed=True, input_tokens=533840, cached_input_tokens=448768, output_tokens=997, delta_input=+87,719, judgment=match.
- R50-C / Turn 10: expected=ACK_10, actual=ACK_10, completed=True, input_tokens=629189, cached_input_tokens=536448, output_tokens=1066, delta_input=+95,349, judgment=match.
- R50-C / Turn 11: expected=ACK_11, actual=ACK_11, completed=True, input_tokens=732168, cached_input_tokens=631680, output_tokens=1138, delta_input=+102,979, judgment=match.
- R50-C / Turn 12: expected=ACK_12, actual=ACK_12, completed=True, input_tokens=842777, cached_input_tokens=734592, output_tokens=1255, delta_input=+110,609, judgment=match.
- R50-C / Turn 13: expected=ACK_13, actual=ACK_13, completed=True, input_tokens=961016, cached_input_tokens=845056, output_tokens=1341, delta_input=+118,239, judgment=match.
- R50-C / Turn 14: expected=ACK_14, actual=ACK_14, completed=True, input_tokens=1086885, cached_input_tokens=963200, output_tokens=1402, delta_input=+125,869, judgment=match.
- R50-C / Turn 15: expected=ACK_15, actual=ACK_15, completed=True, input_tokens=1220384, cached_input_tokens=1089024, output_tokens=1467, delta_input=+133,499, judgment=match.
- R50-C / Turn 16: expected=ACK_16, actual=ACK_16, completed=True, input_tokens=1361513, cached_input_tokens=1222400, output_tokens=1474, delta_input=+141,129, judgment=match.
- R50-C / Turn 17: expected=ACK_17, actual=ACK_17, completed=True, input_tokens=1510272, cached_input_tokens=1363456, output_tokens=1520, delta_input=+148,759, judgment=match.
- R50-C / Turn 18: expected=ACK_18, actual=ACK_18, completed=True, input_tokens=1666661, cached_input_tokens=1512192, output_tokens=1527, delta_input=+156,389, judgment=match.
- R50-C / Turn 19: expected=ACK_19, actual=ACK_19, completed=True, input_tokens=1830680, cached_input_tokens=1668480, output_tokens=1595, delta_input=+164,019, judgment=match.
- R50-C / Turn 20: expected=ACK_20, actual=ACK_20, completed=True, input_tokens=2002329, cached_input_tokens=1832448, output_tokens=1769, delta_input=+171,649, judgment=match.
- R50-C / Turn 21: expected=ACK_21, actual=ACK_21, completed=True, input_tokens=2181608, cached_input_tokens=2003968, output_tokens=1802, delta_input=+179,279, judgment=match.
- R50-C / Turn 22: expected=ACK_22, actual=ACK_22, completed=True, input_tokens=2368517, cached_input_tokens=2183168, output_tokens=1809, delta_input=+186,909, judgment=match.
- R50-C / Turn 23: expected=ACK_23, actual=ACK_23, completed=True, input_tokens=2563056, cached_input_tokens=2370048, output_tokens=1816, delta_input=+194,539, judgment=match.
- R50-C / Turn 24: expected=ACK_24, actual=ACK_24, completed=True, input_tokens=2765225, cached_input_tokens=2564480, output_tokens=1914, delta_input=+202,169, judgment=match.
- R50-C / Turn 25: expected=ACK_25, actual=ACK_25, completed=True, input_tokens=2975024, cached_input_tokens=2766592, output_tokens=2003, delta_input=+209,799, judgment=match.
- R50-C / Turn 26: expected=ACK_26, actual=ACK_26, completed=True, input_tokens=3192453, cached_input_tokens=2976256, output_tokens=2133, delta_input=+217,429, judgment=match.
- R50-C / Turn 27: expected=ACK_27, actual=ACK_27, completed=True, input_tokens=3417512, cached_input_tokens=3193600, output_tokens=2140, delta_input=+225,059, judgment=match.
- R50-C / Turn 28: expected=ACK_28, actual=ACK_28, completed=True, input_tokens=3650201, cached_input_tokens=3418624, output_tokens=2147, delta_input=+232,689, judgment=match.
- R50-C / Turn 29: expected=ACK_29, actual=ACK_29, completed=True, input_tokens=3890520, cached_input_tokens=3651200, output_tokens=2154, delta_input=+240,319, judgment=match.
- R50-C / Turn 30: expected=ACK_30, actual=ACK_30, completed=True, input_tokens=4138469, cached_input_tokens=3891456, output_tokens=2234, delta_input=+247,949, judgment=match.
- R50-C / Turn 31: expected=ACK_31, actual=ACK_31, completed=True, input_tokens=4294468, cached_input_tokens=3894912, output_tokens=2342, delta_input=+155,999, judgment=match.
- R50-C / Turn 32: expected=ACK_32, actual=ACK_32, completed=True, input_tokens=4458097, cached_input_tokens=4050816, output_tokens=2367, delta_input=+163,629, judgment=match.
- R50-C / Turn 33: expected=ACK_33, actual=ACK_33, completed=True, input_tokens=4629356, cached_input_tokens=4214400, output_tokens=2397, delta_input=+171,259, judgment=match.
- R50-C / Turn 34: expected=ACK_34, actual=ACK_34, completed=True, input_tokens=4808245, cached_input_tokens=4385536, output_tokens=2442, delta_input=+178,889, judgment=match.
- R50-C / Turn 35: expected=ACK_35, actual=ACK_35, completed=True, input_tokens=4994764, cached_input_tokens=4564352, output_tokens=2449, delta_input=+186,519, judgment=match.
- R50-C / Turn 36: expected=ACK_36, actual=ACK_36, completed=True, input_tokens=5188913, cached_input_tokens=4750848, output_tokens=2480, delta_input=+194,149, judgment=match.
- R50-C / Turn 37: expected=ACK_37, actual=ACK_37, completed=True, input_tokens=5390692, cached_input_tokens=4944896, output_tokens=2487, delta_input=+201,779, judgment=match.
- R50-C / Turn 38: expected=ACK_38, actual=ACK_38, completed=True, input_tokens=5600101, cached_input_tokens=5146624, output_tokens=2494, delta_input=+209,409, judgment=match.
- R50-C / Turn 39: expected=ACK_39, actual=ACK_39, completed=True, input_tokens=5817140, cached_input_tokens=5355904, output_tokens=2501, delta_input=+217,039, judgment=match.
- R50-C / Turn 40: expected=ACK_40, actual=ACK_40, completed=True, input_tokens=6041809, cached_input_tokens=5572864, output_tokens=2570, delta_input=+224,669, judgment=match.
- R50-C / Turn 41: expected=ACK_41, actual=ACK_41, completed=True, input_tokens=6274108, cached_input_tokens=5797504, output_tokens=2597, delta_input=+232,299, judgment=match.
- R50-C / Turn 42: expected=ACK_42, actual=ACK_42, completed=True, input_tokens=6514037, cached_input_tokens=6029696, output_tokens=2604, delta_input=+239,929, judgment=match.
- R50-C / Turn 43: expected=ACK_43, actual=ACK_43, completed=True, input_tokens=6761596, cached_input_tokens=6269568, output_tokens=2611, delta_input=+247,559, judgment=match.
- R50-C / Turn 44: expected=ACK_44, actual=ACK_44, completed=True, input_tokens=6917547, cached_input_tokens=6280192, output_tokens=2638, delta_input=+155,951, judgment=match.
- R50-C / Turn 45: expected=ACK_45, actual=ACK_45, completed=True, input_tokens=7081128, cached_input_tokens=6436096, output_tokens=2661, delta_input=+163,581, judgment=match.
- R50-C / Turn 46: expected=ACK_46, actual=ACK_46, completed=True, input_tokens=7252339, cached_input_tokens=6599552, output_tokens=2668, delta_input=+171,211, judgment=match.
- R50-C / Turn 47: expected=ACK_47, actual=ACK_47, completed=True, input_tokens=7431180, cached_input_tokens=6770688, output_tokens=2675, delta_input=+178,841, judgment=match.
- R50-C / Turn 48: expected=ACK_48, actual=ACK_48, completed=True, input_tokens=7617651, cached_input_tokens=6949504, output_tokens=2682, delta_input=+186,471, judgment=match.
- R50-C / Turn 49: expected=TOKEN, actual=ACK_49, completed=True, input_tokens=7811751, cached_input_tokens=7135872, output_tokens=3731, delta_input=+194,100, judgment=mismatch (sequence shift in final recall).

### Cross-verbatim Summary Findings
- Across all three runs, the average between-turn increase in input_tokens was 159,039.0 tokens/turn.
- Increments are not strict constants; they vary by turn due to cache state, response length, and internal processing fluctuation.
- In the failing run (R50-C), intermediate ACK sequence consistency is preserved while only final token retrieval falls to `ACK_49`, suggesting priority inversion in reference selection rather than complete forgetting.

## 15. Appendix B: Full Statistical Procedure Description and Re-analysis Perspectives
### 15.1 Success-rate Interval Estimation (Wilson)
Wilson intervals were adopted because under small-sample conditions, Wald intervals can become overly optimistic or pessimistic.
In this experiment, n=1,2,3 are mixed, and 95% CI width directly affects interpretation, so interval estimates were shown alongside the main tables.

### 15.2 Auxiliary Use of One-sided Binomial Tail Probability
Against the operational target success rate of 80% at 50 turns, the observed 2/3 appears insufficient intuitively, but statistical power is low at n=3.
Therefore, this report does not claim a formal rejection decision and instead presents it as auxiliary evidence of insufficient operational safety margin.

### 15.3 Positioning of Regression (Descriptive, Not Causal)
The regression equations in this report are not predictors that guarantee future values; they are trend-compression summaries within the observed range.
In particular, long-text duration regression has low R^2, indicating that character count alone does not explain latency.

### 15.4 Re-evaluation Design for Production Operation
1. Re-evaluate the 50-turn range with at least N=20 repetitions, and decide Go/No-Go based on the CI lower bound.
2. For long text, include not only extraction tasks but also constrained reasoning tasks.
3. Treat intervention presence/absence (checkpoint/restate) as an experimental factor, and judge effects by absolute failure-rate improvement.
4. Set monitoring thresholds for context usage; when final input tokens exceed the threshold, automatically insert summarization/compression.

## 16. Appendix C: Detailed Discussion (Long Form)
### C-1
The central contribution of this study is not just reporting a success rate, but identifying the shape of failure. LLM evaluation is often reduced to a pass/fail binary, but in production the critical issue is failure structure. The failure observed here was neither unrelated-token spew nor grammatical collapse; it was a type where only final reference deviated while sequence consistency was maintained. This implies high potential for operational mitigation. In other words, prompt design and state re-anchoring (restate) at turn boundaries may reduce failure rates to a practical range.

### C-2
The long-text validation results look very strong at first glance. However, the task here is marker extraction, with shallow reasoning depth. Therefore, generalizing to 300,000 characters is fine should be avoided; the scientifically valid statement is the narrower one: no failures observed for 300,000-character extraction tasks. In higher-order reasoning tasks such as consistency checks across multiple constraints, exception-rule priority decisions, and contradictory-document integration, task complexity may dominate input length.

### C-3
For context usage, the final multi-turn step appears to increase exponentially, but there are only four observation points (20/30/40/50), so a high-R^2 linear approximation itself is not surprising. More important than coefficient values is the fact that scale reaches about 7.8M tokens at 50 turns. In production, workflow design should introduce context compression and state re-baselining before reaching this scale, and threshold control (token-budget policy) should be standardized.

### C-4
The difference between failing and successful runs is small even at the surface-response level. Intermediate ACK sequences look nearly identical, with divergence only at the final point. This can be interpreted as a near-critical phenomenon: internal reference competition sits near threshold, and slight condition differences (cache state, response length, internal search path) flip the final choice. Near criticality, single trials are weak evidence; repeated testing and distribution-level evaluation are essential.

### C-5
Operationally, it is important to introduce failure-type labeling into evaluation design. Beyond overall success rate, separately tracking final_recall failures, mid_turn failures, and init failures allows rational prioritization of mitigations. In this dataset, failures are concentrated at final_recall, so mitigations should focus on end-turn reinforcement (re-explicit final turn, short restatement, double-check prompts).

### C-6
For long-text performance judgments, not only averages but also worst-case latency (p95/p99) must be incorporated. With the present sample size, high-quantile estimation is difficult, but future experiments should increase N per condition and evaluate in alignment with operational SLOs. Especially in batch/parallel environments, queue delay and execution delay are mixed, so decomposed measurement (wait time/execution time) is desirable.

### C-7
Finally, these results directly affect decisions on adopting Codex-led workflows. Stability at <=40 turns is sufficiently usable for workflow design, while handling 50+ turns should include design-side aids (checkpoint/restate, summarization, validation loops). In practice, the shortest path is not to assume model performance, but to design workflows around how the model fails.

### C-8
For future high-precision research, it is effective to repeat the same task across multiple models, temperatures, and execution time windows, then separate variance components with mixed-effects models. This allows simultaneous handling of model differences, task differences, time differences, and cache differences, and quantifies where uncertainty is largest. It is an important step toward design-relevant statistics beyond simple mean comparisons.

### C-9
Before deployment into production, not only correct answers but also safe wrong answers should be defined. For example, even if final-token recall fails, returning the latest ACK may bound damage in some cases. By contrast, for tasks involving confidential information or external side effects, the same failure type can directly cause major incidents. Therefore, evaluation metrics should be weighted by task risk, and decision rules should explicitly state that acceptability can differ even at the same 66.7%.

### C-10
In this way, the value of this report is not a single success-rate number, but the conversion of findings into deployable operational design. Identify boundary zones, capture failure types, and map them into assistive design. Continuously cycling these three steps maintains quality despite model updates and environmental change. Evaluation should not be a one-time ritual; it should be built in as part of the system.
