"""Source-backed starting candidate; the evaluated controller may change it."""
from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

FEATURES = [
    "MSSubClass", "LotArea", "OverallQual", "OverallCond", "YearBuilt", "YearRemodAdd",
    "1stFlrSF", "2ndFlrSF", "LowQualFinSF", "GrLivArea", "FullBath", "HalfBath",
    "BedroomAbvGr", "KitchenAbvGr", "TotRmsAbvGrd", "Fireplaces", "WoodDeckSF",
    "OpenPorchSF", "EnclosedPorch", "3SsnPorch", "ScreenPorch", "PoolArea",
    "MiscVal", "MoSold", "YrSold",
]


def fit_predict(train: pd.DataFrame, features: pd.DataFrame):
    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestRegressor(n_estimators=100, random_state=1, n_jobs=1)),
    ])
    model.fit(train[FEATURES], train["SalePrice"])
    return model.predict(features[FEATURES])
