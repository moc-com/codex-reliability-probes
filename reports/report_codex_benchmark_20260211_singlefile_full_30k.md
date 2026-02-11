# 大規模コンテキスト下における Codex 信頼性評価レポート（完全版・単一MD）

- 作成時刻（UTC）: 2026-02-11T04:58:42Z
- レポート特性: 単一ファイル完結、検証データ内包、個人特定情報および絶対パスを本文から除去
- モデル: gpt-5.3-codex（環境マニフェスト由来） [S7]

## 要旨
本報告は、Codex 運用における2つの実務的ボトルネック、すなわち (i) 多ターン連続対話での最終想起信頼性、(ii) 超長文入力での厳密抽出精度と処理時間、を定量的に評価した。評価は再現可能な決定論的プロトコルで実施し、結果を strict 一致で判定した。 [S1][S4][S8][S9]

主要結果は次の通りである。
1. 20/30/40 turns は strict 100%（ただし n=1 で不確実性は広い）。 [S1][S2]
2. 50 turns は 3 試行中 2 成功（66.7%）。失敗は final recall で、期待トークンではなく `ACK_49` が返る recency slip であった。 [S1]
3. 長文抽出（5,000→300,000 chars）は全条件 2/2 成功（100%）で、処理時間は 8-11 秒帯。 [S4][S5]
4. コンテキスト使用量は multi-turn 最終ターンで急増し、50 turns の平均 final input は約 7.81M tokens に到達。 [S3]

本稿は、これらの結果を「どの条件で壊れやすいか」「なぜ壊れるか」「次に何を検証すべきか」の観点で機序仮説まで拡張して記述する。

## 1. 研究目的と研究課題
### 1.1 研究目的
運用現場で再現可能な品質ゲートを構築するため、以下を明らかにする。
- RQ1: 50 turns 以内での multi-turn 記憶信頼性はどこまで維持されるか。
- RQ2: 300,000 chars 級入力での厳密抽出精度と遅延は実用域にあるか。
- RQ3: 失敗はランダム破綻か、構造的（説明可能）エラーパターンか。

### 1.2 事前仮説（作業仮説）
- H1: 20-40 turns は >=95% で通過する。
- H2: 50 turns でも >=80% を維持する。
- H3: 入力長増加とともに遅延増・精度低下が顕在化する。

## 2. 実験方法
### 2.1 多ターン記憶試験（Primary endpoint: <=50 turns）
プロトコル:
1. Turn 0: 一意トークンを保存させ、`STORED` を厳密返答。
2. Turn 1..(N-2): `ACK_t` を厳密返答。
3. Turn N-1: 初回保存トークンのみ返答（最終想起）。

判定:
- strict_pass: 完全一致。
- semantic_pass: 正規化一致（補助）。
- failure_stage: init / mid_turn / final_recall。

### 2.2 長文抽出試験（5,000-300,000 chars）
プロトコル:
1. 長文本文に `<<TOKEN:...>>` を埋め込む。
2. 「トークン値のみ」を返答させる。
3. 各長さで2試行。

判定: strict一致、duration、input/cached/output token usage。

### 2.3 統計手法
- 成功率区間: Wilson 95% CI。
- 50-turn 仮説補助検定: `P(X<=k | n, p0)` の片側二項尾確率。
- 記述回帰: 線形回帰（説明用、因果推定ではない）。

## 3. 集計結果（要約）
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

## 4. コンテキスト使用量の精密分析
### 4.1 Multi-turn の init/final 使用量
| turns | n | avg_init_input | avg_init_cached | avg_init_output | avg_final_input | avg_final_cached | avg_final_output | final_cached/input |
|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 19,050.0 | 3,456.0 | 188.0 | 1,830,699.0 | 1,547,136.0 | 2,126.0 | 0.8451 |
| 30 | 1 | 19,050.0 | 17,152.0 | 190.0 | 3,890,549.0 | 3,641,856.0 | 1,908.0 | 0.9361 |
| 40 | 1 | 19,050.0 | 16,768.0 | 84.0 | 5,817,242.0 | 5,283,712.0 | 2,605.0 | 0.9083 |
| 50 | 3 | 19,049.3 | 3,456.0 | 197.7 | 7,811,960.0 | 7,131,221.3 | 3,136.7 | 0.9129 |

観察: final input tokens は turns 増加に対して急増し、50 turns で約 7.81M tokens。これは 20 turns の約4.27倍である。 [S3]

### 4.2 Long-context の使用量
| length_chars | n | avg_input_tokens | avg_cached_input_tokens | avg_output_tokens |
|---|---|---|---|---|
| 5,000 | 2 | 18,219.0 | 10,112.0 | 140.5 |
| 10,000 | 2 | 19,156.0 | 10,112.0 | 101.5 |
| 15,000 | 2 | 20,094.0 | 3,456.0 | 131.0 |
| 20,000 | 2 | 21,031.0 | 16,768.0 | 112.0 |
| 300,000 | 2 | 73,531.0 | 3,456.0 | 166.0 |

観察: 300,000 chars の平均 input は 73,531 tokens。cached は実行条件の影響を受け、長さに単調比例しない。 [S6]

## 5. 仮説と観測の差分（Gap Analysis）
- H1（20-40 turns >=95%）: 支持。観測は100%。 [S2]
- H2（50 turns >=80%）: 不支持。観測66.7%（差分 -13.3pt）。 [S2]
- H3（長文化で劣化）: 今回タスクでは不支持（失敗未観測、遅延増も弱い）。 [S5]
- 50-turn補助計算: P(X<=2|n=3,p=0.8)=0.488。サンプル小のため強い棄却根拠ではないが、設計目標80%に対し余裕が薄いことを示す。 [S1]
- 長文側（n=10, 失敗0）での rule-of-three 上限失敗率は約 30.0%。100%成功の見かけ値を過信すべきではない。 [S4]

