"""
Author: Haoyin Xu
"""
import time
import tracemalloc
import argparse
from numpy.random import permutation
import openml
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from river import tree
from skgarden import MondrianForestClassifier
from sdtf import StreamDecisionForest

from toolbox import *


def experiment_dt():
    """Runs experiments for Batch Decision Tree"""
    dt_l = []
    train_time_l = []
    test_time_l = []
    v_m_l = []
    v_max_l = []
    n_node_l = []
    size_l = []

    dt = DecisionTreeClassifier()

    for i in range(23):
        X_t = X_r[: (i + 1) * 100]
        y_t = y_r[: (i + 1) * 100]

        # Train the model
        start_time = time.perf_counter()

        tracemalloc.start()

        dt.fit(X_t, y_t)

        v_m, v_max = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        end_time = time.perf_counter()
        train_time_l.append(end_time - start_time)

        # Check size
        size = clf_size(dt, "../results/dt/temp.pickle")
        size_l.append(size)

        # Check node counts
        n_node = node_count(dt, forest=False)
        n_node_l.append(n_node)

        # Test the model
        start_time = time.perf_counter()

        tracemalloc.start()

        dt_l.append(prediction(dt, X_test, y_test))

        v_m_temp, v_max_temp = tracemalloc.get_traced_memory()
        v_m = (v_m, v_m_temp)
        v_max = (v_max, v_max_temp)
        tracemalloc.stop()

        end_time = time.perf_counter()
        test_time_l.append(end_time - start_time)

        # Check memory
        v_max_l.append(v_max)
        v_m_l.append(v_m)

    return dt_l, train_time_l, test_time_l, v_m_l, v_max_l, n_node_l, size_l


def experiment_rf():
    """Runs experiments for Random Forest"""
    rf_l = []
    train_time_l = []
    test_time_l = []
    v_m_l = []
    v_max_l = []
    n_node_l = []
    size_l = []

    rf = RandomForestClassifier(n_estimators=10)

    for i in range(23):
        X_t = X_r[: (i + 1) * 100]
        y_t = y_r[: (i + 1) * 100]

        # Train the model
        start_time = time.perf_counter()

        tracemalloc.start()

        rf.fit(X_t, y_t)

        v_m, v_max = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        end_time = time.perf_counter()
        train_time_l.append(end_time - start_time)

        # Check size
        size = clf_size(rf, "../results/rf/temp.pickle")
        size_l.append(size)

        # Check node counts
        n_node = node_count(rf, forest=True)
        n_node_l.append(n_node)

        # Test the model
        start_time = time.perf_counter()

        tracemalloc.start()

        rf_l.append(prediction(rf, X_test, y_test))

        v_m_temp, v_max_temp = tracemalloc.get_traced_memory()
        v_m = (v_m, v_m_temp)
        v_max = (v_max, v_max_temp)
        tracemalloc.stop()

        end_time = time.perf_counter()
        test_time_l.append(end_time - start_time)

        # Check memory
        v_max_l.append(v_max)
        v_m_l.append(v_m)

    return rf_l, train_time_l, test_time_l, v_m_l, v_max_l, n_node_l, size_l


def experiment_ht():
    """Runs experiments for Hoeffding Tree"""
    ht_l = []
    train_time_l = []
    test_time_l = []
    v_m_l = []
    v_max_l = []
    n_node_l = []
    size_l = []

    ht = tree.HoeffdingTreeClassifier(max_size=1000, grace_period=2)

    for i in range(2300):
        X_t = X_r[i]
        y_t = y_r[i]

        idx = range(60)
        X_t = dict(zip(idx, X_t))

        start_time = time.perf_counter()

        tracemalloc.start()

        ht.learn_one(X_t, y_t)

        v_m, v_max = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        end_time = time.perf_counter()
        train_time_l.append(end_time - start_time)

        if i > 0 and (i + 1) % 100 == 0:
            # Check size
            size = clf_size(ht, "../results/ht/temp.pickle")
            size_l.append(size)

            # Check node counts
            n_node = ht.n_nodes
            n_node_l.append(n_node)

            p_t = 0.0
            start_time = time.perf_counter()

            tracemalloc.start()

            for j in range(X_test.shape[0]):
                y_pred = ht.predict_one(X_test[j])
                if y_pred == y_test[j]:
                    p_t += 1
            ht_l.append(p_t / X_test.shape[0])

            v_m_temp, v_max_temp = tracemalloc.get_traced_memory()
            v_m = (v_m, v_m_temp)
            v_max = (v_max, v_max_temp)
            tracemalloc.stop()

            end_time = time.perf_counter()
            test_time_l.append(end_time - start_time)

            # Check memory
            v_max_l.append(v_max)
            v_m_l.append(v_m)

    # Reformat the train times
    new_train_time_l = []
    for i in range(1, 2300):
        train_time_l[i] += train_time_l[i - 1]
        if i > 0 and (i + 1) % 100 == 0:
            new_train_time_l.append(train_time_l[i])
    train_time_l = new_train_time_l

    return ht_l, train_time_l, test_time_l, v_m_l, v_max_l, n_node_l, size_l


