# TripEase ML Pipeline Design (Step 4 — Theory Only)

This document is a **design blueprint** for the ML pipeline. It contains **no executable training code**, no `model.fit()` / `.train()` / evaluation implementation, and no changes to UI, views, URLs, or database models. Implementation (Step 5) will follow this blueprint.

**Scope:** Based on Step 3, only **easemytrip.csv** is in scope for this blueprint. The same structure can be reused when **flight_delay.csv**, **airline_on_time.csv**, and **flight_price.csv** are added later.

---

## 1. Per-dataset problem definition and feature grouping

### 1.1 Dataset: easemytrip.csv

**ML problem type:**  
- **Regression** — predict a continuous target (fare amount).

**Proposed target variable:**  
- **`Fare`** (ticket price).  
- **Assumptions:**  
  - Fare is the primary business outcome of interest for price prediction.  
  - All fare values are in a single currency (e.g. INR).  
  - No currency column is present; if multi-currency data is added later, the design must be revisited.

**Feature grouping (conceptual only; no encoding or dropping performed here):**

| Group | Columns | Notes |
|-------|---------|--------|
| **Identifier / metadata** | `Uniq Id` | Row ID only. **Do not use as a predictive feature.** Use only for tracing or joins. |
| **Metadata (non-predictive)** | `Crawl Timestamp` | Scrape/collection time only. **Do not use as a predictive feature** (leakage / non-generalizability risk). Document as such in preprocessing. |
| **Categorical** | `Source`, `Destination`, `Layover1`, `Layover2`, `Layover3` | Origin, destination, and stop cities. Empty layover = no stop at that position. |
| **Categorical (multi-valued)** | `Flight Operator`, `Flight Number` | Pipe-separated per leg (e.g. `SpiceJet|SpiceJet`). Can be decomposed into primary airline, segment count, same-airline flag, etc. |
| **Temporal (date)** | `Departure Date`, `Arrival Date` | String dates (e.g. `23Apr2020`). To be parsed for feature extraction. |
| **Temporal (time)** | `Departure Time`, `Arrival Time` | String times (e.g. `13:10`). To be parsed for feature extraction. |
| **Derived temporal / numerical** | `Total Time` | Duration string (e.g. `08h 50m`). To be converted to minutes (numerical). |
| **Numerical** | `Number Of Stops`, `Fare` | Stored as strings; to be cast to integer and float. `Fare` is the target. |

**Assumptions (explicit):**  
- Route is defined by Source → Layover(s) → Destination.  
- Layover columns are structurally missing (no stop at that position), not missing at random.  
- No other datasets (e.g. flight_delay, airline_on_time, flight_price) are used in this blueprint; when added, a separate section per dataset will be needed.

---

## 2. Preprocessing pipeline (design only)

Design only — strategies and options, no implementation.

### 2.1 Missing values

- **Strategy options:**  
  - **Identifier / metadata:** No imputation. Exclude from feature set (e.g. `Uniq Id`, `Crawl Timestamp` as non-features).  
  - **Layover columns (Layover1, Layover2, Layover3):** Treat empty as “no stop at this position.” Option A: keep as categorical with a dedicated category (e.g. “None” / “NoStop”). Option B: derive a single “number of stops” and “via cities” list and do not impute. **Recommendation:** Option B for simplicity; retain original columns in raw data for traceability.  
  - **All other columns (from Step 3):** No missing values; no imputation needed.  
- **No deletion of rows** for missing layovers; only structural encoding.

### 2.2 Categorical variables

- **Columns concerned:** `Source`, `Destination`, `Layover1`, `Layover2`, `Layover3`, and derived from `Flight Operator` (e.g. primary airline).  
- **Encoding options (to be chosen at implementation time):**  
  - **One-hot encoding:** For low-cardinality fields (e.g. if we bucket routes or airlines).  
  - **Target encoding (with proper validation):** For high-cardinality (e.g. city/airport codes) to avoid explosion of dimensions.  
  - **Frequency encoding:** Alternative for high-cardinality as a stable, leakage-resistant option.  
  - **Leave as string / hash:** Not recommended for tree-based models if interpretability or stability is desired.  
- **Multi-valued fields (`Flight Operator`, `Flight Number`):** Define derived features first (e.g. primary operator, number of segments, same-airline flag), then apply encoding to those. No encoding of raw pipe-separated string as a single token.

### 2.3 Date/time features

- **Parsing:** Convert string dates and times to a proper date/time type; convert `Total Time` to minutes (integer).  
- **Feature extraction ideas (no implementation):**  
  - From departure/arrival date: day of week, month, is_weekend, is_holiday (if calendar available).  
  - From departure/arrival time: hour of day, time-of-day bucket (e.g. morning/afternoon/evening), possibly “overnight” flag if arrival date ≠ departure date.  
  - From duration: total minutes (and optionally squared or binned).  
- **Explicit exclusion:** Do **not** derive “days until departure” or “booking lead time” from `Crawl Timestamp`; it is scrape time only and must not be used as a feature.

### 2.4 Feature scaling / normalization

- **When required:** For linear models, distance-based models, or neural networks, scale numerical features (e.g. total minutes, number of stops if treated as continuous).  
- **Options:** Standardization (zero mean, unit variance) or min-max scaling.  
- **When optional:** Tree-based models (e.g. Random Forest, Gradient Boosting) typically do not require scaling; document choice per model family in Step 5.

### 2.5 Outlier handling