## 6. 記述回帰とスケーリング
### 6.1 Multi-turn final input vs turns
- 回帰式: `final_input_tokens = 198,704.76 * turns + (-2,117,054.10)`
- 決定係数: `R^2 = 0.999844`
- 記述予測（55 turns）: `8,811,707.7` tokens

### 6.2 Long input_tokens vs chars
- 回帰式: `input_tokens = 0.187499094 * chars + (17,281.2634)`
- 決定係数: `R^2 = 0.999999999895`
- 記述予測（500k chars）: `111,030.8` tokens
- 記述予測（1M chars）: `204,780.4` tokens

### 6.3 duration vs chars
- 回帰式: `duration_sec = 0.000001169811 * chars + (9.6181)`
- 決定係数: `R^2 = 0.113325`
解釈: この範囲では長さ単独の時間寄与は弱く、タスク複雑性や実行環境要因の寄与が支配的と考えられる。

## 7. 失敗機序の詳細
| fail_stage | note | count |
|---|---|---|
| final_recall | final_recall_semantic_mismatch_or_timeout | 1 |

唯一の観測失敗は final_recall で、返答が `ACK_49` となった。これは「無関連トークンへの崩壊」ではなく「系列保持下での最終参照誤り」であり、recency 側への引力（recency attractor）を示唆する。 [S1][S10]

## 8. 長文試験の効率指標（試行別）
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

## 9. 生データ（本文内完全展開）
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

## 10. 50-turn 3ランの各ターン推移（150行）
注: expected列の `TOKEN` は最終想起ターンで保存トークンを期待することを意味する。

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

## 11. 妥当性と限界
1. 条件ごとの試行数が小さい（n=1〜3, n=2）ため、CI幅は広い。
2. 長文課題は抽出中心であり、推論中心タスクへの外挿は慎重であるべき。
3. cached token はセッション状態依存であり、入力長単独で一意に決まらない。
4. 本報告の回帰は記述モデルであり、因果解釈を意図しない。

## 12. 実務的含意と次段計画
### 12.1 実務的含意
- 安全域: <=40 turns を基本運用域とする。
- 50 turns 運用: checkpoint/restate 等の介入なしでは再現性リスクあり。
- 300k長文: 抽出タスクでは実用可能性が高いが、推論複雑タスクの追加検証が必須。

### 12.2 次段実験（高精度化）
1. 境界鋭化: 42/45/48/50/52 turns, 各 N>=20。
2. 介入比較: 10-turn毎 checkpoint/restate 有無のA/B比較。
3. 複雑度ラダー: 抽出 -> 制約検索 -> 2-hop参照 -> 多制約推論。
4. token-budget 操作: turns固定で冗長情報量を増減し、失敗率曲線を推定。

## 13. 出典（匿名化ID）
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

## 14. 付録A: 50ターン3ランの逐語的ターン解釈（詳細ログ解説）
本節は、本文表の数値を人手検証しやすいよう、各ターンを1行ずつ自然言語で解説する。
表形式だけでは見落としやすい「増分の揺らぎ」「最終ターンの回収挙動」「応答パターンの連続性」を、試行単位で明示した。

