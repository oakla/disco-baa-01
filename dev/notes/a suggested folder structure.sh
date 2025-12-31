my-project/
├─ README.md
├─ pyproject.toml        # or requirements.txt/conda env
├─ .gitignore
├─ .env.example
├─ Makefile              # optional, nice for repeatable commands
├─ configs/              # YAML/TOML configs (paths, models, params)
│
├─ data/
│  ├─ raw/               # immutable original data
│  ├─ external/          # third-party datasets
│  ├─ interim/           # cleaned/merged but not final
│  └─ processed/         # model-ready data
│
├─ notebooks/            # EDA & experiments (numbered)
│  ├─ 01_eda.ipynb
│  ├─ 02_features.ipynb
│  └─ 03_modeling.ipynb
│
├─ src/
│  └─ my_project/
│     ├─ __init__.py
│     ├─ data/           # loading/validation
│     ├─ features/       # feature engineering
│     ├─ models/         # training/inference code
│     ├─ evaluation/     # metrics, analysis
│     └─ utils/
│
├─ scripts/              # CLI-ish entry points calling src/
│  ├─ download_data.py
│  ├─ make_dataset.py
│  ├─ train.py
│  └─ evaluate.py
│
├─ models/               # serialized models, checkpoints
│
├─ reports/
│  ├─ figures/
│  └─ report.md          # or slides
│
└─ tests/
   ├─ test_data.py
   ├─ test_features.py
   └─ test_models.py