- **Target (`Fare`):** Check distribution (e.g. histogram, quantiles). Options: (A) log-transform for right skew, (B) cap at high quantile (e.g. 99th), (C) keep and use robust metrics. **Recommendation:** Analyze distribution in Step 5; prefer log-transform or capping over removing rows, to retain volume.  
- **Duration (total minutes):** Cap or flag extreme values (e.g. > 24 hours) if they are data errors; otherwise keep with a possible “long-haul” flag.  
- **No blanket row deletion** without explicit business rule and documentation.

---

## 3. Data splitting strategy

- **Recommended split:**  
  - **Train:** e.g. 70–80% of rows.  
  - **Validation:** e.g. 10–15% (for hyperparameter tuning and early stopping).  
  - **Test:** e.g. 10–15% (holdout, no tuning on it).  
- **Split type:**  
  - **Random split:** Acceptable if rows are treated as independent (no strict time ordering).  
  - **Time-based split (preferred if applicable):** If `Departure Date` (or similar) is a reliable proxy for “when the observation is from,” split by time so that train < validation < test by date. This reduces leakage from future information and better mimics deployment (predict for future dates).  
- **Justification:**  
  - Random: simple, maximizes use of data; assumes no strong temporal drift.  
  - Time-based: aligns with real use (predicting fares for future departures); reduces leakage and gives a more realistic performance estimate.  
- **Recommendation:** Prefer **time-based split** on `Departure Date` (or earliest date in the row). If a single date is ambiguous (e.g. multi-leg with multiple dates), define a rule (e.g. first departure date) and document it.  
- **Stratification:** For regression, optional stratification by binned fare (e.g. quartiles) to keep price distribution similar across splits; document if used.

---

## 4. Evaluation plan

- **Dataset in scope:** easemytrip.csv → **regression** (target: `Fare`).

### 4.1 Metrics (suitable for regression)

- **MAE (Mean Absolute Error):** Average absolute error in fare units.  
  - **Business interpretation:** Typical average mistake in price (e.g. in INR). Easy to communicate (e.g. “on average we are off by ₹X”).  
- **RMSE (Root Mean Squared Error):** Penalizes large errors more.  
  - **Business interpretation:** How much large over/under-predictions hurt; useful for cost-sensitive decisions.  
- **MAPE (Mean Absolute Percentage Error), if no zero fares:** Percentage error.  
  - **Business interpretation:** Relative accuracy (e.g. “on average X% off”). Use with care if many small fares (denominator small).  
- **R² (coefficient of determination):** Proportion of variance explained.  
  - **Business interpretation:** How much of fare variation is captured by the model (0–1 scale).

### 4.2 Business interpretation (summary)

- **MAE / RMSE:** Direct impact on pricing decisions and user trust (e.g. “typical error in rupees”).  
- **MAPE:** Useful for relative performance across routes or time periods.  
- **R²:** Useful for “how much we can explain” vs. leaving as baseline (e.g. mean fare).

**Recommendation:** Report at least **MAE** and **RMSE** on the test set; optionally MAPE and R². No executable evaluation code in this document.

---

## 5. Risk and data quality assessment

### 5.1 Data leakage risks

- **Crawl Timestamp:** Must **not** be used as a feature. Using it could leak information about when the scrape happened and create non-generalizable patterns.  
- **Uniq Id:** Must not be used as a feature; purely an identifier.  
- **Target encoding:** If target encoding is used for categoricals, it must be fitted on **training data only** and applied to validation/test without using test/validation targets (proper cross-fitting).  
- **Temporal leakage:** If split is random, future dates may appear in training and past in test; time-based split mitigates this.

### 5.2 Bias risks

- **Geographic/carrier bias:** Data may over-represent certain routes or airlines; model may perform poorly on under-represented segments.  
- **Time period bias:** If data spans a specific period (e.g. COVID), fare patterns may not generalize.  
- **Mitigation:** Document data coverage (routes, dates, airlines); monitor performance by segment in Step 5; consider stratified reporting of metrics.

### 5.3 Imbalanced data issues

- **Regression:** No class imbalance; potential **value-range imbalance** (e.g. many low fares, few very high). Consider robust metrics (MAE) and/or log-transform or stratified split by fare bin.  
- **Layover sparsity:** Most rows have 0–1 stops; 2–3 stops are rarer. Not classification imbalance but may affect feature usefulness for multi-stop fares.

### 5.4 Dataset limitations

- **Single dataset:** Only easemytrip.csv; no external demand, events, or competitor prices.  
- **Single currency assumed:** No currency field; if present later, design must be updated.  
- **Scrape nature:** Crawl Timestamp is scrape time, not booking time; no “lead time” or “booking date” for true demand modeling.  
- **Composite fields:** Pipe-separated operators and flight numbers require clear derivation rules for features.  
- **No guarantee of representativeness** of routes, dates, or airlines for future deployment.

---

## 6. Output format and recommendations summary

- **Format:** Human-readable; bullet points and tables; **no executable ML training code**.  
- **Recommendations only:**  
  - Treat **Fare** as the only target for easemytrip.csv; regression.  
  - Do **not** use `Uniq Id` or `Crawl Timestamp` as features; document Crawl Timestamp as scrape-time-only and a leakage risk if misused.  
  - Preprocess layovers as structural “no stop” and derive numerical/categorical features; consider time-based train/validation/test split; report MAE and RMSE (and optionally MAPE, R²).  
  - Address leakage (no Crawl Timestamp, proper target encoding), bias (coverage and segment-wise checks), and data limitations (single dataset, single currency, scrape nature) in implementation (Step 5).

This blueprint is intended for use in **Step 5 (model training)**; no training or evaluation code is implemented in this step.