### R50-A 詳細逐語ログ
- R50-A / Turn 00: expected=STORED, actual=STORED, completed=True, input_tokens=19050, cached_input_tokens=3456, output_tokens=138, delta_input=initial, 判定=一致。
- R50-A / Turn 01: expected=ACK_1, actual=ACK_1, completed=True, input_tokens=45730, cached_input_tokens=22400, output_tokens=299, delta_input=+26,680, 判定=一致。
- R50-A / Turn 02: expected=ACK_2, actual=ACK_2, completed=True, input_tokens=80040, cached_input_tokens=49024, output_tokens=423, delta_input=+34,310, 判定=一致。
- R50-A / Turn 03: expected=ACK_3, actual=ACK_3, completed=True, input_tokens=121980, cached_input_tokens=83200, output_tokens=526, delta_input=+41,940, 判定=一致。
- R50-A / Turn 04: expected=ACK_4, actual=ACK_4, completed=True, input_tokens=171550, cached_input_tokens=125056, output_tokens=605, delta_input=+49,570, 判定=一致。
- R50-A / Turn 05: expected=ACK_5, actual=ACK_5, completed=True, input_tokens=228750, cached_input_tokens=174592, output_tokens=631, delta_input=+57,200, 判定=一致。
- R50-A / Turn 06: expected=ACK_6, actual=ACK_6, completed=True, input_tokens=293580, cached_input_tokens=231680, output_tokens=717, delta_input=+64,830, 判定=一致。
- R50-A / Turn 07: expected=ACK_7, actual=ACK_7, completed=True, input_tokens=366040, cached_input_tokens=296448, output_tokens=806, delta_input=+72,460, 判定=一致。
- R50-A / Turn 08: expected=ACK_8, actual=ACK_8, completed=True, input_tokens=446130, cached_input_tokens=368768, output_tokens=908, delta_input=+80,090, 判定=一致。
- R50-A / Turn 09: expected=ACK_9, actual=ACK_9, completed=True, input_tokens=533850, cached_input_tokens=448768, output_tokens=1047, delta_input=+87,720, 判定=一致。
- R50-A / Turn 10: expected=ACK_10, actual=ACK_10, completed=True, input_tokens=629200, cached_input_tokens=536448, output_tokens=1128, delta_input=+95,350, 判定=一致。
- R50-A / Turn 11: expected=ACK_11, actual=ACK_11, completed=True, input_tokens=732180, cached_input_tokens=631680, output_tokens=1211, delta_input=+102,980, 判定=一致。
- R50-A / Turn 12: expected=ACK_12, actual=ACK_12, completed=True, input_tokens=842790, cached_input_tokens=734592, output_tokens=1262, delta_input=+110,610, 判定=一致。
- R50-A / Turn 13: expected=ACK_13, actual=ACK_13, completed=True, input_tokens=961030, cached_input_tokens=845184, output_tokens=1378, delta_input=+118,240, 判定=一致。
- R50-A / Turn 14: expected=ACK_14, actual=ACK_14, completed=True, input_tokens=1086900, cached_input_tokens=963328, output_tokens=1484, delta_input=+125,870, 判定=一致。
- R50-A / Turn 15: expected=ACK_15, actual=ACK_15, completed=True, input_tokens=1220400, cached_input_tokens=1089152, output_tokens=1513, delta_input=+133,500, 判定=一致。
- R50-A / Turn 16: expected=ACK_16, actual=ACK_16, completed=True, input_tokens=1361530, cached_input_tokens=1222528, output_tokens=1611, delta_input=+141,130, 判定=一致。
- R50-A / Turn 17: expected=ACK_17, actual=ACK_17, completed=True, input_tokens=1510290, cached_input_tokens=1363584, output_tokens=1724, delta_input=+148,760, 判定=一致。
- R50-A / Turn 18: expected=ACK_18, actual=ACK_18, completed=True, input_tokens=1666680, cached_input_tokens=1512320, output_tokens=1731, delta_input=+156,390, 判定=一致。
- R50-A / Turn 19: expected=ACK_19, actual=ACK_19, completed=True, input_tokens=1830700, cached_input_tokens=1668608, output_tokens=1738, delta_input=+164,020, 判定=一致。
- R50-A / Turn 20: expected=ACK_20, actual=ACK_20, completed=True, input_tokens=2002350, cached_input_tokens=1832576, output_tokens=1831, delta_input=+171,650, 判定=一致。
- R50-A / Turn 21: expected=ACK_21, actual=ACK_21, completed=True, input_tokens=2181630, cached_input_tokens=2004096, output_tokens=1914, delta_input=+179,280, 判定=一致。
- R50-A / Turn 22: expected=ACK_22, actual=ACK_22, completed=True, input_tokens=2368540, cached_input_tokens=2183296, output_tokens=1945, delta_input=+186,910, 判定=一致。
- R50-A / Turn 23: expected=ACK_23, actual=ACK_23, completed=True, input_tokens=2563080, cached_input_tokens=2370176, output_tokens=1952, delta_input=+194,540, 判定=一致。
- R50-A / Turn 24: expected=ACK_24, actual=ACK_24, completed=True, input_tokens=2765250, cached_input_tokens=2564608, output_tokens=1959, delta_input=+202,170, 判定=一致。
- R50-A / Turn 25: expected=ACK_25, actual=ACK_25, completed=True, input_tokens=2975050, cached_input_tokens=2766720, output_tokens=2065, delta_input=+209,800, 判定=一致。
- R50-A / Turn 26: expected=ACK_26, actual=ACK_26, completed=True, input_tokens=3192480, cached_input_tokens=2976384, output_tokens=2072, delta_input=+217,430, 判定=一致。
- R50-A / Turn 27: expected=ACK_27, actual=ACK_27, completed=True, input_tokens=3417540, cached_input_tokens=3193728, output_tokens=2260, delta_input=+225,060, 判定=一致。
- R50-A / Turn 28: expected=ACK_28, actual=ACK_28, completed=True, input_tokens=3650230, cached_input_tokens=3418752, output_tokens=2267, delta_input=+232,690, 判定=一致。
- R50-A / Turn 29: expected=ACK_29, actual=ACK_29, completed=True, input_tokens=3890550, cached_input_tokens=3651328, output_tokens=2274, delta_input=+240,320, 判定=一致。
- R50-A / Turn 30: expected=ACK_30, actual=ACK_30, completed=True, input_tokens=4138500, cached_input_tokens=3891584, output_tokens=2364, delta_input=+247,950, 判定=一致。
- R50-A / Turn 31: expected=ACK_31, actual=ACK_31, completed=True, input_tokens=4294532, cached_input_tokens=3895040, output_tokens=2466, delta_input=+156,032, 判定=一致。
- R50-A / Turn 32: expected=ACK_32, actual=ACK_32, completed=True, input_tokens=4458194, cached_input_tokens=4050944, output_tokens=2473, delta_input=+163,662, 判定=一致。
- R50-A / Turn 33: expected=ACK_33, actual=ACK_33, completed=True, input_tokens=4629486, cached_input_tokens=4214528, output_tokens=2496, delta_input=+171,292, 判定=一致。
- R50-A / Turn 34: expected=ACK_34, actual=ACK_34, completed=True, input_tokens=4808408, cached_input_tokens=4385792, output_tokens=2503, delta_input=+178,922, 判定=一致。
- R50-A / Turn 35: expected=ACK_35, actual=ACK_35, completed=True, input_tokens=4994960, cached_input_tokens=4564608, output_tokens=2539, delta_input=+186,552, 判定=一致。
- R50-A / Turn 36: expected=ACK_36, actual=ACK_36, completed=True, input_tokens=5189142, cached_input_tokens=4751104, output_tokens=2546, delta_input=+194,182, 判定=一致。
- R50-A / Turn 37: expected=ACK_37, actual=ACK_37, completed=True, input_tokens=5390954, cached_input_tokens=4945152, output_tokens=2553, delta_input=+201,812, 判定=一致。
- R50-A / Turn 38: expected=ACK_38, actual=ACK_38, completed=True, input_tokens=5600396, cached_input_tokens=5146880, output_tokens=2560, delta_input=+209,442, 判定=一致。
- R50-A / Turn 39: expected=ACK_39, actual=ACK_39, completed=True, input_tokens=5817468, cached_input_tokens=5356288, output_tokens=2567, delta_input=+217,072, 判定=一致。
- R50-A / Turn 40: expected=ACK_40, actual=ACK_40, completed=True, input_tokens=6042170, cached_input_tokens=5573248, output_tokens=2574, delta_input=+224,702, 判定=一致。
- R50-A / Turn 41: expected=ACK_41, actual=ACK_41, completed=True, input_tokens=6274502, cached_input_tokens=5797888, output_tokens=2581, delta_input=+232,332, 判定=一致。
- R50-A / Turn 42: expected=ACK_42, actual=ACK_42, completed=True, input_tokens=6514464, cached_input_tokens=6030080, output_tokens=2588, delta_input=+239,962, 判定=一致。
- R50-A / Turn 43: expected=ACK_43, actual=ACK_43, completed=True, input_tokens=6762056, cached_input_tokens=6269952, output_tokens=2595, delta_input=+247,592, 判定=一致。
- R50-A / Turn 44: expected=ACK_44, actual=ACK_44, completed=True, input_tokens=6918048, cached_input_tokens=6273408, output_tokens=2620, delta_input=+155,992, 判定=一致。
- R50-A / Turn 45: expected=ACK_45, actual=ACK_45, completed=True, input_tokens=7081670, cached_input_tokens=6429312, output_tokens=2627, delta_input=+163,622, 判定=一致。
- R50-A / Turn 46: expected=ACK_46, actual=ACK_46, completed=True, input_tokens=7252922, cached_input_tokens=6592896, output_tokens=2650, delta_input=+171,252, 判定=一致。
- R50-A / Turn 47: expected=ACK_47, actual=ACK_47, completed=True, input_tokens=7431804, cached_input_tokens=6764032, output_tokens=2673, delta_input=+178,882, 判定=一致。
- R50-A / Turn 48: expected=ACK_48, actual=ACK_48, completed=True, input_tokens=7618316, cached_input_tokens=6942848, output_tokens=2759, delta_input=+186,512, 判定=一致。
- R50-A / Turn 49: expected=TOKEN, actual=CP_coarse_50_1_20260211, completed=True, input_tokens=7812457, cached_input_tokens=7129216, output_tokens=2863, delta_input=+194,141, 判定=一致。

