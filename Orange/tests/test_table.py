import os
import unittest
from itertools import chain
from math import isnan
import random

from Orange import data
from Orange.data import filter
from Orange.data import Unknown

import numpy as np
from mock import Mock, MagicMock, patch


class TableTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_indexing_class(self):
        d = data.Table("test1")
        self.assertEqual([e.get_class() for e in d], ["t", "t", "f"])
        cind = len(d.domain) - 1
        self.assertEqual([e[cind] for e in d], ["t", "t", "f"])
        self.assertEqual([e["d"] for e in d], ["t", "t", "f"])
        cvar = d.domain.class_var
        self.assertEqual([e[cvar] for e in d], ["t", "t", "f"])

    def test_indexing(self):
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d = data.Table("test2")

            # regular, discrete
            varc = d.domain["c"]
            self.assertEqual(d[0, 1], "0")
            self.assertEqual(d[0, varc], "0")
            self.assertEqual(d[0, "c"], "0")
            self.assertEqual(d[0][1], "0")
            self.assertEqual(d[0][varc], "0")
            self.assertEqual(d[0]["c"], "0")

            # regular, continuous
            varb = d.domain["b"]
            self.assertEqual(d[0, 0], 0)
            self.assertEqual(d[0, varb], 0)
            self.assertEqual(d[0, "b"], 0)
            self.assertEqual(d[0][0], 0)
            self.assertEqual(d[0][varb], 0)
            self.assertEqual(d[0]["b"], 0)

            #negative
            varb = d.domain["b"]
            self.assertEqual(d[-2, 0], 3.333)
            self.assertEqual(d[-2, varb], 3.333)
            self.assertEqual(d[-2, "b"], 3.333)
            self.assertEqual(d[-2][0], 3.333)
            self.assertEqual(d[-2][varb], 3.333)
            self.assertEqual(d[-2]["b"], 3.333)

            # meta, discrete
            vara = d.domain["a"]
            metaa = d.domain.index("a")
            self.assertEqual(d[0, metaa], "A")
            self.assertEqual(d[0, vara], "A")
            self.assertEqual(d[0, "a"], "A")
            self.assertEqual(d[0][metaa], "A")
            self.assertEqual(d[0][vara], "A")
            self.assertEqual(d[0]["a"], "A")

            # meta, string
            vare = d.domain["e"]
            metae = d.domain.index("e")
            self.assertEqual(d[0, metae], "i")
            self.assertEqual(d[0, vare], "i")
            self.assertEqual(d[0, "e"], "i")
            self.assertEqual(d[0][metae], "i")
            self.assertEqual(d[0][vare], "i")
            self.assertEqual(d[0]["e"], "i")


    def test_indexing_example(self):
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d = data.Table("test2")
            e = d[0]

            # regular, discrete
            varc = d.domain["c"]
            self.assertEqual(e[1], "0")
            self.assertEqual(e[varc], "0")
            self.assertEqual(e["c"], "0")

            # regular, continuous
            varb = d.domain["b"]
            self.assertEqual(e[0], 0)
            self.assertEqual(e[varb], 0)
            self.assertEqual(e["b"], 0)

            # meta, discrete
            vara = d.domain["a"]
            metaa = d.domain.index("a")
            self.assertEqual(e[metaa], "A")
            self.assertEqual(e[vara], "A")
            self.assertEqual(e["a"], "A")

            # meta, string
            vare = d.domain["e"]
            metae = d.domain.index("e")
            self.assertEqual(e[metae], "i")
            self.assertEqual(e[vare], "i")
            self.assertEqual(e["e"], "i")


    def test_indexing_assign_value(self):
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d = data.Table("test2")

            # meta
            vara = d.domain["a"]
            metaa = d.domain.index("a")

            self.assertEqual(d[0, "a"], "A")
            d[0, "a"] = "B"
            self.assertEqual(d[0, "a"], "B")
            d[0]["a"] = "A"
            self.assertEqual(d[0, "a"], "A")

            d[0, vara] = "B"
            self.assertEqual(d[0, "a"], "B")
            d[0][vara] = "A"
            self.assertEqual(d[0, "a"], "A")

            d[0, metaa] = "B"
            self.assertEqual(d[0, "a"], "B")
            d[0][metaa] = "A"
            self.assertEqual(d[0, "a"], "A")

            # regular
            varb = d.domain["b"]

            self.assertEqual(d[0, "b"], 0)
            d[0, "b"] = 42
            self.assertEqual(d[0, "b"], 42)
            d[0]["b"] = 0
            self.assertEqual(d[0, "b"], 0)

            d[0, varb] = 42
            self.assertEqual(d[0, "b"], 42)
            d[0][varb] = 0
            self.assertEqual(d[0, "b"], 0)

            d[0, 0] = 42
            self.assertEqual(d[0, "b"], 42)
            d[0][0] = 0
            self.assertEqual(d[0, "b"], 0)


    def test_indexing_del_example(self):
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d = data.Table("test2")
            initlen = len(d)

            # remove first
            d[4, "e"] = "4ex"
            self.assertEqual(d[4, "e"], "4ex")
            del d[0]
            self.assertEqual(len(d), initlen - 1)
            self.assertEqual(d[3, "e"], "4ex")

            # remove middle
            del d[2]
            self.assertEqual(len(d), initlen - 2)
            self.assertEqual(d[2, "e"], "4ex")

            # remove middle
            del d[4]
            self.assertEqual(len(d), initlen - 3)
            self.assertEqual(d[2, "e"], "4ex")

            # remove last
            d[-1, "e"] = "was last"
            del d[-1]
            self.assertEqual(len(d), initlen - 4)
            self.assertEqual(d[2, "e"], "4ex")
            self.assertNotEqual(d[-1, "e"], "was last")

            # remove one before last
            d[-1, "e"] = "was last"
            del d[-2]
            self.assertEqual(len(d), initlen - 5)
            self.assertEqual(d[2, "e"], "4ex")
            self.assertEqual(d[-1, "e"], "was last")

            with self.assertRaises(ValueError):
                del d[100]
            self.assertEqual(len(d), initlen - 5)

            with self.assertRaises(ValueError):
                del d[-100]
            self.assertEqual(len(d), initlen - 5)

    @unittest.skip("Are discrete attributes represented as pzthon strings of floats?")
    def test_indexing_assign_example(self):
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d = data.Table("test2")

            vara = d.domain["a"]
            metaa = d.domain.index(vara)

            self.assertFalse(isnan(d[0, "a"]))
            d[0] = ["3.14", "1", "f"]
            self.assertEqual(list(d[0]), [3.14, "1", "f"])
            self.assertTrue(isnan(d[0, "a"]))
            d[0] = [3.15, 1, "t"]
            self.assertEqual(list(d[0]), [3.15, "0", "t"])

            with self.assertRaises(ValueError):
                d[0] = ["3.14", "1"]

            ex = data.Instance(d.domain, ["3.16", "1", "f"])
            d[0] = ex
            self.assertEqual(list(d[0]), [3.16, "1", "f"])

            ex = data.Instance(d.domain, ["3.16", "1", "f"])
            ex["e"] = "mmmapp"
            d[0] = ex
            self.assertEqual(list(d[0]), [3.16, "1", "f"])
            self.assertEqual(d[0, "e"], "mmmapp")

    def test_slice(self):
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d = data.Table("test2")
            x = d[:3]
            self.assertEqual(len(x), 3)
            self.assertEqual([e[0] for e in x], [0, 1.1, 2.22])

            x = d[2:5]
            self.assertEqual(len(x), 3)
            self.assertEqual([e[0] for e in x], [2.22, 2.23, 2.24])

            x = d[4:1:-1]
            self.assertEqual(len(x), 3)
            self.assertEqual([e[0] for e in x], [2.24, 2.23, 2.22])

            x = d[-3:]
            self.assertEqual(len(x), 3)
            self.assertEqual([e[0] for e in x], [2.26, 3.333, Unknown])


    def test_assign_slice_value(self):
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d = data.Table("test2")
            d[2:5, 0] = 42
            self.assertEqual([e[0] for e in d], [0, 1.1, 42, 42, 42, 2.25, 2.26, 3.333, Unknown])
            d[:3, "b"] = 43
            self.assertEqual([e[0] for e in d], [43, 43, 43, 42, 42, 2.25, 2.26, 3.333, None])
            d[-2:, d.domain[0]] = 44
            self.assertEqual([e[0] for e in d], [43, 43, 43, 42, 42, 2.25, 2.26, 44, 44])

            d[2:5, "a"] = "A"
            self.assertEqual([e["a"] for e in d], list("ABAAACCDE"))


    def test_del_slice_example(self):
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d = data.Table("test2")

            vals = [e[0] for e in d]

            del d[2:2]
            self.assertEqual([e[0] for e in d], vals)

            del d[2:5]
            del vals[2:5]
            self.assertEqual([e[0] for e in d], vals)

            del d[:]
            self.assertEqual(len(d), 0)


    def test_set_slice_example(self):
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d = data.Table("test2")
            d[5, 0] = 42
            d[:3] = d[5]
            self.assertEqual(d[1, 0], 42)

            d[5:2:-1] = [3, None, None]
            self.assertEqual([e[0] for e in d], [42, 42, 42, 3, 3, 3, 2.26, 3.333, None])
            self.assertTrue(isnan(d[3, 2]))

            with self.assertRaises(TypeError):
                d[2:5] = 42

    def test_multiple_indices(self):
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d = data.Table("test2")

            with self.assertRaises(IndexError):
                x = d[2, 5, 1]

            with self.assertRaises(IndexError):
                x = d[(2, 5, 1)]

            x = d[[2, 5, 1]]
            self.assertEqual([e[0] for e in x], [2.22, 2.25, 1.1])
            # TODO reenable tests with metas when they are implemented
            #            self.assertEqual([e["a"] for e in x], ["C", "C", "B"])

            # Indexing by generators is not longer available after moving to numpy and
            # removing row_indices
            #            x = d[(x for x in range(5, 2, -1))]
            #            self.assertEqual([e[0] for e in x], [2.25, 2.24, 2.23])


    def test_assign_multiple_indices_value(self):
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d = data.Table("test2")

            d[1:4, "b"] = 42
            self.assertEqual([e[0] for e in d], [0, 42, 42, 42, 2.24, 2.25, 2.26, 3.333, None])

            d[range(5, 2, -1), "b"] = None
            self.assertEqual([e[d.domain[0]] for e in d], [0, 42, 42, None, "?", "", 2.26, 3.333, None])


    def test_del_multiple_indices_example(self):
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d = data.Table("test2")

            vals = [e[0] for e in d]

            del d[[1, 5, 2]]
            del vals[5]
            del vals[2]
            del vals[1]
            self.assertEqual([e[0] for e in d], vals)

            del d[range(1, 3)]
            del vals[1:3]
            self.assertEqual([e[0] for e in d], vals)


    def test_set_multiple_indices_example(self):
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d = data.Table("test2")

            vals = [e[0] for e in d]
            d[[1, 2, 5]] = [42, None, None]
            vals[1] = vals[2] = vals[5] = 42
            self.assertEqual([e[0] for e in d], vals)


    def test_views(self):
        d = data.Table("zoo")
        crc = d.checksum(True)
        x = d[:20]
        self.assertEqual(crc, d.checksum(True))
        del x[13]
        self.assertEqual(crc, d.checksum(True))
        del x[4:9]
        self.assertEqual(crc, d.checksum(True))
        x[2, "name"] = "leocorn"
        self.assertEqual(d[2, "name"], "leocorn")
        x[2, 1] = 0
        self.assertEqual(d[2, 1], 0)
        x[2, 1] = 1
        self.assertEqual(d[2, 1], 1)
        x[2][1] = 0
        self.assertEqual(d[2, 1], 0)

        d[2][1] = 1
        self.assertEqual(x[2, 1], 1)
        d[2, 1] = 0
        self.assertEqual(x[2, 1], 0)

        x[2, "name"] = "dinosaur"
        self.assertEqual(d[2, "name"], "dinosaur")
        x[2]["name"] = "yeti"
        self.assertEqual(d[2, "name"], "yeti")

        d[2, "name"] = "dinosaur"
        self.assertEqual(x[2, "name"], "dinosaur")
        d[2]["name"] = "yeti"
        self.assertEqual(x[2, "name"], "yeti")


    def test_bool(self):
        d = data.Table("iris")
        self.assertTrue(d)
        del d[:]
        self.assertFalse(d)

        d = data.Table("test3")
        self.assertFalse(d)

        d = data.Table("iris")
        self.assertTrue(d)
        d.clear()
        self.assertFalse(d)


    def test_checksum(self):
        d = data.Table("zoo")
        d[42, 3] = 0
        crc1 = d.checksum(False)
        d[42, 3] = 1
        crc2 = d.checksum(False)
        self.assertNotEqual(crc1, crc2)
        d[42, 3] = 0
        crc3 = d.checksum(False)
        self.assertEqual(crc1, crc3)
        _ = d[42, "name"]
        d[42, "name"] = "non-animal"
        crc4 = d.checksum(False)
        self.assertEqual(crc1, crc4)
        crc4 = d.checksum(True)
        crc5 = d.checksum(1)
        crc6 = d.checksum(False)
        self.assertNotEqual(crc1, crc4)
        self.assertNotEqual(crc1, crc5)
        self.assertEqual(crc1, crc6)

    def test_random(self):
        d = data.Table("zoo")
        self.assertTrue(isinstance(d.random_example(), data.Instance))
        d.clear()
        self.assertRaises(IndexError, d.random_example)

    def test_total_weight(self):
        d = data.Table("zoo")
        self.assertEqual(d.total_weight(), len(d))

        d.set_weights(0)
        d[0].set_weight(0.1)
        d[10].set_weight(0.2)
        d[-1].set_weight(0.3)
        self.assertAlmostEqual(d.total_weight(), 0.6)
        del d[10]
        self.assertAlmostEqual(d.total_weight(), 0.4)
        d.clear()
        self.assertAlmostEqual(d.total_weight(), 0)


    def test_has_missing(self):
        d = data.Table("zoo")
        self.assertFalse(d.has_missing())
        self.assertFalse(d.has_missing_class())

        d[10, 3] = "?"
        self.assertTrue(d.has_missing())
        self.assertFalse(d.has_missing_class())

        d[10].set_class("?")
        self.assertTrue(d.has_missing())
        self.assertTrue(d.has_missing_class())

        d = data.Table("test3")
        self.assertFalse(d.has_missing())
        self.assertFalse(d.has_missing_class())

    def test_shuffle(self):
        d = data.Table("zoo")
        crc = d.checksum()
        names = set(str(x["name"]) for x in d)

        d.shuffle()
        self.assertNotEqual(crc, d.checksum())
        self.assertSetEqual(names, set(str(x["name"]) for x in d))
        crc2 = d.checksum()

        x = d[2:10]
        crcx = x.checksum()
        d.shuffle()
        self.assertNotEqual(crc2, d.checksum())
        self.assertEqual(crcx, x.checksum())

        crc2 = d.checksum()
        x.shuffle()
        self.assertNotEqual(crcx, x.checksum())
        self.assertEqual(crc2, d.checksum())

    @staticmethod
    def not_less_ex(ex1, ex2):
        for v1, v2 in zip(ex1, ex2):
            if v1 != v2:
                return v1 < v2
        return True

    @staticmethod
    def sorted(d):
        for i in range(1, len(d)):
            if not TableTestCase.not_less_ex(d[i - 1], d[i]):
                return False
        return True

    @staticmethod
    def not_less_ex_ord(ex1, ex2, ord):
        for a in ord:
            if ex1[a] != ex2[a]:
                return ex1[a] < ex2[a]
        return True

    @staticmethod
    def sorted_ord(d, ord):
        for i in range(1, len(d)):
            if not TableTestCase.not_less_ex_ord(d[i - 1], d[i], ord):
                return False
        return True

    def test_sort(self):
        d = data.Table("iris")
        d.sort()
        self.assertTrue(TableTestCase.sorted(d))

        for order in ([1], [], [4, 1, 2]):
            d.sort(order)
            self.assertTrue(TableTestCase.sorted_ord(d, order))

        e = d[0]
        self.assertRaises(RuntimeError, d.shuffle)
        self.assertRaises(RuntimeError, d.sort)
        del e

        d.shuffle()
        order = [4, 1, 2]
        crc = d.checksum()
        x = d[:]
        x.sort()
        self.assertEqual(crc, d.checksum())
        self.assertTrue(TableTestCase.sorted(x))

        x.sort(order)
        self.assertEqual(crc, d.checksum())
        self.assertTrue(TableTestCase.sorted_ord(x, order))

    def test_remove_duplicates(self):
        d = data.Table("zoo")
        d.remove_duplicates()
        d.sort()
        for i in range(1, len(d)):
            self.assertNotEqual(d[i - 1].native(), d[i].native())

    def test_append(self):
        d = data.Table("test3")
        d.append([None] * 3)
        self.assertEqual(1, len(d))
        self.assertTrue(all(isnan(i) for i in d[0]))

        d.append([42, "0", None])
        self.assertEqual(2, len(d))
        self.assertEqual(d[1], [42, "0", None])

    def test_append2(self):
        d = data.Table("iris")
        d.shuffle()
        l1 = len(d)
        d.append([1, 2, 3, 4, 0])
        self.assertEqual(len(d), l1 + 1)
        self.assertEqual(d[-1], [1, 2, 3, 4, 0])

        x = data.Instance(d[10])
        d.append(x)
        self.assertEqual(d[-1], d[10])

        x = d[:50]
        with self.assertRaises(ValueError):
            x.append(d[50])

        x.ensure_copy()
        x.append(d[50])
        self.assertEqual(x[50], d[50])


    def test_extend(self):
        d = data.Table("iris")
        d.shuffle()

        x = d[:5]
        x.ensure_copy()
        d.extend(x)
        for i in range(5):
            self.assertTrue(d[i] == d[-5 + i])

        x = d[:5]
        with self.assertRaises(ValueError):
            d.extend(x)

    def test_convert_through_append(self):
        d = data.Table("iris")
        dom2 = data.Domain([d.domain[0], d.domain[2], d.domain[4]])
        d2 = data.Table(dom2)
        dom3 = data.Domain([d.domain[1], d.domain[2]], None)
        d3 = data.Table(dom3)
        for e in d[:5]:
            d2.append(e)
            d3.append(e)
        for e, e2, e3 in zip(d, d2, d3):
            self.assertEqual(e[0], e2[0])
            self.assertEqual(e[1], e3[0])

    def test_pickle(self):
        import pickle

        d = data.Table("zoo")
        s = pickle.dumps(d)
        d2 = pickle.loads(s)
        self.assertEqual(d[0], d2[0])
        self.assertEqual(d.checksum(), d2.checksum())

        d = data.Table("iris")
        s = pickle.dumps(d)
        d2 = pickle.loads(s)
        self.assertEqual(d[0], d2[0])
        self.assertEqual(d.checksum(), d2.checksum())

    def test_pickle_ref(self):
        import pickle

        d = data.Table("zoo")
        dr = d[:10]
        self.assertEqual(dr.base, d)

        s = pickle.dumps(dr)
        d2 = pickle.loads(s)
        self.assertEqual(d[0], d2[0])
        self.assertEqual(dr.checksum(), d2.checksum())


    def test_sample(self):
        d = data.Table("iris")

        li = [1] * 10 + [0] * 140
        d1 = d.sample(li)
        self.assertEqual(len(d1), 10)
        for i in range(10):
            self.assertEqual(d1[i], d[i])
            self.assertEqual(d1[i].id, d[i].id)
        d[0, 0] = 42
        self.assertEqual(d1[0, 0], 42)

        d1 = d.sample(li, copy=True)
        self.assertEqual(len(d1), 10)
        self.assertEqual(d1[0], d[0])
        self.assertNotEqual(d1[0].id, d[0].id)
        d[0, 0] = 41
        self.assertEqual(d1[0, 0], 42)

        li = [1, 2, 3, 4, 5] * 30
        d1 = d.sample(li, 2)
        self.assertEqual(len(d1), 30)
        for i in range(30):
            self.assertEqual(d1[i].id, d[1 + 5 * i].id)

        ri = orange.MakeRandomIndicesCV(d)
        for fold in range(10):
            d1 = d.sample(ri, fold)
            self.assertEqual(orange.get_class_distribution(d1), [5, 5, 5])

    def test_translate_through_slice(self):
        d = data.Table("iris")
        dom = data.Domain(["petal length", "sepal length", "iris"], source=d.domain)
        print(d.domain)
        d_ref = d[:10, dom]
        self.assertEqual(d_ref.domain.class_var, d.domain.class_var)
        self.assertEqual(d_ref[0, "petal length"], d[0, "petal length"])
        self.assertEqual(d_ref[0, "sepal length"], d[0, "sepal length"])
        self.assertEqual(d_ref.X.shape, (10, 2))
        self.assertEqual(d_ref.Y.shape, (10, 1))


    def test_indexing_filter_cont(self):
        d = data.Table("iris")
        v = d.columns
        d2 = d[v.sepal_length < 5]
        self.assertEqual(len(d2), 22)
        d2[0, 0] = 42
        d3 = [e for e in d if e[0] == 42]
        self.assertEqual(len(d3), 1)
        self.assertEqual(d3[0], d2[0])

        d = data.Table("iris")
        v = d.columns
        self.assertEqual(len(d[v.sepal_length <= 5]), 32)
        self.assertEqual(len(d[v.sepal_length > 5]), 118)
        self.assertEqual(len(d[v.sepal_length >= 5]), 128)
        self.assertEqual(len(d[v.sepal_length == 5]), 10)

        self.assertEqual(len(d[(v.sepal_length == 5) & (v.sepal_width < 3.3)]), 4)
        self.assertEqual(len(d[(v.sepal_length < 4.5) | (v.sepal_width == 3.0)]), 28)

        self.assertEqual(len(d[v.sepal_width == (3.0, 3.3)]), 57)
        self.assertEqual(len(d[v.sepal_width != (3.0, 3.3)]), 93)
        self.assertEqual(len(d[v.sepal_length < (5.0, 5.3)]), 22)
        self.assertEqual(len(d[v.sepal_length <= (5.0, 5.3)]), 32)
        self.assertEqual(len(d[v.sepal_length > (4.7, 5.0)]), 118)
        self.assertEqual(len(d[v.sepal_length >= (4.7, 5.0)]), 128)

    def test_indexing_filter_disc(self):
        d = data.Table("iris")
        v = d.columns
        self.assertEqual(len(d[v.iris == "Iris-setosa"]), 50)
        self.assertEqual(len(d[v.iris == ["Iris-setosa", "Iris-versicolor"]]), 100)
        self.assertEqual(len(d[v.iris != "Iris-setosa"]), 100)
        self.assertEqual(len(d[v.iris != ["Iris-setosa", "Iris-versicolor"]]), 50)
        with self.assertRaises(TypeError):
            d[v.iris < "Iris-setosa"]

    def test_indexing_filter_string(self):
        d = data.Table("zoo")
        name = d.domain["name"]
        self.assertEqual(len(d[name == "girl"]), 1)
        self.assertEqual(len(d[name != "girl"]), 100)
        self.assertEqual(len(d[name == ["girl", "gull", "mole"]]), 3)
        self.assertEqual(len(d[name != ["girl", "gull", "mole"]]), 98)

        self.assertEqual(len(d[name < "calf"]), 6)
        self.assertEqual(len(d[name <= "calf"]), 7)
        self.assertEqual(len(d[name > "calf"]), 94)
        self.assertEqual(len(d[name >= "calf"]), 95)

        with self.assertRaises(TypeError):
            d[name < ["calf", "girl"]]

    def test_indexing_filter_assign(self):
        d = data.Table("iris")
        v = d.columns
        d[v.iris == "Iris-setosa", v.petal_length] = 42
        for e in d:
            if e[-1] == "Iris-setosa":
                self.assertEqual(e["petal length"], 42)
            else:
                self.assertNotEqual(e["petal length"], 42)

        """
        # This does not work yet for ass_subscript in general, not only for filters

        d = data.Table("iris")
        v = d.columns
        d[v.iris == "Iris-setosa", (v.petal_length, v.sepal_length)] = 42
        for e in d:
            if e[-1] == "Iris-setosa":
                self.assertEqual(e["petal length"], 42)
                self.assertEqual(e["sepal length"], 42)
            else:
                self.assertNotEqual(e["petal length"], 42)
                self.assertNotEqual(e["sepal length"], 42)
            self.assertNotEqual(e["petal width"], 42)
            self.assertNotEqual(e["sepal width"], 42)
         """

        d = data.Table("iris")
        v = d.columns
        del d[v.sepal_length <= 5]
        self.assertEqual(len(d), 118)
        for e in d:
            self.assertGreater(e["sepal length"], 5)


    def test_saveTab(self):
        d = data.Table("iris")[:3]
        d.save("test-save.tab")
        try:
            d2 = data.Table("test-save.tab")
            for e1, e2 in zip(d, d2):
                self.assertEqual(e1, e2)
        finally:
            os.remove("test-save.tab")

        dom = data.Domain([data.ContinuousVariable("a")])
        d = data.Table(dom)
        d += [[i] for i in range(3)]
        d.save("test-save.tab")
        try:
            d2 = data.Table("test-save.tab")
            self.assertEqual(len(d.domain.attributes), 0)
            self.assertEqual(d.domain.classVar, dom[0])
            for i in range(3):
                self.assertEqual(d2[i], [i])
        finally:
            os.remove("test-save.tab")

        dom = data.Domain([data.ContinuousVariable("a")], None)
        d = data.Table(dom)
        d += [[i] for i in range(3)]
        d.save("test-save.tab")
        try:
            d2 = data.Table("test-save.tab")
            self.assertEqual(len(d.domain.attributes), 1)
            self.assertEqual(d.domain[0], dom[0])
            for i in range(3):
                self.assertEqual(d2[i], [i])
        finally:
            os.remove("test-save.tab")


    def test_from_numpy(self):
        import random

        a = np.arange(20, dtype="d").reshape((4, 5))
        a[:, -1] = [0, 0, 0, 1]
        dom = data.Domain([data.ContinuousVariable(x) for x in "abcd"],
                          data.DiscreteVariable("e", values=["no", "yes"]))
        table = data.Table(dom, a)
        for i in range(4):
            self.assertEqual(table[i].get_class(), "no" if i < 3 else "yes")
            for j in range(5):
                self.assertEqual(a[i, j], table[i, j])
                table[i, j] = random.random()
                self.assertEqual(a[i, j], table[i, j])

        with self.assertRaises(IndexError):
            table[0, -5] = 5

    @unittest.skip("Probably obsolete")
    def test_anonymous_from_numpy(self):
        a = numpy.zeros((4, 5))
        a[0, 0] = 0.5
        a[3, 1] = 11
        a[3, 2] = -1
        a[1, 3] = 5
        knn = orange.kNNLearner(a)
        data = knn.find_nearest.examples
        domain = data.domain
        self.assertEqual([var.name for var in domain.variables],
                         ["var%05i" % i for i in range(5)])
        self.assertEqual(domain[0].var_type, orange.VarTypes.Continuous)
        self.assertEqual(domain[1].var_type, orange.VarTypes.Continuous)
        self.assertEqual(domain[2].var_type, orange.VarTypes.Continuous)
        self.assertEqual(domain[3].var_type, orange.VarTypes.Discrete)
        self.assertEqual(domain[3].values, ["v%i" % i for i in range(6)])
        self.assertEqual(domain[4].var_type, orange.VarTypes.Discrete)
        self.assertEqual(domain[4].values, ["v0"])

        dom2 = data.Domain([data.ContinuousVariable("a"),
                            data.ContinuousVariable("b"),
                            data.ContinuousVariable("c"),
                            data.DiscreteVariable("d", values="abcdef"),
                            data.DiscreteVariable("e", values="ab")])
        ex = data.Instance(dom2, [3.14, 42, 2.7, "d", "a"])
        knn(ex)
        ex1 = domain(ex)
        self.assertEqual(list(map(float, ex1)), list(map(float, ex)))
        ex2 = dom2(ex1)
        self.assertEqual(list(map(float, ex1)), list(map(float, ex2)))
        self.assertEqual(ex1, ex2)
        self.assertEqual(ex1, ex)

        iris = data.Table("iris")
        with self.assertRaises(ValueError):
            domain(iris[0])

        knn.find_nearest.examples = numpy.zeros((3, 3))
        domain = knn.find_nearest.examples.domain
        for i in range(3):
            var = domain[i]
            self.assertEqual(var.name, "var%05i" % i)
            self.assertEqual(var.values, ["v0"])


    def test_filter_is_defined(self):
        d = data.Table("iris")
        d[1, 4] = Unknown
        self.assertTrue(isnan(d[1, 4]))
        d[140, 0] = Unknown
        e = d.filter_is_defined()
        self.assertEqual(len(e), len(d) - 2)
        self.assertEqual(e[0], d[0])
        self.assertEqual(e[1], d[2])
        self.assertEqual(e[147], d[149])
        self.assertTrue(d.has_missing())
        self.assertFalse(e.has_missing())

    def test_filter_has_class(self):
        d = data.Table("iris")
        d[1, 4] = Unknown
        self.assertTrue(isnan(d[1, 4]))
        d[140, 0] = Unknown
        e = d.filter_has_class()
        self.assertEqual(len(e), len(d) - 1)
        self.assertEqual(e[0], d[0])
        self.assertEqual(e[1], d[2])
        self.assertEqual(e[148], d[149])
        self.assertTrue(d.has_missing())
        self.assertTrue(e.has_missing())
        self.assertFalse(e.has_missing_class())

    def test_filter_random(self):
        d = data.Table("iris")
        e = d.filter_random(50)
        self.assertEqual(len(e), 50)
        e = d.filter_random(50, negate=True)
        self.assertEqual(len(e), 100)
        for i in range(5):
            e = d.filter_random(0.2)
            self.assertEqual(len(e), 30)
            bc = np.bincount(np.array(e.Y[:, 0], dtype=int))
            if min(bc) > 7:
                break
        else:
            self.fail("Filter returns too uneven distributions")

    def test_filter_same_value(self):
        d = data.Table("zoo")
        mind = d.domain["type"].to_val("mammal")
        lind = d.domain["legs"].to_val("4")
        gind = d.domain["name"].to_val("girl")
        for pos, val, r in (("type", "mammal", mind),
                            (len(d.domain.attributes), mind, mind),
                            ("legs", lind, lind),
                            ("name", "girl", gind)):
            e = d.filter_same_value(pos, val)
            f = d.filter_same_value(pos, val, negate=True)
            self.assertEqual(len(e) + len(f), len(d))
            self.assertTrue(all(ex[pos] == r for ex in e))
            self.assertTrue(all(ex[pos] != r for ex in f))

    def test_filter_value_continuous(self):
        d = data.Table("iris")
        col = d.X[:, 2]

        v = d.columns
        f = filter.FilterContinuous(v.petal_length,
                                    filter.ValueFilter.Operator.Between, min=4.5, max=5.1)

        x = d.filter_values(f)
        self.assertTrue(np.all(4.5 <= x.X[:, 2]))
        self.assertTrue(np.all(x.X[:, 2] <= 5.1))
        self.assertEqual(sum((col >= 4.5 ) * (col <= 5.1)), len(x))

        f.ref = 5.1
        f.oper = filter.ValueFilter.Operator.Equal
        x = d.filter_values(f)
        self.assertTrue(np.all(x.X[:, 2] == 5.1))
        self.assertEqual(sum(col == 5.1), len(x))

        f.oper = filter.ValueFilter.Operator.NotEqual
        x = d.filter_values(f)
        self.assertTrue(np.all(x.X[:, 2] != 5.1))
        self.assertEqual(sum(col != 5.1), len(x))

        f.oper = filter.ValueFilter.Operator.Less
        x = d.filter_values(f)
        self.assertTrue(np.all(x.X[:, 2] < 5.1))
        self.assertEqual(sum(col < 5.1), len(x))

        f.oper = filter.ValueFilter.Operator.LessEqual
        x = d.filter_values(f)
        self.assertTrue(np.all(x.X[:, 2] <= 5.1))
        self.assertEqual(sum(col <= 5.1), len(x))

        f.oper = filter.ValueFilter.Operator.Greater
        x = d.filter_values(f)
        self.assertTrue(np.all(x.X[:, 2] > 5.1))
        self.assertEqual(sum(col > 5.1), len(x))

        f.oper = filter.ValueFilter.Operator.GreaterEqual
        x = d.filter_values(f)
        self.assertTrue(np.all(x.X[:, 2] >= 5.1))
        self.assertEqual(sum(col >= 5.1), len(x))

        f.oper = filter.ValueFilter.Operator.Outside
        f.min, f.max = 4.5, 5.1
        x = d.filter_values(f)
        for e in x:
            self.assertTrue(e[2] < 4.5 or e[2] > 5.1)
        self.assertEqual(sum((col < 4.5) + (col > 5.1)), len(x))


    def test_filter_value_continuous_args(self):
        d = data.Table("iris")
        col = d.X[:, 2]
        v = d.columns

        f = filter.FilterContinuous(v.petal_length,
                                    filter.ValueFilter.Operator.Equal, ref=5.1)
        x = d.filter_values(f)
        self.assertTrue(np.all(x.X[:, 2] == 5.1))
        self.assertEqual(sum(col == 5.1), len(x))

        f = filter.FilterContinuous(2,
                                    filter.ValueFilter.Operator.Equal, ref=5.1)
        self.assertTrue(np.all(x.X[:, 2] == 5.1))
        self.assertEqual(sum(col == 5.1), len(x))

        f = filter.FilterContinuous("petal length",
                                    filter.ValueFilter.Operator.Equal, ref=5.1)
        self.assertTrue(np.all(x.X[:, 2] == 5.1))
        self.assertEqual(sum(col == 5.1), len(x))

        f = filter.FilterContinuous("sepal length",
                                    filter.ValueFilter.Operator.Equal, ref=5.1)
        f.position = 2
        self.assertTrue(np.all(x.X[:, 2] == 5.1))
        self.assertEqual(sum(col == 5.1), len(x))

        f = filter.FilterContinuous("sepal length",
                                    filter.ValueFilter.Operator.Equal, ref=5.1)
        f.position = v.petal_length
        self.assertTrue(np.all(x.X[:, 2] == 5.1))
        self.assertEqual(sum(col == 5.1), len(x))

        f = filter.FilterContinuous(v.petal_length,
                                    filter.ValueFilter.Operator.Equal, ref=18)
        f.ref = 5.1
        x = d.filter_values(f)
        self.assertTrue(np.all(x.X[:, 2] == 5.1))
        self.assertEqual(sum(col == 5.1), len(x))

        f = filter.FilterContinuous(v.petal_length,
                                    filter.ValueFilter.Operator.Equal, ref=18)
        f.min = 5.1
        x = d.filter_values(f)
        self.assertTrue(np.all(x.X[:, 2] == 5.1))
        self.assertEqual(sum(col == 5.1), len(x))


    def test_valueFilter_discrete(self):
        d = data.Table("zoo")

        f = filter.FilterDiscrete(d.domain.class_var, values=[2, 3, 4])
        for e in d.filter_values(f):
            self.assertTrue(e.get_class() in [2, 3, 4])

        f.values = ["mammal"]
        for e in d.filter_values(f):
            self.assertTrue(e.get_class() == "mammal")

        f = filter.FilterDiscrete(d.domain.class_var, values=[2, "mammal"])
        for e in d.filter_values(f):
            self.assertTrue(e.get_class() in [2, "mammal"])

        f = filter.FilterDiscrete(d.domain.class_var, values=[2, "martian"])
        self.assertRaises(ValueError, d.filter_values, f)

        f = filter.FilterDiscrete(d.domain.class_var, values=[2, data.Table])
        self.assertRaises(TypeError, d.filter_values, f)


    def test_valueFilter_string_case_sens(self):
        d = data.Table("zoo")
        col = d[:, "name"].metas[:, 0]

        f = filter.FilterString("name", filter.ValueFilter.Operator.Equal, "girl")
        x = d.filter_values(f)
        self.assertEqual(len(x), 1)
        self.assertEqual(x[0, "name"], "girl")
        self.assertTrue(np.all(x.metas == "girl"))

        f.oper = f.Operator.NotEqual
        x = d.filter_values(f)
        self.assertEqual(len(x), len(d) - 1)
        self.assertTrue(np.all(x[:, "name"] != "girl"))

        f.oper = f.Operator.Less
        x = d.filter_values(f)
        self.assertEqual(len(x), sum(col < "girl"))
        self.assertTrue(np.all(x.metas < "girl"))

        f.oper = f.Operator.LessEqual
        x = d.filter_values(f)
        self.assertEqual(len(x), sum(col <= "girl"))
        self.assertTrue(np.all(x.metas <= "girl"))

        f.oper = f.Operator.Greater
        x = d.filter_values(f)
        self.assertEqual(len(x), sum(col > "girl"))
        self.assertTrue(np.all(x.metas > "girl"))

        f.oper = f.Operator.GreaterEqual
        x = d.filter_values(f)
        self.assertEqual(len(x), sum(col >= "girl"))
        self.assertTrue(np.all(x.metas >= "girl"))

        f.oper = f.Operator.Between
        f.max = "lion"
        x = d.filter_values(f)
        self.assertEqual(len(x), sum(("girl" <= col) * (col <= "lion")))
        self.assertTrue(np.all(x.metas >= "girl"))
        self.assertTrue(np.all(x.metas <= "lion"))

        f.oper = f.Operator.Outside
        x = d.filter_values(f)
        self.assertEqual(len(x), sum(col < "girl") + sum(col > "lion"))
        self.assertTrue(np.all((x.metas < "girl") + (x.metas > "lion")))

        f.oper = f.Operator.Contains
        f.ref = "ea"
        x = d.filter_values(f)
        for e in x:
            self.assertTrue("ea" in e["name"])
        self.assertEqual(len(x), len([e for e in col if "ea" in e]))

        f.oper = f.Operator.BeginsWith
        f.ref = "sea"
        x = d.filter_values(f)
        for e in x:
            self.assertTrue(str(e["name"]).startswith("sea"))
        self.assertEqual(len(x), len([e for e in col if e.startswith("sea")]))

        f.oper = f.Operator.EndsWith
        f.ref = "ion"
        x = d.filter_values(f)
        for e in x:
            self.assertTrue(str(e["name"]).endswith("ion"))
        self.assertEqual(len(x), len([e for e in col if e.endswith("ion")]))


    def test_valueFilter_string_case_insens(self):
        d = data.Table("zoo")
        d[d[:, "name"].metas[:, 0] == "girl", "name"] = "GIrl"

        col = d[:, "name"].metas[:, 0]

        f = filter.FilterString("name", filter.ValueFilter.Operator.Equal, "giRL")
        f.case_sensitive = False
        x = d.filter_values(f)
        self.assertEqual(len(x), 1)
        self.assertEqual(x[0, "name"], "GIrl")
        self.assertTrue(np.all(x.metas == "GIrl"))

        f.oper = f.Operator.NotEqual
        x = d.filter_values(f)
        self.assertEqual(len(x), len(d) - 1)
        self.assertTrue(np.all(x[:, "name"] != "GIrl"))

        f.oper = f.Operator.Less
        f.ref = "CHiCKEN"
        x = d.filter_values(f)
        print(x.metas)
        self.assertEqual(len(x), sum(col < "chicken") - 1) ## girl!
        self.assertTrue(np.all(x.metas < "chicken"))

        f.oper = f.Operator.LessEqual
        x = d.filter_values(f)
        self.assertEqual(len(x), sum(col <= "chicken") - 1)
        self.assertTrue(np.all(x.metas <= "chicken"))

        f.oper = f.Operator.Greater
        x = d.filter_values(f)
        self.assertEqual(len(x), sum(col > "chicken") + 1)
        for e in x:
            self.assertGreater(str(e["name"]).lower(), "chicken")

        f.oper = f.Operator.GreaterEqual
        x = d.filter_values(f)
        self.assertEqual(len(x), sum(col >= "chicken") + 1)
        for e in x:
            self.assertGreaterEqual(str(e["name"]).lower(), "chicken")

        f.oper = f.Operator.Between
        f.max = "liOn"
        x = d.filter_values(f)
        self.assertEqual(len(x), sum((col >= "chicken") * (col <= "lion")) + 1)
        for e in x:
            self.assertTrue("chicken" <= str(e["name"]).lower() <= "lion")

        f.oper = f.Operator.Outside
        x = d.filter_values(f)
        self.assertEqual(len(x), sum(col < "chicken") + sum(col > "lion") - 1)
        self.assertTrue(np.all((x.metas < "chicken") + (x.metas > "lion")))

        f.oper = f.Operator.Contains
        f.ref = "iR"
        x = d.filter_values(f)
        for e in x:
            self.assertTrue("ir" in str(e["name"]).lower())
        self.assertEqual(len(x), len([e for e in col if "ir" in e]) + 1)

        f.oper = f.Operator.BeginsWith
        f.ref = "GI"
        x = d.filter_values(f)
        for e in x:
            self.assertTrue(str(e["name"]).lower().startswith("gi"))
        self.assertEqual(len(x), len([e for e in col if e.lower().startswith("gi")]))

        f.oper = f.Operator.EndsWith
        f.ref = "ion"
        x = d.filter_values(f)
        for e in x:
            self.assertTrue(str(e["name"]).endswith("ion"))
        self.assertEqual(len(x), len([e for e in col if e.endswith("ion")]))


        #TODO Test conjunctions and disjunctions of conditions

