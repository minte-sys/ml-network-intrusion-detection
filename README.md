# Network Intrusion Detection System

An educational machine-learning dashboard that classifies historical network-flow records as **Normal** or **Attack**. Upload a CSV, view totals and per-record predictions, and inspect measured model performance. This is a local portfolio demonstration, not live packet capture or a production IDS.

## What works

- Random Forest trained on NSL-KDD's official training split, measured on its separate test split.
- Saved preprocessing and model in one `joblib` pipeline; the API never retrains on startup.
- FastAPI `/health`, `/model-info`, `/predict`, and `/predict-file` endpoints.
- Browser dashboard with CSV upload, distribution bar, alert, and first 100 classifications.
- Included `sample_traffic.csv` with 100 **real test-set feature rows** (labels removed), for a quick demonstration. These rows are part of the evaluation split; the demo sample is not another independent evaluation.

## Architecture

`NSL-KDD → numeric imputation + categorical encoding → Random Forest → saved pipeline → FastAPI → browser dashboard`

The model sees 41 traffic features, including protocol, service, connection duration, byte counts, and host-level statistics. The `attack_type` label becomes `0` for `normal`, `1` otherwise. The dataset's `difficulty` column is excluded because it is benchmark metadata rather than a network-flow feature. Categorical values use one-hot encoding with unseen values ignored; numeric values use median imputation. Transformations are fitted on the training split only. No scaling is necessary for the tree-based model. Missing-cell counts are in `models/metrics.json`.

## Dataset

**NSL-KDD**, `KDDTrain+.txt` (125,973 rows) and `KDDTest+.txt` (22,544 rows). Dataset description: [University of New Brunswick, Canadian Institute for Cybersecurity](https://www.unb.ca/cic/datasets/nsl.html). Downloadable TXT mirror: [HoaNP/NSL-KDD-DataSet](https://github.com/HoaNP/NSL-KDD-DataSet). The files are comma-separated, without a header, with 41 features followed by attack label and difficulty. No data was collected by this project. The historical benchmark is not representative of all modern traffic.

Download both files into `data/` using the repository link above, preserving these exact names: `KDDTrain+.txt`, `KDDTest+.txt`. Raw dataset files are ignored by Git. The model binary is also ignored because the training command reproducibly generates it. The sample file is committed for a quick API demonstration after training.

## Measured results

Random Forest, 100 trees, `min_samples_leaf=2`, fixed seed 42. Train on **KDDTrain+** and evaluate once on **KDDTest+**, without resplitting or tuning on the held-out set. Positive class = Attack.

| Metric | Separate test split |
| --- | ---: |
| Accuracy | 77.90% |
| Precision (Attack) | 96.86% |
| Recall (Attack) | 63.22% |
| F1 (Attack) | 76.51% |
| ROC-AUC | 96.58% |

Confusion matrix (actual rows, predicted columns):

| | Predicted Normal | Predicted Attack |
| --- | ---: | ---: |
| Actual Normal | 9,448 | 263 |
| Actual Attack | 4,720 | 8,113 |

Accuracy alone hides the large number of missed attacks. The model's high precision means most positive predictions were attacks in this dataset, while its modest recall means many actual attack records were classified Normal. The dashboard shows model probability as **confidence**, not a calibrated real-world risk score. Full machine-readable results: `models/metrics.json`.

## Setup and run

Python 3.10+ recommended. From the project directory:

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/train.py
python -m uvicorn src.api:app --reload
```

Open `http://127.0.0.1:8000/` and upload `sample_traffic.csv`. Open `http://127.0.0.1:8000/docs` for interactive API documentation. Training requires both downloaded data files; serving requires `models/model.joblib` and the committed `models/metrics.json`.

### CSV schema and API

Upload a headered CSV with the **41 exact feature column names** from `GET /model-info`. Additional label and difficulty columns are ignored. Max 10,000 records and 5 MB. For a single prediction, POST JSON `{"features":{"duration":0,...}}` to `/predict`, supplying all 41 named features. Both prediction endpoints return actual model outputs and reject missing or invalid columns.

## Screenshots

Capture and add screenshots after running locally: dashboard, analysis of `sample_traffic.csv`, and `/model-info` results. No screenshot is claimed yet.

## Limitations and next steps

The dataset is historical, measured recall is limited, and these flow features alone cannot confirm an intrusion. This dashboard does not monitor live traffic. Future work: investigate recall and threshold selection on a dedicated validation set, try newer datasets, compare models, calibrate probabilities, and add live flow collection and authentication.

## CV wording

**Network Intrusion Detection System | Python, scikit-learn, FastAPI, JavaScript**

- Trained a reproducible Random Forest pipeline on NSL-KDD flow features and evaluated it on the separate test split (77.9% accuracy, 63.2% attack recall).
- Built FastAPI single-record and CSV batch inference endpoints with a browser dashboard for classification summaries and visual alerts.

## How to explain this project in an interview

> It analyzes network-flow summaries and marks them Normal or Attack using the historical NSL-KDD dataset. Each feature describes a connection, such as its protocol, byte counts, or recent host behavior. I fitted missing-value handling and category encoding on the training data, then trained a Random Forest because it handles mixed, nonlinear patterns well without complex tuning. Precision asks what fraction of predicted attacks were attacks; recall asks what fraction of actual attacks we caught. Recall is particularly important here, and my model misses about 37% of test attacks. The confusion matrix shows 9,448 correctly classified normal flows, 8,113 correctly classified attacks, 263 false alarms, and 4,720 missed attacks. FastAPI loads the saved pipeline and sends predictions to the dashboard. With more time I would work on recall using a validation split and a more recent dataset.

## GitHub

Suggested repository: `ml-network-intrusion-detection`. Description: “Machine learning-based network intrusion detection with FastAPI and a traffic analysis dashboard.” Topics: `machine-learning`, `cybersecurity`, `intrusion-detection`, `network-security`, `python`, `fastapi`, `scikit-learn`.

Create an empty GitHub repository, then from this folder run `git init`, `git add .`, `git commit -m "Build educational ML network intrusion detector"`, `git branch -M main`, `git remote add origin <your-repo-URL>`, `git push -u origin main`. Check `git status` and `git ls-files` before pushing; `data/*.txt` and `models/*.joblib` should not appear.