### R50-B 詳細逐語ログ
- R50-B / Turn 00: expected=STORED, actual=STORED, completed=True, input_tokens=19049, cached_input_tokens=3456, output_tokens=176, delta_input=initial, 判定=一致。
- R50-B / Turn 01: expected=ACK_1, actual=ACK_1, completed=True, input_tokens=45728, cached_input_tokens=22400, output_tokens=340, delta_input=+26,679, 判定=一致。
- R50-B / Turn 02: expected=ACK_2, actual=ACK_2, completed=True, input_tokens=80037, cached_input_tokens=49024, output_tokens=430, delta_input=+34,309, 判定=一致。
- R50-B / Turn 03: expected=ACK_3, actual=ACK_3, completed=True, input_tokens=121976, cached_input_tokens=83200, output_tokens=499, delta_input=+41,939, 判定=一致。
- R50-B / Turn 04: expected=ACK_4, actual=ACK_4, completed=True, input_tokens=171545, cached_input_tokens=125056, output_tokens=630, delta_input=+49,569, 判定=一致。
- R50-B / Turn 05: expected=ACK_5, actual=ACK_5, completed=True, input_tokens=228744, cached_input_tokens=174592, output_tokens=722, delta_input=+57,199, 判定=一致。
- R50-B / Turn 06: expected=ACK_6, actual=ACK_6, completed=True, input_tokens=293573, cached_input_tokens=231680, output_tokens=758, delta_input=+64,829, 判定=一致。
- R50-B / Turn 07: expected=ACK_7, actual=ACK_7, completed=True, input_tokens=366032, cached_input_tokens=296448, output_tokens=814, delta_input=+72,459, 判定=一致。
- R50-B / Turn 08: expected=ACK_8, actual=ACK_8, completed=True, input_tokens=446121, cached_input_tokens=368768, output_tokens=849, delta_input=+80,089, 判定=一致。
- R50-B / Turn 09: expected=ACK_9, actual=ACK_9, completed=True, input_tokens=533840, cached_input_tokens=448768, output_tokens=932, delta_input=+87,719, 判定=一致。
- R50-B / Turn 10: expected=ACK_10, actual=ACK_10, completed=True, input_tokens=629189, cached_input_tokens=536448, output_tokens=991, delta_input=+95,349, 判定=一致。
- R50-B / Turn 11: expected=ACK_11, actual=ACK_11, completed=True, input_tokens=732168, cached_input_tokens=631680, output_tokens=1079, delta_input=+102,979, 判定=一致。
- R50-B / Turn 12: expected=ACK_12, actual=ACK_12, completed=True, input_tokens=842777, cached_input_tokens=734592, output_tokens=1159, delta_input=+110,609, 判定=一致。
- R50-B / Turn 13: expected=ACK_13, actual=ACK_13, completed=True, input_tokens=961016, cached_input_tokens=845056, output_tokens=1211, delta_input=+118,239, 判定=一致。
- R50-B / Turn 14: expected=ACK_14, actual=ACK_14, completed=True, input_tokens=1086885, cached_input_tokens=963200, output_tokens=1218, delta_input=+125,869, 判定=一致。
- R50-B / Turn 15: expected=ACK_15, actual=ACK_15, completed=True, input_tokens=1220384, cached_input_tokens=1089024, output_tokens=1308, delta_input=+133,499, 判定=一致。
- R50-B / Turn 16: expected=ACK_16, actual=ACK_16, completed=True, input_tokens=1361513, cached_input_tokens=1222400, output_tokens=1404, delta_input=+141,129, 判定=一致。
- R50-B / Turn 17: expected=ACK_17, actual=ACK_17, completed=True, input_tokens=1510272, cached_input_tokens=1363456, output_tokens=1465, delta_input=+148,759, 判定=一致。
- R50-B / Turn 18: expected=ACK_18, actual=ACK_18, completed=True, input_tokens=1666661, cached_input_tokens=1512192, output_tokens=1531, delta_input=+156,389, 判定=一致。
- R50-B / Turn 19: expected=ACK_19, actual=ACK_19, completed=True, input_tokens=1830680, cached_input_tokens=1668480, output_tokens=1642, delta_input=+164,019, 判定=一致。
- R50-B / Turn 20: expected=ACK_20, actual=ACK_20, completed=True, input_tokens=2002329, cached_input_tokens=1832448, output_tokens=1685, delta_input=+171,649, 判定=一致。
- R50-B / Turn 21: expected=ACK_21, actual=ACK_21, completed=True, input_tokens=2181608, cached_input_tokens=2003968, output_tokens=1692, delta_input=+179,279, 判定=一致。
- R50-B / Turn 22: expected=ACK_22, actual=ACK_22, completed=True, input_tokens=2368517, cached_input_tokens=2183168, output_tokens=1782, delta_input=+186,909, 判定=一致。
- R50-B / Turn 23: expected=ACK_23, actual=ACK_23, completed=True, input_tokens=2563056, cached_input_tokens=2370048, output_tokens=1825, delta_input=+194,539, 判定=一致。
- R50-B / Turn 24: expected=ACK_24, actual=ACK_24, completed=True, input_tokens=2765225, cached_input_tokens=2564480, output_tokens=1901, delta_input=+202,169, 判定=一致。
- R50-B / Turn 25: expected=ACK_25, actual=ACK_25, completed=True, input_tokens=2975024, cached_input_tokens=2766592, output_tokens=2022, delta_input=+209,799, 判定=一致。
- R50-B / Turn 26: expected=ACK_26, actual=ACK_26, completed=True, input_tokens=3192453, cached_input_tokens=2976256, output_tokens=2048, delta_input=+217,429, 判定=一致。
- R50-B / Turn 27: expected=ACK_27, actual=ACK_27, completed=True, input_tokens=3417512, cached_input_tokens=3193600, output_tokens=2055, delta_input=+225,059, 判定=一致。
- R50-B / Turn 28: expected=ACK_28, actual=ACK_28, completed=True, input_tokens=3650201, cached_input_tokens=3418624, output_tokens=2062, delta_input=+232,689, 判定=一致。
- R50-B / Turn 29: expected=ACK_29, actual=ACK_29, completed=True, input_tokens=3890520, cached_input_tokens=3651200, output_tokens=2069, delta_input=+240,319, 判定=一致。
- R50-B / Turn 30: expected=ACK_30, actual=ACK_30, completed=True, input_tokens=4138469, cached_input_tokens=3891456, output_tokens=2145, delta_input=+247,949, 判定=一致。
- R50-B / Turn 31: expected=ACK_31, actual=ACK_31, completed=True, input_tokens=4294449, cached_input_tokens=3894912, output_tokens=2191, delta_input=+155,980, 判定=一致。
- R50-B / Turn 32: expected=ACK_32, actual=ACK_32, completed=True, input_tokens=4458059, cached_input_tokens=4050816, output_tokens=2221, delta_input=+163,610, 判定=一致。
- R50-B / Turn 33: expected=ACK_33, actual=ACK_33, completed=True, input_tokens=4629299, cached_input_tokens=4214400, output_tokens=2252, delta_input=+171,240, 判定=一致。
- R50-B / Turn 34: expected=ACK_34, actual=ACK_34, completed=True, input_tokens=4808169, cached_input_tokens=4385536, output_tokens=2280, delta_input=+178,870, 判定=一致。
- R50-B / Turn 35: expected=ACK_35, actual=ACK_35, completed=True, input_tokens=4994669, cached_input_tokens=4564352, output_tokens=2315, delta_input=+186,500, 判定=一致。
- R50-B / Turn 36: expected=ACK_36, actual=ACK_36, completed=True, input_tokens=5188799, cached_input_tokens=4750720, output_tokens=2349, delta_input=+194,130, 判定=一致。
- R50-B / Turn 37: expected=ACK_37, actual=ACK_37, completed=True, input_tokens=5390559, cached_input_tokens=4944768, output_tokens=2356, delta_input=+201,760, 判定=一致。
- R50-B / Turn 38: expected=ACK_38, actual=ACK_38, completed=True, input_tokens=5599949, cached_input_tokens=5146496, output_tokens=2363, delta_input=+209,390, 判定=一致。
- R50-B / Turn 39: expected=ACK_39, actual=ACK_39, completed=True, input_tokens=5816969, cached_input_tokens=5355776, output_tokens=2370, delta_input=+217,020, 判定=一致。
- R50-B / Turn 40: expected=ACK_40, actual=ACK_40, completed=True, input_tokens=6041619, cached_input_tokens=5572736, output_tokens=2377, delta_input=+224,650, 判定=一致。
- R50-B / Turn 41: expected=ACK_41, actual=ACK_41, completed=True, input_tokens=6273899, cached_input_tokens=5797248, output_tokens=2384, delta_input=+232,280, 判定=一致。
- R50-B / Turn 42: expected=ACK_42, actual=ACK_42, completed=True, input_tokens=6513809, cached_input_tokens=6029440, output_tokens=2391, delta_input=+239,910, 判定=一致。
- R50-B / Turn 43: expected=ACK_43, actual=ACK_43, completed=True, input_tokens=6761349, cached_input_tokens=6269312, output_tokens=2398, delta_input=+247,540, 判定=一致。
- R50-B / Turn 44: expected=ACK_44, actual=ACK_44, completed=True, input_tokens=6917328, cached_input_tokens=6272768, output_tokens=2491, delta_input=+155,979, 判定=一致。
- R50-B / Turn 45: expected=ACK_45, actual=ACK_45, completed=True, input_tokens=7080937, cached_input_tokens=6428672, output_tokens=2562, delta_input=+163,609, 判定=一致。
- R50-B / Turn 46: expected=ACK_46, actual=ACK_46, completed=True, input_tokens=7252176, cached_input_tokens=6592256, output_tokens=2604, delta_input=+171,239, 判定=一致。
- R50-B / Turn 47: expected=ACK_47, actual=ACK_47, completed=True, input_tokens=7431045, cached_input_tokens=6763392, output_tokens=2611, delta_input=+178,869, 判定=一致。
- R50-B / Turn 48: expected=ACK_48, actual=ACK_48, completed=True, input_tokens=7617544, cached_input_tokens=6942208, output_tokens=2649, delta_input=+186,499, 判定=一致。
- R50-B / Turn 49: expected=TOKEN, actual=CP_focus_50_2_20260211, completed=True, input_tokens=7811672, cached_input_tokens=7128576, output_tokens=2816, delta_input=+194,128, 判定=一致。