def experiment_mf():
    """Runs experiments for Mondrian Forest"""
    mf_l = []
    train_time_l = []
    test_time_l = []
    v_m_l = []
    v_max_l = []
    n_node_l = []
    size_l = []

    mf = MondrianForestClassifier(n_estimators=10)

    for i in range(23):
        X_t = X_r[i * 100 : (i + 1) * 100]
        y_t = y_r[i * 100 : (i + 1) * 100]

        # Train the model
        start_time = time.perf_counter()

        tracemalloc.start()

        mf.partial_fit(X_t, y_t)

        v_m, v_max = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        end_time = time.perf_counter()
        train_time_l.append(end_time - start_time)

        # Check size
        size = clf_size(mf, "../results/mf/temp.pickle")
        size_l.append(size)

        # Check node counts
        n_node = node_count(mf, forest=True)
        n_node_l.append(n_node)

        # Test the model
        start_time = time.perf_counter()

        tracemalloc.start()

        mf_l.append(prediction(mf, X_test, y_test))

        v_m_temp, v_max_temp = tracemalloc.get_traced_memory()
        v_m = (v_m, v_m_temp)
        v_max = (v_max, v_max_temp)
        tracemalloc.stop()

        end_time = time.perf_counter()
        test_time_l.append(end_time - start_time)

        # Check memory
        v_max_l.append(v_max)
        v_m_l.append(v_m)

    # Reformat the train times
    for i in range(1, 23):
        train_time_l[i] += train_time_l[i - 1]

    return mf_l, train_time_l, test_time_l, v_m_l, v_max_l, n_node_l, size_l


def experiment_sdt():
    """Runs experiments for Stream Decision Tree"""
    sdt_l = []
    train_time_l = []
    test_time_l = []
    v_m_l = []
    v_max_l = []
    n_node_l = []
    size_l = []

    sdt = DecisionTreeClassifier()

    for i in range(23):
        X_t = X_r[i * 100 : (i + 1) * 100]
        y_t = y_r[i * 100 : (i + 1) * 100]

        # Train the model
        start_time = time.perf_counter()

        tracemalloc.start()

        sdt.partial_fit(X_t, y_t, classes=[0, 1, 2])

        v_m, v_max = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        end_time = time.perf_counter()
        train_time_l.append(end_time - start_time)

        # Check size
        size = clf_size(sdt, "../results/sdt/temp.pickle")
        size_l.append(size)

        # Check node counts
        n_node = node_count(sdt, forest=False)
        n_node_l.append(n_node)

        # Test the model
        start_time = time.perf_counter()

        tracemalloc.start()

        sdt_l.append(prediction(sdt, X_test, y_test))

        v_m_temp, v_max_temp = tracemalloc.get_traced_memory()
        v_m = (v_m, v_m_temp)
        v_max = (v_max, v_max_temp)
        tracemalloc.stop()

        end_time = time.perf_counter()
        test_time_l.append(end_time - start_time)

        # Check memory
        v_max_l.append(v_max)
        v_m_l.append(v_m)

    # Reformat the train times
    for i in range(1, 23):
        train_time_l[i] += train_time_l[i - 1]

    return sdt_l, train_time_l, test_time_l, v_m_l, v_max_l, n_node_l, size_l


def experiment_sdf():
    """Runs experiments for Stream Decision Forest"""
    sdf_l = []
    train_time_l = []
    test_time_l = []
    v_m_l = []
    v_max_l = []
    n_node_l = []
    size_l = []

    sdf = StreamDecisionForest(n_estimators=10)

    for i in range(23):
        X_t = X_r[i * 100 : (i + 1) * 100]
        y_t = y_r[i * 100 : (i + 1) * 100]

        # Train the model
        start_time = time.perf_counter()

        tracemalloc.start()

        sdf.partial_fit(X_t, y_t, classes=[0, 1, 2])

        v_m, v_max = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        end_time = time.perf_counter()
        train_time_l.append(end_time - start_time)

        # Check size
        size = clf_size(sdf, "../results/sdf/temp.pickle")
        size_l.append(size)

        # Check node counts
        n_node = node_count(sdf, forest=True)
        n_node_l.append(n_node)

        # Test the model
        start_time = time.perf_counter()

        tracemalloc.start()

        sdf_l.append(prediction(sdf, X_test, y_test))

        v_m_temp, v_max_temp = tracemalloc.get_traced_memory()
        v_m = (v_m, v_m_temp)
        v_max = (v_max, v_max_temp)
        tracemalloc.stop()

        end_time = time.perf_counter()
        test_time_l.append(end_time - start_time)

        # Check memory
        v_max_l.append(v_max)
        v_m_l.append(v_m)

    # Reformat the train times
    for i in range(1, 23):
        train_time_l[i] += train_time_l[i - 1]

    return sdf_l, train_time_l, test_time_l, v_m_l, v_max_l, n_node_l, size_l


