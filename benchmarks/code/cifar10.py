"""
Author: Haoyin Xu
"""
import time
import argparse
import numpy as np
import torchvision.datasets as datasets
from numpy.random import permutation
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from river import tree
from skgarden import MondrianForestClassifier
from sdtf import StreamDecisionForest, CascadeStreamForest


def write_result(filename, acc_ls):
    """Writes results to specified text file"""
    output = open(filename, "w")
    for acc in acc_ls:
        output.write(str(acc) + "\n")


def prediction(classifier):
    """Generates predictions from model"""
    predictions = classifier.predict(X_test)

    p_t = 0
    for i in range(X_test.shape[0]):
        if predictions[i] == y_test[i]:
            p_t += 1

    return p_t / X_test.shape[0]


def experiment_dt():
    """Runs experiments for Batch Decision Tree"""
    dt_l = []
    train_time_l = []
    test_time_l = []

    dt = DecisionTreeClassifier()

    for i in range(500):
        X_t = X_r[: (i + 1) * 100]
        y_t = y_r[: (i + 1) * 100]

        # Train the model
        start_time = time.perf_counter()
        dt.fit(X_t, y_t)
        end_time = time.perf_counter()
        train_time_l.append(end_time - start_time)

        # Test the model
        start_time = time.perf_counter()
        dt_l.append(prediction(dt))
        end_time = time.perf_counter()
        test_time_l.append(end_time - start_time)

    return dt_l, train_time_l, test_time_l


def experiment_rf():
    """Runs experiments for Random Forest"""
    rf_l = []
    train_time_l = []
    test_time_l = []

    rf = RandomForestClassifier()

    for i in range(500):
        X_t = X_r[: (i + 1) * 100]
        y_t = y_r[: (i + 1) * 100]

        # Train the model
        start_time = time.perf_counter()
        rf.fit(X_t, y_t)
        end_time = time.perf_counter()
        train_time_l.append(end_time - start_time)

        # Test the model
        start_time = time.perf_counter()
        rf_l.append(prediction(rf))
        end_time = time.perf_counter()
        test_time_l.append(end_time - start_time)

    return rf_l, train_time_l, test_time_l


def experiment_ht():
    """Runs experiments for Hoeffding Tree"""
    ht_l = []
    train_time_l = []
    test_time_l = []

    ht = tree.HoeffdingTreeClassifier(max_size=1000, grace_period=2)

    for i in range(X_train.shape[0]):
        X_t = X_r[i]
        y_t = y_r[i]

        idx = range(1024)
        X_t = dict(zip(idx, X_t))

        start_time = time.perf_counter()
        ht.learn_one(X_t, y_t)
        end_time = time.perf_counter()
        train_time_l.append(end_time - start_time)

        if i > 0 and (i + 1) % 100 == 0:
            p_t = 0.0
            start_time = time.perf_counter()
            for j in range(X_test.shape[0]):
                y_pred = ht.predict_one(X_test[j])
                if y_pred == y_test[j]:
                    p_t += 1
            ht_l.append(p_t / X_test.shape[0])
            print(p_t / X_test.shape[0], i)
            end_time = time.perf_counter()
            test_time_l.append(end_time - start_time)

    # Reformat the train times
    new_train_time_l = []
    for i in range(1, X_train.shape[0]):
        train_time_l[i] += train_time_l[i - 1]
        if i > 0 and (i + 1) % 100 == 0:
            new_train_time_l.append(train_time_l[i])
    train_time_l = new_train_time_l

    return ht_l, train_time_l, test_time_l


def experiment_mf():
    """Runs experiments for Mondrian Forest"""
    mf_l = []
    train_time_l = []
    test_time_l = []

    mf = MondrianForestClassifier(n_estimators=10)

    for i in range(500):
        X_t = X_r[i * 100 : (i + 1) * 100]
        y_t = y_r[i * 100 : (i + 1) * 100]

        # Train the model
        start_time = time.perf_counter()
        mf.partial_fit(X_t, y_t)
        end_time = time.perf_counter()
        train_time_l.append(end_time - start_time)

        # Test the model
        start_time = time.perf_counter()
        mf_l.append(prediction(mf))
        end_time = time.perf_counter()
        test_time_l.append(end_time - start_time)

    # Reformat the train times
    for i in range(1, 500):
        train_time_l[i] += train_time_l[i - 1]

    return mf_l, train_time_l, test_time_l