### R50-C 詳細逐語ログ
- R50-C / Turn 00: expected=STORED, actual=STORED, completed=True, input_tokens=19049, cached_input_tokens=3456, output_tokens=279, delta_input=initial, 判定=一致。
- R50-C / Turn 01: expected=ACK_1, actual=ACK_1, completed=True, input_tokens=45728, cached_input_tokens=22400, output_tokens=440, delta_input=+26,679, 判定=一致。
- R50-C / Turn 02: expected=ACK_2, actual=ACK_2, completed=True, input_tokens=80037, cached_input_tokens=49024, output_tokens=496, delta_input=+34,309, 判定=一致。
- R50-C / Turn 03: expected=ACK_3, actual=ACK_3, completed=True, input_tokens=121976, cached_input_tokens=83200, output_tokens=607, delta_input=+41,939, 判定=一致。
- R50-C / Turn 04: expected=ACK_4, actual=ACK_4, completed=True, input_tokens=171545, cached_input_tokens=125056, output_tokens=681, delta_input=+49,569, 判定=一致。
- R50-C / Turn 05: expected=ACK_5, actual=ACK_5, completed=True, input_tokens=228744, cached_input_tokens=174592, output_tokens=734, delta_input=+57,199, 判定=一致。
- R50-C / Turn 06: expected=ACK_6, actual=ACK_6, completed=True, input_tokens=293573, cached_input_tokens=231680, output_tokens=792, delta_input=+64,829, 判定=一致。
- R50-C / Turn 07: expected=ACK_7, actual=ACK_7, completed=True, input_tokens=366032, cached_input_tokens=296448, output_tokens=835, delta_input=+72,459, 判定=一致。
- R50-C / Turn 08: expected=ACK_8, actual=ACK_8, completed=True, input_tokens=446121, cached_input_tokens=368768, output_tokens=913, delta_input=+80,089, 判定=一致。
- R50-C / Turn 09: expected=ACK_9, actual=ACK_9, completed=True, input_tokens=533840, cached_input_tokens=448768, output_tokens=997, delta_input=+87,719, 判定=一致。
- R50-C / Turn 10: expected=ACK_10, actual=ACK_10, completed=True, input_tokens=629189, cached_input_tokens=536448, output_tokens=1066, delta_input=+95,349, 判定=一致。
- R50-C / Turn 11: expected=ACK_11, actual=ACK_11, completed=True, input_tokens=732168, cached_input_tokens=631680, output_tokens=1138, delta_input=+102,979, 判定=一致。
- R50-C / Turn 12: expected=ACK_12, actual=ACK_12, completed=True, input_tokens=842777, cached_input_tokens=734592, output_tokens=1255, delta_input=+110,609, 判定=一致。
- R50-C / Turn 13: expected=ACK_13, actual=ACK_13, completed=True, input_tokens=961016, cached_input_tokens=845056, output_tokens=1341, delta_input=+118,239, 判定=一致。
- R50-C / Turn 14: expected=ACK_14, actual=ACK_14, completed=True, input_tokens=1086885, cached_input_tokens=963200, output_tokens=1402, delta_input=+125,869, 判定=一致。
- R50-C / Turn 15: expected=ACK_15, actual=ACK_15, completed=True, input_tokens=1220384, cached_input_tokens=1089024, output_tokens=1467, delta_input=+133,499, 判定=一致。
- R50-C / Turn 16: expected=ACK_16, actual=ACK_16, completed=True, input_tokens=1361513, cached_input_tokens=1222400, output_tokens=1474, delta_input=+141,129, 判定=一致。
- R50-C / Turn 17: expected=ACK_17, actual=ACK_17, completed=True, input_tokens=1510272, cached_input_tokens=1363456, output_tokens=1520, delta_input=+148,759, 判定=一致。
- R50-C / Turn 18: expected=ACK_18, actual=ACK_18, completed=True, input_tokens=1666661, cached_input_tokens=1512192, output_tokens=1527, delta_input=+156,389, 判定=一致。
- R50-C / Turn 19: expected=ACK_19, actual=ACK_19, completed=True, input_tokens=1830680, cached_input_tokens=1668480, output_tokens=1595, delta_input=+164,019, 判定=一致。
- R50-C / Turn 20: expected=ACK_20, actual=ACK_20, completed=True, input_tokens=2002329, cached_input_tokens=1832448, output_tokens=1769, delta_input=+171,649, 判定=一致。
- R50-C / Turn 21: expected=ACK_21, actual=ACK_21, completed=True, input_tokens=2181608, cached_input_tokens=2003968, output_tokens=1802, delta_input=+179,279, 判定=一致。
- R50-C / Turn 22: expected=ACK_22, actual=ACK_22, completed=True, input_tokens=2368517, cached_input_tokens=2183168, output_tokens=1809, delta_input=+186,909, 判定=一致。
- R50-C / Turn 23: expected=ACK_23, actual=ACK_23, completed=True, input_tokens=2563056, cached_input_tokens=2370048, output_tokens=1816, delta_input=+194,539, 判定=一致。
- R50-C / Turn 24: expected=ACK_24, actual=ACK_24, completed=True, input_tokens=2765225, cached_input_tokens=2564480, output_tokens=1914, delta_input=+202,169, 判定=一致。
- R50-C / Turn 25: expected=ACK_25, actual=ACK_25, completed=True, input_tokens=2975024, cached_input_tokens=2766592, output_tokens=2003, delta_input=+209,799, 判定=一致。
- R50-C / Turn 26: expected=ACK_26, actual=ACK_26, completed=True, input_tokens=3192453, cached_input_tokens=2976256, output_tokens=2133, delta_input=+217,429, 判定=一致。
- R50-C / Turn 27: expected=ACK_27, actual=ACK_27, completed=True, input_tokens=3417512, cached_input_tokens=3193600, output_tokens=2140, delta_input=+225,059, 判定=一致。
- R50-C / Turn 28: expected=ACK_28, actual=ACK_28, completed=True, input_tokens=3650201, cached_input_tokens=3418624, output_tokens=2147, delta_input=+232,689, 判定=一致。
- R50-C / Turn 29: expected=ACK_29, actual=ACK_29, completed=True, input_tokens=3890520, cached_input_tokens=3651200, output_tokens=2154, delta_input=+240,319, 判定=一致。
- R50-C / Turn 30: expected=ACK_30, actual=ACK_30, completed=True, input_tokens=4138469, cached_input_tokens=3891456, output_tokens=2234, delta_input=+247,949, 判定=一致。
- R50-C / Turn 31: expected=ACK_31, actual=ACK_31, completed=True, input_tokens=4294468, cached_input_tokens=3894912, output_tokens=2342, delta_input=+155,999, 判定=一致。
- R50-C / Turn 32: expected=ACK_32, actual=ACK_32, completed=True, input_tokens=4458097, cached_input_tokens=4050816, output_tokens=2367, delta_input=+163,629, 判定=一致。
- R50-C / Turn 33: expected=ACK_33, actual=ACK_33, completed=True, input_tokens=4629356, cached_input_tokens=4214400, output_tokens=2397, delta_input=+171,259, 判定=一致。
- R50-C / Turn 34: expected=ACK_34, actual=ACK_34, completed=True, input_tokens=4808245, cached_input_tokens=4385536, output_tokens=2442, delta_input=+178,889, 判定=一致。
- R50-C / Turn 35: expected=ACK_35, actual=ACK_35, completed=True, input_tokens=4994764, cached_input_tokens=4564352, output_tokens=2449, delta_input=+186,519, 判定=一致。
- R50-C / Turn 36: expected=ACK_36, actual=ACK_36, completed=True, input_tokens=5188913, cached_input_tokens=4750848, output_tokens=2480, delta_input=+194,149, 判定=一致。
- R50-C / Turn 37: expected=ACK_37, actual=ACK_37, completed=True, input_tokens=5390692, cached_input_tokens=4944896, output_tokens=2487, delta_input=+201,779, 判定=一致。
- R50-C / Turn 38: expected=ACK_38, actual=ACK_38, completed=True, input_tokens=5600101, cached_input_tokens=5146624, output_tokens=2494, delta_input=+209,409, 判定=一致。
- R50-C / Turn 39: expected=ACK_39, actual=ACK_39, completed=True, input_tokens=5817140, cached_input_tokens=5355904, output_tokens=2501, delta_input=+217,039, 判定=一致。
- R50-C / Turn 40: expected=ACK_40, actual=ACK_40, completed=True, input_tokens=6041809, cached_input_tokens=5572864, output_tokens=2570, delta_input=+224,669, 判定=一致。
- R50-C / Turn 41: expected=ACK_41, actual=ACK_41, completed=True, input_tokens=6274108, cached_input_tokens=5797504, output_tokens=2597, delta_input=+232,299, 判定=一致。
- R50-C / Turn 42: expected=ACK_42, actual=ACK_42, completed=True, input_tokens=6514037, cached_input_tokens=6029696, output_tokens=2604, delta_input=+239,929, 判定=一致。
- R50-C / Turn 43: expected=ACK_43, actual=ACK_43, completed=True, input_tokens=6761596, cached_input_tokens=6269568, output_tokens=2611, delta_input=+247,559, 判定=一致。
- R50-C / Turn 44: expected=ACK_44, actual=ACK_44, completed=True, input_tokens=6917547, cached_input_tokens=6280192, output_tokens=2638, delta_input=+155,951, 判定=一致。
- R50-C / Turn 45: expected=ACK_45, actual=ACK_45, completed=True, input_tokens=7081128, cached_input_tokens=6436096, output_tokens=2661, delta_input=+163,581, 判定=一致。
- R50-C / Turn 46: expected=ACK_46, actual=ACK_46, completed=True, input_tokens=7252339, cached_input_tokens=6599552, output_tokens=2668, delta_input=+171,211, 判定=一致。
- R50-C / Turn 47: expected=ACK_47, actual=ACK_47, completed=True, input_tokens=7431180, cached_input_tokens=6770688, output_tokens=2675, delta_input=+178,841, 判定=一致。
- R50-C / Turn 48: expected=ACK_48, actual=ACK_48, completed=True, input_tokens=7617651, cached_input_tokens=6949504, output_tokens=2682, delta_input=+186,471, 判定=一致。
- R50-C / Turn 49: expected=TOKEN, actual=ACK_49, completed=True, input_tokens=7811751, cached_input_tokens=7135872, output_tokens=3731, delta_input=+194,100, 判定=不一致（最終想起の系列ずれ）。