def column_sizes(table):
    return len(table.domain.attributes), len(table.domain.class_vars), len(table.domain.metas)

class TableTests(unittest.TestCase):
    attributes = ["Feature %i" % i for i in range(10)]
    class_vars = ["Class %i" % i for i in range(3)]
    metas = ["Meta %i" % i for i in range(5)]
    nrows = 10
    row_indices = (1, 5, 7, 9)

    data = np.random.random((nrows, len(attributes)))
    class_data = np.random.random((nrows, len(class_vars)))
    meta_data = np.random.random((nrows, len(metas)))
    weight_data = np.random.random((nrows, ))

    def mock_domain(self, with_classes=False, with_metas=False):
        attributes = self.attributes
        class_vars = self.class_vars if with_classes else []
        metas = self.metas if with_metas else []
        variables = attributes + class_vars
        return MagicMock(data.Domain, attributes=attributes, class_vars=class_vars, metas=metas, variables=variables)

    def create_domain(self, attributes=(), classes=(), metas=()):
        attr_vars = [data.ContinuousVariable(name=a) if isinstance(a, str) else a for a in attributes]
        class_vars = [data.ContinuousVariable(name=c) if isinstance(c, str) else c for c in classes]
        meta_vars = [data.StringVariable(name=m) if isinstance(m, str) else m for m in metas]

        domain = data.Domain(attr_vars, class_vars)
        domain.metas = meta_vars
        return domain