# Prepare splice DNA data
dataset = openml.datasets.get_dataset(46)
X, y, is_categorical, _ = dataset.get_data(
    dataset_format="array", target=dataset.default_target_attribute
)
X_train, X_test, y_train, y_test = train_test_split(X, y)

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
args = parser.parse_args()

# Perform experiments
if args.all or args.dt:
    dt_acc_l = []
    dt_train_t_l = []
    dt_test_t_l = []
    dt_v_m_l = []
    dt_v_max_l = []
    dt_n_node_l = []
    dt_size_l = []
    for i in range(1):
        p = permutation(X_train.shape[0])

        X_r = X_train[p]
        y_r = y_train[p]

        (
            dt_acc,
            dt_train_t,
            dt_test_t,
            dt_v_m,
            dt_v_max,
            dt_n_node,
            dt_size,
        ) = experiment_dt()
        dt_acc_l.append(dt_acc)
        dt_train_t_l.append(dt_train_t)
        dt_test_t_l.append(dt_test_t)
        dt_v_m_l.append(dt_v_m)
        dt_v_max_l.append(dt_v_max)
        dt_n_node_l.append(dt_n_node)
        dt_size_l.append(dt_size)

        write_result("../results/dt/splice_acc", dt_acc_l)
        write_result("../results/dt/splice_train_t", dt_train_t_l)
        write_result("../results/dt/splice_test_t", dt_test_t_l)
        write_result("../results/dt/splice_v_m", dt_v_m_l, True)
        write_result("../results/dt/splice_v_max", dt_v_max_l, True)
        write_result("../results/dt/splice_n_node", dt_n_node_l)
        write_result("../results/dt/splice_size", dt_size_l, True)

if args.all or args.rf:
    rf_acc_l = []
    rf_train_t_l = []
    rf_test_t_l = []
    rf_v_m_l = []
    rf_v_max_l = []
    rf_n_node_l = []
    rf_size_l = []
    for i in range(1):
        p = permutation(X_train.shape[0])

        X_r = X_train[p]
        y_r = y_train[p]

        (
            rf_acc,
            rf_train_t,
            rf_test_t,
            rf_v_m,
            rf_v_max,
            rf_n_node,
            rf_size,
        ) = experiment_rf()
        rf_acc_l.append(rf_acc)
        rf_train_t_l.append(rf_train_t)
        rf_test_t_l.append(rf_test_t)
        rf_v_m_l.append(rf_v_m)
        rf_v_max_l.append(rf_v_max)
        rf_n_node_l.append(rf_n_node)
        rf_size_l.append(rf_size)

        write_result("../results/rf/splice_acc", rf_acc_l)
        write_result("../results/rf/splice_train_t", rf_train_t_l)
        write_result("../results/rf/splice_test_t", rf_test_t_l)
        write_result("../results/rf/splice_v_m", rf_v_m_l, True)
        write_result("../results/rf/splice_v_max", rf_v_max_l, True)
        write_result("../results/rf/splice_n_node", rf_n_node_l)
        write_result("../results/rf/splice_size", rf_size_l, True)

if args.all or args.ht:
    ht_acc_l = []
    ht_train_t_l = []
    ht_test_t_l = []
    ht_v_m_l = []
    ht_v_max_l = []
    ht_n_node_l = []
    ht_size_l = []
    for i in range(1):
        p = permutation(X_train.shape[0])

        X_r = X_train[p]
        y_r = y_train[p]

        (
            ht_acc,
            ht_train_t,
            ht_test_t,
            ht_v_m,
            ht_v_max,
            ht_n_node,
            ht_size,
        ) = experiment_ht()
        ht_acc_l.append(ht_acc)
        ht_train_t_l.append(ht_train_t)
        ht_test_t_l.append(ht_test_t)
        ht_v_m_l.append(ht_v_m)
        ht_v_max_l.append(ht_v_max)
        ht_n_node_l.append(ht_n_node)
        ht_size_l.append(ht_size)

        write_result("../results/ht/splice_acc", ht_acc_l)
        write_result("../results/ht/splice_train_t", ht_train_t_l)
        write_result("../results/ht/splice_test_t", ht_test_t_l)
        write_result("../results/ht/splice_v_m", ht_v_m_l, True)
        write_result("../results/ht/splice_v_max", ht_v_max_l, True)
        write_result("../results/ht/splice_n_node", ht_n_node_l)
        write_result("../results/ht/splice_size", ht_size_l, True)