### 逐語ログ横断での要約所見
- 3ラン合算の turn間 input_tokens 増分平均は 159,039.0 tokens/turn であった。
- 増分は厳密な定数ではなく、キャッシュ状態・応答長・内部処理の揺れによりターン毎に変動する。
- 失敗ラン（R50-C）は中間ACK系列の一貫性は維持しつつ、最終トークン回収のみ `ACK_49` に落ちるため、完全忘却ではなく参照優先度の逆転が示唆される。

## 15. 付録B: 統計手順の完全記述と再解析観点
### 15.1 成功率区間推定（Wilson）
Wilson区間を採用した理由は、小標本条件でWald区間が過度に楽観/悲観化しやすいためである。
本実験では n=1,2,3 が混在し、95% CIの幅が結果解釈に直結するため、区間推定を本文の主表に併記した。

### 15.2 片側二項尾確率の補助的利用
50ターンの目標成功率80%という運用目標に対し、観測値2/3は直観上は不足だが、n=3では統計的検出力が低い。
そのため本報告では「棄却判定」を主張せず、運用上の安全余裕（margin）不足を示す補助証拠として提示した。

### 15.3 回帰の位置づけ（因果でなく記述）
本報告の回帰式は、将来値を保証する予測器ではなく、観測レンジでの傾向圧縮（trend compression）である。
特に long-text の duration 回帰は R^2 が低く、文字数単独で遅延を説明しないことを示した。