class CreateEmptyTable(TableTests):
    def test_calling_new_with_no_parameters_constructs_a_new_instance(self):
        table = data.Table()
        self.assertIsInstance(table, data.Table)


class CreateTableWithFilename(TableTests):
    filename = "data.tab"

    @patch("os.path.exists", Mock(return_value=True))
    @patch("Orange.data.io.TabDelimReader")
    def test_read_data_calls_appropriate_data_reader_and_returns_its_result(self, reader_mock):
        table_mock = Mock(data.Table)
        reader_instance = reader_mock.return_value = Mock(read_file=Mock(return_value=table_mock))

        table = data.Table.read_data(self.filename)

        reader_instance.read_file.assert_called_with(self.filename)
        self.assertEqual(table, table_mock)

    @patch("os.path.exists", Mock(return_value=False))
    def test_raises_error_if_file_does_not_exist(self):
        with self.assertRaises(IOError):
            data.Table.read_data(self.filename)

    @patch("os.path.exists", Mock(return_value=True))
    def test_raises_error_if_file_has_unknown_extension(self):
        with self.assertRaises(IOError):
            data.Table.read_data("file.invalid_extension")

    @patch("Orange.data.table.Table.read_data")
    def test_calling_new_with_string_argument_calls_read_data(self, read_data):
        data.Table(self.filename)

        read_data.assert_called_with(self.filename)

    @patch("Orange.data.table.Table.read_data")
    def test_calling_new_with_keyword_argument_filename_calls_read_data(self, read_data):
        data.Table(filename=self.filename)

        read_data.assert_called_with(self.filename)


