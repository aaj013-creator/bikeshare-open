"""Exercise 4: predict demand minus yesterday, then invert in ride units.

Run validation first; use --test only after freezing the experiment.
Does not overwrite the untransformed reports/metrics.json.
"""
import argparse
import json
from pathlib import Path

from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, r2_score

from src.config import TARGET
from src.features import build_features, feature_columns
from src.ingest import load_raw
from src.train import MODELS, temporal_split


def experiment(include_test=False):
    df = build_features(load_raw())
    cols = feature_columns(df)
    train, valid, test = temporal_split(df)
    models = {name: clone(model).fit(train[cols], train[TARGET])
              for name, model in MODELS.items()}
    residual = clone(MODELS['hgb']).fit(
        train[cols], train[TARGET] - train['cnt_lag_1'])
    results = {}
    for name, part in [('valid', valid)] + ([('test', test)] if include_test else []):
        predictions = {key: model.predict(part[cols]) for key, model in models.items()}
        predictions['hgb_delta'] = residual.predict(part[cols]) + part['cnt_lag_1'].to_numpy()
        results[name] = {key: {
            'r2': round(float(r2_score(part[TARGET], pred)), 4),
            'mae': round(float(mean_absolute_error(part[TARGET], pred)), 1)
        } for key, pred in predictions.items()}
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--test', action='store_true')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = experiment(args.test)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