if args.all or args.mf:
    mf_acc_l = []
    mf_train_t_l = []
    mf_test_t_l = []
    mf_v_m_l = []
    mf_v_max_l = []
    mf_n_node_l = []
    mf_size_l = []
    for i in range(1):
        p = permutation(X_train.shape[0])

        X_r = X_train[p]
        y_r = y_train[p]

        (
            mf_acc,
            mf_train_t,
            mf_test_t,
            mf_v_m,
            mf_v_max,
            mf_n_node,
            mf_size,
        ) = experiment_mf()
        mf_acc_l.append(mf_acc)
        mf_train_t_l.append(mf_train_t)
        mf_test_t_l.append(mf_test_t)
        mf_v_m_l.append(mf_v_m)
        mf_v_max_l.append(mf_v_max)
        mf_n_node_l.append(mf_n_node)
        mf_size_l.append(mf_size)

        write_result("../results/mf/splice_acc", mf_acc_l)
        write_result("../results/mf/splice_train_t", mf_train_t_l)
        write_result("../results/mf/splice_test_t", mf_test_t_l)
        write_result("../results/mf/splice_v_m", mf_v_m_l, True)
        write_result("../results/mf/splice_v_max", mf_v_max_l, True)
        write_result("../results/mf/splice_n_node", mf_n_node_l)
        write_result("../results/mf/splice_size", mf_size_l, True)

if args.all or args.sdt:
    sdt_acc_l = []
    sdt_train_t_l = []
    sdt_test_t_l = []
    sdt_v_m_l = []
    sdt_v_max_l = []
    sdt_n_node_l = []
    sdt_size_l = []
    for i in range(1):
        p = permutation(X_train.shape[0])

        X_r = X_train[p]
        y_r = y_train[p]

        (
            sdt_acc,
            sdt_train_t,
            sdt_test_t,
            sdt_v_m,
            sdt_v_max,
            sdt_n_node,
            sdt_size,
        ) = experiment_sdt()
        sdt_acc_l.append(sdt_acc)
        sdt_train_t_l.append(sdt_train_t)
        sdt_test_t_l.append(sdt_test_t)
        sdt_v_m_l.append(sdt_v_m)
        sdt_v_max_l.append(sdt_v_max)
        sdt_n_node_l.append(sdt_n_node)
        sdt_size_l.append(sdt_size)

        write_result("../results/sdt/splice_acc", sdt_acc_l)
        write_result("../results/sdt/splice_train_t", sdt_train_t_l)
        write_result("../results/sdt/splice_test_t", sdt_test_t_l)
        write_result("../results/sdt/splice_v_m", sdt_v_m_l, True)
        write_result("../results/sdt/splice_v_max", sdt_v_max_l, True)
        write_result("../results/sdt/splice_n_node", sdt_n_node_l)
        write_result("../results/sdt/splice_size", sdt_size_l, True)

if args.all or args.sdf:
    sdf_acc_l = []
    sdf_train_t_l = []
    sdf_test_t_l = []
    sdf_v_m_l = []
    sdf_v_max_l = []
    sdf_n_node_l = []
    sdf_size_l = []
    for i in range(1):
        p = permutation(X_train.shape[0])

        X_r = X_train[p]
        y_r = y_train[p]

        (
            sdf_acc,
            sdf_train_t,
            sdf_test_t,
            sdf_v_m,
            sdf_v_max,
            sdf_n_node,
            sdf_size,
        ) = experiment_sdf()
        sdf_acc_l.append(sdf_acc)
        sdf_train_t_l.append(sdf_train_t)
        sdf_test_t_l.append(sdf_test_t)
        sdf_v_m_l.append(sdf_v_m)
        sdf_v_max_l.append(sdf_v_max)
        sdf_n_node_l.append(sdf_n_node)
        sdf_size_l.append(sdf_size)

        write_result("../results/sdf/splice_acc", sdf_acc_l)
        write_result("../results/sdf/splice_train_t", sdf_train_t_l)
        write_result("../results/sdf/splice_test_t", sdf_test_t_l)
        write_result("../results/sdf/splice_v_m", sdf_v_m_l, True)
        write_result("../results/sdf/splice_v_max", sdf_v_max_l, True)
        write_result("../results/sdf/splice_n_node", sdf_n_node_l)
        write_result("../results/sdf/splice_size", sdf_size_l, True)