class CreateTableWithDomain(TableTests):
    def test_creates_an_empty_table_with_given_domain(self):
        domain = self.mock_domain()
        table = data.Table.new_from_domain(domain)

        self.assertEqual(table.domain, domain)

    def test_creates_zero_filled_rows_in_X_if_domain_contains_attributes(self):
        domain = self.mock_domain()
        table = data.Table.new_from_domain(domain, self.nrows)

        self.assertEqual(table.X.shape, (self.nrows, len(domain.attributes)))
        self.assertFalse(table.X.any())

    def test_creates_zero_filled_rows_in_Y_if_domain_contains_class_vars(self):
        domain = self.mock_domain(with_classes=True)
        table = data.Table.new_from_domain(domain, self.nrows)

        self.assertEqual(table.Y.shape, (self.nrows, len(domain.class_vars)))
        self.assertFalse(table.Y.any())

    def test_creates_zero_filled_rows_in_metas_if_domain_contains_metas(self):
        domain = self.mock_domain(with_metas=True)
        table = data.Table.new_from_domain(domain, self.nrows)

        self.assertEqual(table.metas.shape, (self.nrows, len(domain.metas)))
        self.assertFalse(table.metas.any())

    def test_creates_weights_if_weights_are_true(self):
        domain = self.mock_domain()
        table = data.Table.new_from_domain(domain, self.nrows, True)

        self.assertEqual(table.W.shape, (self.nrows, ))

    def test_does_not_create_weights_if_weights_are_false(self):
        domain = self.mock_domain()
        table = data.Table.new_from_domain(domain, self.nrows, False)

        self.assertEqual(table.W.shape, (self.nrows, 0))

    @patch("Orange.data.table.Table.new_from_domain")
    def test_calling_new_with_domain_calls_new_from_domain(self, new_from_domain):
        domain = self.mock_domain()
        data.Table(domain)

        new_from_domain.assert_called_with(domain)