### 15.4 実運用における再評価設計
1. 50ターン帯は最低N=20の繰り返しで再評価し、CI下限ベースでGo/No-Goを判定する。
2. 長文は抽出課題だけでなく、制約付き推論課題を混在させる。
3. 介入（checkpoint/restate）の有無を実験因子化し、失敗率の絶対改善量で効果判定する。
4. context使用量の監視閾値を設け、final input tokensが閾値を超えた場合は自動的に要約・圧縮を挿入する。

## 16. 付録C: 詳細考察（長文）
### C-1
本研究の中心的意義は、単純な成功率提示にとどまらず、失敗の形を同定した点にある。一般にLLM評価は『通った/落ちた』の二値に回収されがちであるが、実運用で問題になるのは失敗の構造である。今回の失敗は無関係語の噴出や文法崩壊ではなく、系列の一貫性を保ったまま最終参照のみ逸脱する型であり、これは運用設計上の対策可能性が高い。すなわち、プロンプト設計やターン境界での状態再固定（restate）により、失敗率を実用域まで押し下げられる余地がある。

### C-2
長文検証の結果は一見すると非常に良好である。しかし、ここでの課題はマーカー抽出であり、推論木の深さが小さい。従って『300,000文字でも問題ない』という一般化は禁物であり、『300,000文字の抽出課題では失敗未観測』という限定表現が科学的に妥当である。特に、複数制約の整合性判断、例外規則の優先度判定、矛盾文書統合のような高次推論課題では、入力長よりも課題複雑度が支配的に効く可能性が高い。

