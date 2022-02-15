import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split


def split_data(data_input, split_index, value):
    data_output = []
    for data in data_input:
        if data[split_index] == value:
            new_data = data[:split_index]
            new_data.extend(data[split_index + 1:])
            data_output.append(new_data)
    return data_output


def calculate_entropy(data_input):
    label_list = [data[-1] for data in data_input]
    entropy = 0
    for key in Counter(label_list).keys():
        probability = float(Counter(label_list)[key]) / len(data_input)
        entropy -= probability * np.log2(probability)
    return entropy


def compare_information_gain(data_input):
    branch_index = 0
    information_gain = 0
    for i_branch in range(len(data_input[0]) - 1):
        new_entropy = 0
        branch_data = [data[i_branch] for data in data_input]
        branch_data_set = set(branch_data)
        for value in branch_data_set:
            new_data = split_data(data_input, i_branch, value)
            probability = float(len(new_data)) / len(data_input)
            new_entropy += probability * calculate_entropy(new_data)
        # Compare the information gain
        new_information_gain = calculate_entropy(data_input) - new_entropy
        if new_information_gain > information_gain:
            information_gain = new_information_gain
            branch_index = i_branch
    return branch_index


def create_decision_tree(data_input, attribute):
    label_list = [data[-1] for data in data_input]
    # If all instances belong to the same class
    if label_list.count(label_list[0]) == len(label_list):
        return label_list[0]
    # If there are no more attributes that can be tested
    if len(data_input[0]) == 1:
        return max(label_list, key=label_list.count)
    # Decide the attribute
    branch_index = compare_information_gain(data_input)
    branch = attribute[branch_index]
    decision_tree = {branch: {}}
    branch_data = [data[branch_index] for data in data_input]
    branch_data_set = set(branch_data)
    del (attribute[branch_index])
    for value in branch_data_set:
        new_label = attribute[:]
        decision_tree[branch][value] = create_decision_tree(split_data(data_input, branch_index, value), new_label)
    return decision_tree


def predict(tree, attribute_list, test_data):
    label = list(tree.keys())[0]
    label_index = attribute_list.index(label)
    dictionary = tree[label]
    value = test_data[label_index]
    if type(dictionary[value]).__name__ == "dict":
        prediction = predict(dictionary[value], attribute_list, test_data)
    else:
        prediction = dictionary[value]
    return prediction


if __name__ == '__main__':
    # Load data
    df = pd.read_csv('house_votes_84.csv')
    iteration = 0
    accuracy = []
    while iteration < 100:
        print(iteration)
        try:
            # Shuffle the dataset
            df_sf = shuffle(df)
            y = df_sf[df.columns[16]]
            # Randomly partition the dataset
            data_train, data_test, y_train, y_test = train_test_split(df_sf, y, test_size=0.2)
            # Normalize the dataset
            X_train_data_list = data_train.values.tolist()
            X_test_data_list = data_test.values.tolist()
            X_train_attribute_list = data_train.keys().to_list()
            # Create decision tree
            X_train_attribute_list_copy = X_train_attribute_list[:]
            decisionTree = create_decision_tree(X_train_data_list, X_train_attribute_list_copy)
            print(decisionTree)
            # Make prediction
            correct = 0
            for index in range(0, len(y_test)):
                classLabel = predict(decisionTree, X_train_attribute_list, X_test_data_list[index])
                if classLabel == y_test.values[index]:
                    correct += 1
            accuracy.append(correct / len(y_test))
            iteration += 1
        except:
            pass
            continue
    std = np.std(accuracy)
    avg = np.mean(accuracy)
    plt.hist(accuracy, weights=np.ones_like(accuracy) / len(accuracy), align="left", rwidth=0.9)
    plt.xlabel('Accuracy')
    plt.ylabel('Accuracy frequency over training data')
    plt.savefig("FigureDT2.eps", dpi=600, format="eps")
