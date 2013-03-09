import unittest
from sostore import Collection, ID_KEY

class CollectionTestCase(unittest.TestCase):
    def setUp(self):
        self.db = Collection("testcases", db=":memory:")
        
    def tearDown(self):
        self.db.done()
        
    def test_connection(self):
        self.assertIsNotNone(self.db.connection)
        
    def test_insert(self):
        d = {'first': 'Margaux', 'last': 'LaFleur', 'age': 27, 'female': True}
        res = self.db.insert(d)
        
        self.assertIn(ID_KEY, res.keys())
        for k in d.keys():
            self.assertEqual(d[k], res[k])
            
        d_db = self.db.get(res[ID_KEY])
        self.assertIsNotNone(d_db)
        for k in d.keys():
            self.assertEqual(d[k], d_db[k])
           
    def test_update_nonexistant(self):
        d = {'first': 'Henry'}
        self.assertRaises(ValueError, self.db.update, d)
           
    def test_insert_existant(self):
        d = {'first': 'Margaux', 'last': 'LaFleur', 'age': 27, 'female': True}
        self.db.insert(d)
        
        self.assertRaises(ValueError, self.db.insert, d)
           
    def test_update(self):
        d = {'first': 'Henry'}
        inserted = self.db.insert(d)
        
        inserted['last'] = 'McCallum'
        
        res = self.db.update(inserted)
        self.assertEqual(res['last'], 'McCallum')
        self.assertEqual(res['first'], 'Henry')
        
        res['first'] = 'Hank'
        res = self.db.update(inserted)
        self.assertEqual(res['first'], 'Hank')
        
    def test_remove(self):
        d1 = {'first': 'Henry', 'last': 'McCallum'}
        d2 = {'first': 'Margaux', 'last': 'LaFleur'}
        d1 = self.db.insert(d1)
        d2 = self.db.insert(d2)
        
        self.assertIsNotNone(self.db.get(d1[ID_KEY]))
        self.assertIsNotNone(self.db.get(d2[ID_KEY]))
        
        self.db.remove(d2[ID_KEY])
        self.assertIsNone(self.db.get(d2[ID_KEY]))
        self.assertIsNotNone(self.db.get(d1[ID_KEY]))
        
        self.db.remove(d1)
        self.assertIsNone(self.db.get(d1[ID_KEY]))
        
    def test_get(self):
        d1 = {'first': 'Henry', 'last': 'McCallum'}
        d2 = {'first': 'Margaux', 'last': 'LaFleur'}
        d1 = self.db.insert(d1)
        d2 = self.db.insert(d2)
        
        self.assertIsNotNone(self.db.get(d1[ID_KEY]))
        self.assertIsNotNone(self.db.get(d2[ID_KEY]))
        self.assertIsNone(self.db.get(-75))
        
    