class CreateTableWithNumpyData(TableTests):
    def test_creates_a_table_with_given_X(self):
        table = data.Table(self.data)

        self.assertIsInstance(table.domain, data.Domain)
        np.testing.assert_almost_equal(table.X, self.data)

    def test_creates_a_table_with_given_X_and_Y(self):
        table = data.Table(self.data, self.class_data)

        self.assertIsInstance(table.domain, data.Domain)
        np.testing.assert_almost_equal(table.X, self.data)
        np.testing.assert_almost_equal(table.Y, self.class_data)

    def test_creates_a_table_with_given_X_Y_and_metas(self):
        table = data.Table(self.data, self.class_data, self.meta_data)

        self.assertIsInstance(table.domain, data.Domain)
        np.testing.assert_almost_equal(table.X, self.data)
        np.testing.assert_almost_equal(table.Y, self.class_data)
        np.testing.assert_almost_equal(table.metas, self.meta_data)

class CreateTableWithDomainAndNumpyData(TableTests):
    def test_creates_a_table_with_given_domain(self):
        domain = self.mock_domain()
        table = data.Table.new_from_numpy(domain, self.data)

        self.assertEqual(table.domain, domain)

    def test_sets_X(self):
        domain = self.mock_domain()
        table = data.Table.new_from_numpy(domain, self.data)

        np.testing.assert_almost_equal(table.X, self.data)

    def test_sets_Y_if_given(self):
        domain = self.mock_domain(with_classes=True)
        table = data.Table.new_from_numpy(domain, self.data, self.class_data)

        np.testing.assert_almost_equal(table.Y, self.class_data)

    def test_sets_metas_if_given(self):
        domain = self.mock_domain(with_metas=True)
        table = data.Table.new_from_numpy(domain, self.data, metas=self.meta_data)

        np.testing.assert_almost_equal(table.metas, self.meta_data)

    def test_sets_weights_if_given(self):
        domain = self.mock_domain()
        table = data.Table.new_from_numpy(domain, self.data, W=self.weight_data)

        np.testing.assert_almost_equal(table.W, self.weight_data)

    def test_splits_X_and_Y_if_given_in_same_array(self):
        joined_data = np.hstack((self.data, self.class_data))
        domain = self.mock_domain(with_classes=True)
        table = data.Table.new_from_numpy(domain, joined_data)

        np.testing.assert_almost_equal(table.X, self.data)
        np.testing.assert_almost_equal(table.Y, self.class_data)

    def test_initializes_Y_metas_and_W_if_not_given(self):
        domain = self.mock_domain()
        table = data.Table.new_from_numpy(domain, self.data)

        self.assertEqual(table.Y.shape, (self.nrows, len(domain.class_vars)))
        self.assertEqual(table.metas.shape, (self.nrows, len(domain.metas)))
        self.assertEqual(table.W.shape, (self.nrows, 0))

    def test_raises_error_if_columns_in_domain_and_data_do_not_match(self):
        domain = self.mock_domain(with_classes=True, with_metas=True)
        ones = np.zeros((self.nrows, 1))

        with self.assertRaises(ValueError):
            data_ = np.hstack((self.data, ones))
            data.Table.new_from_numpy(domain, data_, self.class_data, self.meta_data)

        with self.assertRaises(ValueError):
            classes_ = np.hstack((self.class_data, ones))
            data.Table.new_from_numpy(domain, self.data, classes_, self.meta_data)

        with self.assertRaises(ValueError):
            metas_ = np.hstack((self.meta_data, ones))
            data.Table.new_from_numpy(domain, self.data, self.class_data, metas_)

    def test_raises_error_if_lengths_of_data_do_not_match(self):
        domain = self.mock_domain(with_classes=True, with_metas=True)

        with self.assertRaises(ValueError):
            data_ = np.vstack((self.data, np.zeros((1, len(self.attributes)))))
            data.Table(domain, data_, self.class_data, self.meta_data)

        with self.assertRaises(ValueError):
            class_data_ = np.vstack((self.class_data, np.zeros((1, len(self.class_vars)))))
            data.Table(domain, self.data, class_data_, self.meta_data)

        with self.assertRaises(ValueError):
            meta_data_ = np.vstack((self.meta_data, np.zeros((1, len(self.metas)))))
            data.Table(domain, self.data, self.class_data, meta_data_)

    @patch("Orange.data.table.Table.new_from_numpy")
    def test_calling_new_with_domain_and_numpy_arrays_calls_new_from_numpy(self, new_from_numpy):
        domain = self.mock_domain()
        data.Table(domain, self.data)
        new_from_numpy.assert_called_with(domain, self.data)

        domain = self.mock_domain(with_classes=True)
        data.Table(domain, self.data, self.class_data)
        new_from_numpy.assert_called_with(domain, self.data, self.class_data)

        domain = self.mock_domain(with_classes=True, with_metas=True)
        data.Table(domain, self.data, self.class_data, self.meta_data)
        new_from_numpy.assert_called_with(domain, self.data, self.class_data, self.meta_data)

        data.Table(domain, self.data, self.class_data, self.meta_data, self.weight_data)
        new_from_numpy.assert_called_with(domain, self.data, self.class_data, self.meta_data, self.weight_data)


