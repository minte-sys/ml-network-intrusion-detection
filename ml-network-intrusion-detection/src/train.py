import json
import numpy as np
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from common import ROOT, FEATURES, CATEGORIES, NUMERIC, read_dataset, validate_frame

train = read_dataset(ROOT/'data/KDDTrain+.txt')
test = read_dataset(ROOT/'data/KDDTest+.txt')
X_train, X_test = validate_frame(train), validate_frame(test)
y_train = (train.attack_type != 'normal').astype(int)
y_test = (test.attack_type != 'normal').astype(int)
preprocessor = ColumnTransformer([
    ('numbers', SimpleImputer(strategy='median'), NUMERIC),
    ('categories', OneHotEncoder(handle_unknown='ignore'), CATEGORIES),
])
model = Pipeline([('preprocessor',preprocessor), ('classifier',RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, min_samples_leaf=2))])
model.fit(X_train,y_train)
pred = model.predict(X_test)
prob = model.predict_proba(X_test)[:,1]
metrics = {'dataset':'NSL-KDD KDDTrain+ / KDDTest+', 'train_rows':len(train),'test_rows':len(test), 'features':FEATURES,
 'train_class_counts':{'normal':int((y_train==0).sum()), 'attack':int((y_train==1).sum())},
 'test_class_counts':{'normal':int((y_test==0).sum()), 'attack':int((y_test==1).sum())},
 'train_missing_cells':int(train.isna().sum().sum()),'test_missing_cells':int(test.isna().sum().sum()),
 'accuracy':accuracy_score(y_test,pred),'precision':precision_score(y_test,pred),
 'recall':recall_score(y_test,pred),'f1':f1_score(y_test,pred), 'roc_auc':roc_auc_score(y_test,prob),
 'confusion_matrix':confusion_matrix(y_test,pred,labels=[0,1]).tolist()}
ROOT.joinpath('models').mkdir(exist_ok=True)
joblib.dump(model,ROOT/'models/model.joblib')
(ROOT/'models/metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps({k:v for k,v in metrics.items() if k not in ('features',)},indent=2))