### C-3
コンテキスト使用量に関しては、multi-turn の最終ターンで指数的に見える増加を示したが、今回の観測点は4点（20/30/40/50）であり、線形近似が高R^2を示すこと自体は驚くべきことではない。重要なのは係数の値よりも、50ターンで約7.8M tokensという規模に達するという事実である。実運用上はこの規模到達前にコンテキスト圧縮や状態の再基準化を入れる設計が必要であり、閾値制御（token-budget policy）をワークフロー標準に組み込むべきである。

### C-4
失敗ランと成功ランの差は、表層応答だけを見ても小さい。中間ACK系列はほぼ同一に見え、最終点のみが分岐する。これは、モデル内部で参照競合が閾値付近にあり、わずかな条件差（キャッシュ状態、応答長、内部探索経路）で最終選択が切り替わる『臨界近傍現象』として解釈できる。臨界近傍では単回試行の意味が薄く、繰り返し試験と分布評価が必須である。

### C-5
研究運用面では、評価設計に『失敗型ラベリング』を導入することが重要である。単なる成功率だけでなく、final_recall失敗、mid_turn失敗、init失敗などを分離して追跡すれば、対策優先度を合理的に決められる。今回のデータでは失敗がfinal_recallに集中しているため、対策も終端ターンの強化（最終ターンの再明示、短い復唱、二重確認プロンプト）に集中すべきである。

### C-6
さらに、長文系の性能判断では、平均値だけでなく最悪ケース遅延（p95/p99）を取り込む必要がある。今回の試行数では高分位推定は困難だったが、将来実験では各条件Nを増やし、運用SLOと整合する形で評価すべきである。特にバッチ処理・並列処理環境ではキュー遅延と実行遅延が混在するため、測定を分解（待ち時間/実行時間）することが望ましい。

### C-7
最後に、今回の結果は『Codex主導フローの採否』に直接関与する。<=40 turns での安定性はフロー設計に十分利用可能であり、50 turns 以上を扱う場合は設計側での補助（checkpoint/restate・要約・検証ループ）を組み込むべきだという具体的指針を与える。すなわち、モデル性能を前提化するのではなく、モデルの誤り方に合わせてフローを設計することが、実務での最短距離である。

### C-8
将来の高精度研究では、同一課題を複数モデル・複数温度・複数実行時間帯で反復し、混合効果モデルで分散成分を分離するアプローチが有効である。これにより、モデル差・課題差・時刻差・キャッシュ差を同時に扱い、どこに最大不確実性があるかを定量化できる。単純な平均比較を超えた、設計に効く統計へ接続するための重要なステップである。

### C-9
また、実運用に投入する前には、正答だけでなく『安全な誤答』を定義する必要がある。たとえば最終トークン想起に失敗しても、直近ACKを返すならば被害限定可能な場合がある。一方で、機密情報や外部副作用を伴うタスクでは、同種の失敗が重大事故に直結する。従って評価指標はタスクリスクに応じて重み付けし、同じ66.7%でも許容可否が異なるという意思決定ルールを明文化すべきである。

### C-10
このように、本報告の価値は単一の成功率数値ではなく、運用に実装できる形での知見変換にある。境界帯を見つけ、失敗型を捉え、補助設計へ落とし込む。この3段階を継続的に回すことで、モデル更新や環境変化があっても品質を維持できる。評価は一度きりの儀式ではなく、システムの一部として内蔵されるべきである。