class CreateTableWithDomainAndTable(TableTests):
    interesting_slices = [slice(0, 0), #[0:0] - empty slice
                          slice(1), #[:1]  - only first element
                          slice(1, None), #[1:]  - all but first
                          slice(-1, None), #[-1:] - only last element
                          slice(-1), #[:-1] - all but last
                          slice(None), #[:]   - all elements
                          slice(None, None, 2), #[::2] - even elements
                          slice(None, None, -1), #[::-1]- all elements reversed
    ]

    row_indices = [1, 5, 6, 7]

    def setUp(self):
        self.domain = self.create_domain(self.attributes, self.class_vars, self.metas)
        self.table = data.Table(self.domain, self.data, self.class_data, self.meta_data)


    def test_creates_table_with_given_domain(self):
        new_table = data.Table.new_from_table(self.table.domain, self.table)

        self.assertIsInstance(new_table, data.Table)
        self.assertIsNot(self.table, new_table)
        self.assertEqual(new_table.domain, self.domain)

    def test_can_copy_table(self):
        new_table = data.Table.new_from_table(self.domain, self.table)
        self.assert_table_with_filter_matches(new_table, self.table)

    def test_can_filter_rows_with_list(self):
        for indices in ([0], [1, 5, 6, 7]):
            new_table = data.Table.new_from_table(self.domain, self.table, row_indices=indices)
            self.assert_table_with_filter_matches(new_table, self.table, rows=indices)

    def test_can_filter_row_with_slice(self):
        for slice_ in self.interesting_slices:
            new_table = data.Table.new_from_table(self.domain, self.table, row_indices=slice_)
            self.assert_table_with_filter_matches(new_table, self.table, rows=slice_)


    def test_can_use_attributes_as_new_columns(self):
        a, c, m = column_sizes(self.table)
        order = [random.randrange(a) for _ in self.domain.attributes]
        new_attributes = [self.domain.attributes[i] for i in order]
        new_domain = self.create_domain(new_attributes, new_attributes, new_attributes)
        new_table = data.Table.new_from_table(new_domain, self.table)

        self.assert_table_with_filter_matches(new_table, self.table, xcols=order, ycols=order, mcols=order)

    def test_can_use_class_vars_as_new_columns(self):
        a, c, m = column_sizes(self.table)
        order = [random.randrange(a, a + c) for _ in self.domain.class_vars]
        new_classes = [self.domain.class_vars[i-a] for i in order]
        new_domain = self.create_domain(new_classes, new_classes, new_classes)
        new_table = data.Table.new_from_table(new_domain, self.table)

        self.assert_table_with_filter_matches(new_table, self.table, xcols=order, ycols=order, mcols=order)

    def test_can_use_metas_as_new_columns(self):
        a, c, m = column_sizes(self.table)
        order = [random.randrange(-m + 1, 0) for _ in self.domain.metas]
        new_metas = [self.domain.metas[::-1][i] for i in order]
        new_domain = self.create_domain(new_metas, new_metas, new_metas)
        new_table = data.Table.new_from_table(new_domain, self.table)

        self.assert_table_with_filter_matches(new_table, self.table, xcols=order, ycols=order, mcols=order)

    def test_can_use_combination_of_all_as_new_columns(self):
        a, c, m = column_sizes(self.table)
        order = [random.randrange(a) for _ in self.domain.attributes] +\
                [random.randrange(a, a + c) for _ in self.domain.class_vars] +\
                [random.randrange(-m + 1, 0) for _ in self.domain.metas]
        random.shuffle(order)
        vars = list(self.domain.variables) + self.domain.metas[::-1]
        vars = [vars[i] for i in order]

        new_domain = self.create_domain(vars, vars, vars)
        new_table = data.Table.new_from_table(new_domain, self.table)
        self.assert_table_with_filter_matches(new_table, self.table, xcols=order, ycols=order, mcols=order)

    def assert_table_with_filter_matches(self, new_table, old_table, rows=..., xcols=..., ycols=..., mcols=...):
        a, c, m = column_sizes(old_table)
        xcols = slice(a) if xcols is Ellipsis else xcols
        ycols = slice(a, a + c) if ycols is Ellipsis else ycols
        mcols = slice(None, -m - 1, -1) if mcols is Ellipsis else mcols

        # Indexing used by convert_domain uses positive indices for variables and classes (classes come after
        # attributes) and negative indices for meta features. This is equivalent to ordinary indexing in  a magic table
        # below.
        magic_table = np.hstack((old_table.X, old_table.Y, old_table.metas[:, ::-1]))
        np.testing.assert_almost_equal(new_table.X, magic_table[rows, xcols])
        np.testing.assert_almost_equal(new_table.Y, magic_table[rows, ycols])
        np.testing.assert_almost_equal(new_table.metas, magic_table[rows, mcols])
        np.testing.assert_almost_equal(new_table.W, self.table.W[rows])