def experiment_sdt():
    """Runs experiments for Stream Decision Tree"""
    sdt_l = []
    train_time_l = []
    test_time_l = []

    sdt = DecisionTreeClassifier()

    for i in range(500):
        X_t = X_r[i * 100 : (i + 1) * 100]
        y_t = y_r[i * 100 : (i + 1) * 100]

        # Train the model
        start_time = time.perf_counter()
        sdt.partial_fit(X_t, y_t, classes=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        end_time = time.perf_counter()
        train_time_l.append(end_time - start_time)

        # Test the model
        start_time = time.perf_counter()
        sdt_l.append(prediction(sdt))
        end_time = time.perf_counter()
        test_time_l.append(end_time - start_time)

    # Reformat the train times
    for i in range(1, 500):
        train_time_l[i] += train_time_l[i - 1]

    return sdt_l, train_time_l, test_time_l


def experiment_sdf():
    """Runs experiments for Stream Decision Forest"""
    sdf_l = []
    train_time_l = []
    test_time_l = []

    sdf = StreamDecisionForest()

    for i in range(500):
        X_t = X_r[i * 100 : (i + 1) * 100]
        y_t = y_r[i * 100 : (i + 1) * 100]

        # Train the model
        start_time = time.perf_counter()
        sdf.partial_fit(X_t, y_t, classes=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        end_time = time.perf_counter()
        train_time_l.append(end_time - start_time)

        # Test the model
        start_time = time.perf_counter()
        sdf_l.append(prediction(sdf))
        end_time = time.perf_counter()
        test_time_l.append(end_time - start_time)

    # Reformat the train times
    for i in range(1, 500):
        train_time_l[i] += train_time_l[i - 1]

    return sdf_l, train_time_l, test_time_l


def experiment_csf():
    """Runs experiments for Cascade Stream Forest"""
    csf_l = []
    train_time_l = []
    test_time_l = []

    csf = CascadeStreamForest()

    for i in range(500):
        X_t = X_r[i * 100 : (i + 1) * 100]
        y_t = y_r[i * 100 : (i + 1) * 100]

        # Train the model
        start_time = time.perf_counter()
        csf.partial_fit(X_t, y_t, classes=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        end_time = time.perf_counter()
        train_time_l.append(end_time - start_time)

        # Test the model
        start_time = time.perf_counter()
        csf_l.append(prediction(csf))
        end_time = time.perf_counter()
        test_time_l.append(end_time - start_time)

    # Reformat the train times
    for i in range(1, 500):
        train_time_l[i] += train_time_l[i - 1]

    return csf_l, train_time_l, test_time_l


# Prepare CIFAR data
# Normalize
scale = np.mean(np.arange(0, 256))
normalize = lambda x: (x - scale) / scale

# Train data
cifar_trainset = datasets.CIFAR10(root="../", train=True, download=True, transform=None)
X_train = normalize(cifar_trainset.data)
y_train = np.array(cifar_trainset.targets)

# Test data
cifar_testset = datasets.CIFAR10(root="../", train=False, download=True, transform=None)
X_test = normalize(cifar_testset.data)
y_test = np.array(cifar_testset.targets)

X_train = X_train.reshape(-1, 32 * 32 * 3)
X_test = X_test.reshape(-1, 32 * 32 * 3)

# Parse classifier choices
parser = argparse.ArgumentParser()
parser.add_argument("-all", help="all classifiers", required=False, action="store_true")
parser.add_argument("-dt", help="decision forests", required=False, action="store_true")
parser.add_argument("-rf", help="random forests", required=False, action="store_true")
parser.add_argument("-ht", help="hoeffding trees", required=False, action="store_true")
parser.add_argument("-mf", help="mondrian forests", required=False, action="store_true")
parser.add_argument(
    "-sdt", help="stream decision trees", required=False, action="store_true"
)
parser.add_argument(
    "-sdf", help="stream decision forests", required=False, action="store_true"
)
parser.add_argument(
    "-csf", help="cascade stream forests", required=False, action="store_true"
)
args = parser.parse_args()

# Perform experiments
if args.all or args.dt:
    dt_acc_l = []
    dt_train_t_l = []
    dt_test_t_l = []
    for i in range(10):
        p = permutation(X_train.shape[0])

        X_r = X_train[p]
        y_r = y_train[p]

        dt_acc, dt_train_t, dt_test_t = experiment_dt()
        dt_acc_l.append(dt_acc)
        dt_train_t_l.append(dt_train_t)
        dt_test_t_l.append(dt_test_t)

        write_result("../results/dt/cifar10_acc.txt", dt_acc_l)
        write_result("../results/dt/cifar10_train_t.txt", dt_train_t_l)
        write_result("../results/dt/cifar10_test_t.txt", dt_test_t_l)

if args.all or args.rf:
    rf_acc_l = []
    rf_train_t_l = []
    rf_test_t_l = []
    for i in range(10):
        p = permutation(X_train.shape[0])

        X_r = X_train[p]
        y_r = y_train[p]

        rf_acc, rf_train_t, rf_test_t = experiment_rf()
        rf_acc_l.append(rf_acc)
        rf_train_t_l.append(rf_train_t)
        rf_test_t_l.append(rf_test_t)

        write_result("../results/rf/cifar10_acc.txt", rf_acc_l)
        write_result("../results/rf/cifar10_train_t.txt", rf_train_t_l)
        write_result("../results/rf/cifar10_test_t.txt", rf_test_t_l)

if args.all or args.ht:
    ht_acc_l = []
    ht_train_t_l = []
    ht_test_t_l = []
    for i in range(10):
        p = permutation(X_train.shape[0])

        X_r = X_train[p]
        y_r = y_train[p]

        ht_acc, ht_train_t, ht_test_t = experiment_ht()
        ht_acc_l.append(ht_acc)
        ht_train_t_l.append(ht_train_t)
        ht_test_t_l.append(ht_test_t)

        write_result("../results/ht/cifar10_acc.txt", ht_acc_l)
        write_result("../results/ht/cifar10_train_t.txt", ht_train_t_l)
        write_result("../results/ht/cifar10_test_t.txt", ht_test_t_l)

if args.all or args.mf:
    mf_acc_l = []
    mf_train_t_l = []
    mf_test_t_l = []
    for i in range(10):
        p = permutation(X_train.shape[0])

        X_r = X_train[p]
        y_r = y_train[p]

        mf_acc, mf_train_t, mf_test_t = experiment_mf()
        mf_acc_l.append(mf_acc)
        mf_train_t_l.append(mf_train_t)
        mf_test_t_l.append(mf_test_t)

        write_result("../results/mf/cifar10_acc.txt", mf_acc_l)
        write_result("../results/mf/cifar10_train_t.txt", mf_train_t_l)
        write_result("../results/mf/cifar10_test_t.txt", mf_test_t_l)

if args.all or args.sdt:
    sdt_acc_l = []
    sdt_train_t_l = []
    sdt_test_t_l = []
    for i in range(10):
        p = permutation(X_train.shape[0])

        X_r = X_train[p]
        y_r = y_train[p]

        sdt_acc, sdt_train_t, sdt_test_t = experiment_sdt()
        sdt_acc_l.append(sdt_acc)
        sdt_train_t_l.append(sdt_train_t)
        sdt_test_t_l.append(sdt_test_t)

        write_result("../results/sdt/cifar10_acc.txt", sdt_acc_l)
        write_result("../results/sdt/cifar10_train_t.txt", sdt_train_t_l)
        write_result("../results/sdt/cifar10_test_t.txt", sdt_test_t_l)

if args.all or args.sdf:
    sdf_acc_l = []
    sdf_train_t_l = []
    sdf_test_t_l = []
    for i in range(10):
        p = permutation(X_train.shape[0])

        X_r = X_train[p]
        y_r = y_train[p]

        sdf_acc, sdf_train_t, sdf_test_t = experiment_sdf()
        sdf_acc_l.append(sdf_acc)
        sdf_train_t_l.append(sdf_train_t)
        sdf_test_t_l.append(sdf_test_t)

        write_result("../results/sdf/cifar10_acc.txt", sdf_acc_l)
        write_result("../results/sdf/cifar10_train_t.txt", sdf_train_t_l)
        write_result("../results/sdf/cifar10_test_t.txt", sdf_test_t_l)

if args.all or args.csf:
    csf_acc_l = []
    csf_train_t_l = []
    csf_test_t_l = []
    for i in range(10):
        p = permutation(X_train.shape[0])

        X_r = X_train[p]
        y_r = y_train[p]

        csf_acc, csf_train_t, csf_test_t = experiment_csf()
        csf_acc_l.append(csf_acc)
        csf_train_t_l.append(csf_train_t)
        csf_test_t_l.append(csf_test_t)

        write_result("../results/csf/cifar10_acc.txt", csf_acc_l)
        write_result("../results/csf/cifar10_train_t.txt", csf_train_t_l)
        write_result("../results/csf/cifar10_test_t.txt", csf_test_t_l)