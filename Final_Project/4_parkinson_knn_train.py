import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt


def f1_score(actual, predicted):
    TP = np.sum(np.multiply([i == True for i in predicted], actual))
    TN = np.sum(np.multiply([i == False for i in predicted], [not j for j in actual]))
    FP = np.sum(np.multiply([i == True for i in predicted], [not j for j in actual]))
    FN = np.sum(np.multiply([i == False for i in predicted], actual))
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    if precision != 0 and recall != 0:
        f1 = (2 * precision * recall) / (precision + recall)
    else:
        f1 = 0
    return f1


def f1_macro(y_true, y_pred):
    macro = []
    for i in np.unique(y_true):
        modified_true = [i == j for j in y_true]
        modified_pred = [i == j for j in y_pred]
        score = f1_score(modified_true, modified_pred)
        macro.append(score)
    return np.mean(macro)


def minmax_scale(df_in):
    df_norm = (df_in - df_in.min()) / (df_in.max() - df_in.min())
    return df_norm


if __name__ == '__main__':
    # Load data
    df = pd.read_csv('parkinsons.csv', sep=',')
    col_class = df.pop('Diagnosis')
    df = minmax_scale(df)
    df.insert(len(df.columns), 'Diagnosis', col_class)

    list_target = df['Diagnosis'].unique()
    df1 = df[df['Diagnosis'].isin([list_target[0]])]
    df0 = df[df['Diagnosis'].isin([list_target[1]])]
    # Split into folds
    k_fold = []
    fold_size1 = math.ceil(len(df1) / 10)
    fold_size0 = math.ceil(len(df0) / 10)
    for k in range(0, 9):
        fold1 = df1.sample(n=fold_size1, random_state=587)
        fold0 = fold1.append(df0.sample(n=fold_size0, random_state=587))
        df1 = df1[~df1.index.isin(fold1.index)]
        df0 = df0[~df0.index.isin(fold0.index)]
        k_fold.append(fold0)
    k_fold.append(df1.append(df0))

    k_list = range(1, 22, 2)
    final_accuracy = {}

    # Train the k-NN algorithm using training set
    accuracy = []
    f1 = []
    for k in k_list:
        print('k = ', k)
        fold_idx = 0
        accuracy_k = []
        f1_k = []
        while fold_idx < 10:
            print('fold_idx = ', fold_idx)
            # Split to train and test dataset
            k_fold_copy = k_fold.copy()
            data_test = k_fold[fold_idx]
            del k_fold_copy[fold_idx]
            data_train = pd.concat(k_fold_copy).sample(n=len(df) - len(data_test.index), replace=True, random_state=587)
            X_train = data_train.drop('Diagnosis', axis=1).values
            y_train = data_train['Diagnosis'].values.astype(int)
            X_test = data_test.drop('Diagnosis', axis=1).values
            y_test = data_test['Diagnosis'].values.astype(int)

            X_train = pd.DataFrame(X_train)
            X_test = pd.DataFrame(X_test)
            y_train = pd.Series(y_train.tolist())
            y_test = pd.Series(y_test.tolist())

            y_pred = []
            for index1, row1 in X_test.iterrows():
                x = row1.values
                distance = [np.sqrt(np.sum((row2.values - x) ** 2)) for index2, row2 in X_train.iterrows()]
                idx_sort = np.argsort(distance)
                y_idx_sort = y_train.values[idx_sort]
                y_top_k = y_idx_sort[:k]
                pred = max(set(y_top_k), key=y_top_k.tolist().count)
                y_pred.append(pred)
            y_test = y_test.tolist()
            f1_i = f1_macro(y_test, y_pred)
            accuracy_i = np.sum(np.array(y_pred) == np.array(y_test)) / len(y_test)
            f1_k.append(f1_i)
            accuracy_k.append(accuracy_i)
            fold_idx += 1
        f1_avg = sum(f1_k) / len(f1_k)
        accuracy_avg = sum(accuracy_k) / len(accuracy_k)
        print('accuracy_avg = ', accuracy_avg)
        print('f1_avg = ', f1_avg)
        accuracy.append(accuracy_avg)
        f1.append(f1_avg)

    plt.plot(k_list, accuracy, '.-', markersize=10, color='#1f77b4')
    plt.xlabel('Value of k')
    plt.ylabel('Cost function')
    plt.show()