def isspecial(s):
    return isinstance(s, slice) or s is Ellipsis
def split_columns(indices, t):
    a, c, m = column_sizes(t)
    if indices is ...:
        return slice(a), slice(c), slice(m)
    elif isinstance(indices, slice):
        return indices, slice(0,0), slice(0,0)
    elif not isinstance(indices, list) and not isinstance(indices, tuple):
        indices = [indices]
    return (
            [t.domain.index(x) for x in indices if 0 <= t.domain.index(x) < a] or slice(0, 0),
            [t.domain.index(x)-a for x in indices if t.domain.index(x) >= a] or slice(0, 0),
            [-t.domain.index(x)-1 for x in indices if t.domain.index(x) < 0] or slice(0, 0))
def getname(variable): return variable.name


class TableIndexingTests(TableTests):
    def setUp(self):
        d = self.domain = self.create_domain(self.attributes, self.class_vars, self.metas)
        t = self.table = data.Table(self.domain, self.data, self.class_data, self.meta_data)
        self.magic_table = np.hstack((self.table.X, self.table.Y, self.table.metas[:, ::-1]))

        self.rows = [0, -1]
        self.multiple_rows = [slice(0,0), ..., slice(1, -1, -1)]
        a, c, m = column_sizes(t)
        columns = [0, a-1, a, a+c-1, -1, -m]
        self.columns = chain(columns,
                                       map(lambda x:d[x], columns),
                                       map(lambda x:d[x].name, columns))
        self.multiple_columns = chain(self.multiple_rows,
                                      [d.attributes, d.class_vars, d.metas, [0,a,-1]],
                                      [self.attributes, self.class_vars, self.metas],
                                      [self.attributes + self.class_vars + self.metas])

        # TODO: indexing with [[0,1], [0,1]] produces weird results
        # TODO: what should be the results of table[1, :]

    def test_can_select_a_single_value(self):
        for r in self.rows:
            for c in self.columns:
                value = self.table[r, c]
                self.assertAlmostEqual(value, self.magic_table[r,self.domain.index(c)])

                value = self.table[r][c]
                self.assertAlmostEqual(value, self.magic_table[r,self.domain.index(c)])

    def test_can_select_a_single_row(self):
        for r in self.rows:
            row = self.table[r]
            np.testing.assert_almost_equal(np.array(list(row)), np.hstack((self.data[r, :], self.class_data[r, :])))

    def test_can_select_a_subset_of_rows_and_columns(self):
        for r in self.rows:
            for c in self.multiple_columns:
                table = self.table[r, c]

                attr, cls, metas = split_columns(c, self.table)
                np.testing.assert_almost_equal(table.X, self.table.X[[r], attr])
                np.testing.assert_almost_equal(table.Y, self.table.Y[[r], cls])
                np.testing.assert_almost_equal(table.metas, self.table.metas[[r], metas])

        for r in self.multiple_rows:
            for c in chain(self.columns, self.multiple_rows):
                table = self.table[r, c]

                attr, cls, metas = split_columns(c, self.table)
                np.testing.assert_almost_equal(table.X, self.table.X[r, attr])
                np.testing.assert_almost_equal(table.Y, self.table.Y[r, cls])
                np.testing.assert_almost_equal(table.metas, self.table.metas[r, metas])


