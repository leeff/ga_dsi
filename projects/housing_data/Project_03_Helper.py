import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import pprint as pprint


# Define the values to be processed so I can do the same preprocessing to both train and test set
class Project_03_Helper(object):

    def __init__(self):

        self.features_to_drop = []
        self.t_features_to_drop = []

        # for imputing
        self.impute_fill_values = {}
        self.impute_missing_values = {}
        self.features_to_impute = []
        self.t_features_to_impute = []


        self.standard_scalers = {}
        self.features_to_get_dummies_with_drop_first = []
        self.features_to_get_dummies_without_drop_first = []
        self.t_features_to_get_dummies_with_drop_first = []
        self.t_features_to_get_dummies_without_drop_first = []




    def __str__(self):

        _str = ''.join( \
                   ['Features to Drop:\n',  \
                   str(self.features_to_drop),  \
                   '\n\nFeatures to Impute:\n'] )

        for f in self.features_to_impute:
            _str += ''.join('Feature {} : Fill {} with {}.\n'.format(f , str(self.impute_missing_values[f]), str(self.impute_fill_values[f])))

        _str += '\nFeatures to Get Dummies with Drop First:\n'
        _str += str(self.features_to_get_dummies_with_drop_first)
        _str += '\n\nFeatures to Get Dummies without Drop First:\n'
        _str += str(self.features_to_get_dummies_without_drop_first)

        return _str


    def add_feature_to_make_dummy(self, feature, drop_first=False):
        _list = self.features_to_get_dummies_without_drop_first
        if (drop_first):
            _list = self.features_to_get_dummies_with_drop_first

        _features = []
        if isinstance(feature, list):
            _features = feature
        else:
            _features = [feature]

        for f in _features:
            if f in _list:
                raise Exception(f + ' already in dummy list!')
            else:
                _list.append(f)


    def add_feature_to_drop(self, feature):
        _features = []
        if isinstance(feature, list):
            _features = feature
        else:
            _features = [feature]

        for f in _features:
            if f in self.features_to_drop:
                raise Exception(f + ' already in drop list!')
            else:
                self.features_to_drop.append(f)


    def add_feature_to_impute(self,feature,df=None,strategy=None,missing_values=None, fill_value=None):

        _features = []
        if isinstance(feature, list):
            _features = feature
        else:
            _features = [feature]

        for f in _features:

            if f in self.features_to_impute:
                raise Exception(f + ' already in impute list!')

            if (strategy == 'median'):
                self.impute_fill_values[f] = df[f].median()
            elif (strategy == 'mean'):
                self.impute_fill_values[f] = df[f].mean()
            else:
                self.impute_fill_values[f] = fill_value
            self.impute_missing_values[f] = missing_values
            self.features_to_impute.append(f)


    def add_feature_to_impute_with_median(self,feature,df,missing_values=None):
        self.add_feature_to_impute(feature,df,strategy='median',missing_values=missing_values)


    def transform(self, df):

        df_columns = df.columns.values

        # make sure every feature to process is found in df
        self.t_features_to_drop = [x for x in self.features_to_drop if x in df_columns]
        self.t_features_to_impute = [x for x in self.features_to_impute if x in df_columns]
        self.t_features_to_get_dummies_with_drop_first = [x for x in self.features_to_get_dummies_with_drop_first if x in df_columns]
        self.t_features_to_get_dummies_without_drop_first = [x for x in self.features_to_get_dummies_without_drop_first if x in df_columns]

        # drop features
        if len(self.t_features_to_drop) > 0:
            df.drop(columns=self.t_features_to_drop, inplace=True, errors='raise')

        # impute values
        for f in self.t_features_to_impute:
            if (self.impute_missing_values[f] == None):
                df.loc[df[f].isnull(),f] = self.impute_fill_values[f]
            else:
                df.loc[df[f]==self.impute_missing_values,f] = self.impute_fill_values[f]

        # pd.getDummies
        if (len(self.t_features_to_get_dummies_with_drop_first)>0):
            df = pd.get_dummies(df, columns=self.t_features_to_get_dummies_with_drop_first, drop_first=True)
        if (len(self.t_features_to_get_dummies_without_drop_first)>0):
            df = pd.get_dummies(df, columns=self.t_features_to_get_dummies_without_drop_first, drop_first=False)

        return df



    def find_nulls(self, df):
        column_exist_null_selector = df.isnull().sum() > 0
        df.isnull().sum()[column_exist_null_selector]
        return pd.DataFrame(data={'number of nulls': df.isnull().sum()[column_exist_null_selector],\
                   'object type':df.dtypes[column_exist_null_selector]}).sort_values(by='number of nulls', ascending=False)