class TableElementAssignmentTest(TableTests):
    def setUp(self):
        self.domain = self.create_domain(self.attributes, self.class_vars, self.metas)
        self.table = data.Table(self.domain, self.data, self.class_data, self.meta_data)


    def test_can_assign_values(self):
        self.table[0, 0] = 42.
        self.assertAlmostEqual(self.table.X[0, 0], 42.)

    def test_can_assign_values_to_classes(self):
        a, c, m = column_sizes(self.table)
        self.table[0, a] = 42.
        self.assertAlmostEqual(self.table.Y[0, 0], 42.)

    def test_can_assign_values_to_metas(self):
        self.table[0, -1] = 42.
        self.assertAlmostEqual(self.table.metas[0, 0], 42.)

    def test_can_assign_rows_to_rows(self):
        self.table[0] = self.table[1]
        np.testing.assert_almost_equal(self.table.X[0], self.table.X[1])
        np.testing.assert_almost_equal(self.table.Y[0], self.table.Y[1])
        np.testing.assert_almost_equal(self.table.metas[0], self.table.metas[1])

    def test_can_assign_lists(self):
        a, c, m = column_sizes(self.table)
        new_example = [float(i) for i in range(13)]
        self.table[0] = new_example
        np.testing.assert_almost_equal(self.table.X[0], np.array(new_example[:a]))
        np.testing.assert_almost_equal(self.table.Y[0], np.array(new_example[a:]))

    def test_can_assign_np_array(self):
        a, c, m = column_sizes(self.table)
        new_example = np.array([float(i) for i in range(13)])
        self.table[0] = new_example
        np.testing.assert_almost_equal(self.table.X[0], new_example[:a])
        np.testing.assert_almost_equal(self.table.Y[0], new_example[a:])


if __name__ == "__main__":
    unittest.main()