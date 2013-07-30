import unittest
from sostore import Collection, ID_KEY, ConnectionException

class CollectionTestCase(unittest.TestCase):
    def setUp(self):
        self.db = Collection("testcases", db=":memory:")
        
    def tearDown(self):
        self.db.done()
        
    def test_connection(self):
        self.assertIsNotNone(self.db.connection)
        
    def test_connection_closed(self):
        self.db.done()
        self.assertRaises(ConnectionException, self.db.all)
        
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
            
    def test_insert_randomize(self):
        d = {'first': 'Margaux', 'last': 'LaFleur', 'age': 27, 'female': True}
        res = self.db.insert(d, randomize=True)
        
        self.assertTrue(res[ID_KEY] >= 1E+6)
        
        d2 = {'first': 'Henry'}
        res2 = self.db.insert(d2, randomize=True)
        
        # Check for non-sequential keys
        self.assertTrue(abs(d2[ID_KEY] - d[ID_KEY]) > 1)
           
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
        res = self.db.update(res)
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
        
    def test_count(self):
        d1 = {'first': 'Henry', 'last': 'McCallum'}
        d2 = {'first': 'Margaux', 'last': 'LaFleur'}
        d3 = {'first': 'Stephen', 'occupation': 'king'}
        d1 = self.db.insert(d1)
        d2 = self.db.insert(d2)
        d3 = self.db.insert(d3)
        
        self.assertEqual(self.db.count, 3)
        
        self.db.remove(d3)
        
        self.assertEqual(self.db.count, 2)
        
    def test_get(self):
        d1 = {'first': 'Henry', 'last': 'McCallum'}
        d2 = {'first': 'Margaux', 'last': 'LaFleur'}
        d1 = self.db.insert(d1)
        d2 = self.db.insert(d2)
        
        self.assertIsNotNone(self.db.get(d1[ID_KEY]))
        self.assertIsNotNone(self.db.get(d2[ID_KEY]))
        self.assertIsNone(self.db.get(-75))
        
    def test_get_many(self):
        d1 = {'first': 'Henry', 'last': 'McCallum'}
        d2 = {'first': 'Margaux', 'last': 'LaFleur'}
        d3 = {'first': 'Stephen', 'occupation': 'king'}
        d1 = self.db.insert(d1)
        d2 = self.db.insert(d2)
        d3 = self.db.insert(d3)
        
        ids = (d1[ID_KEY], d2[ID_KEY])
        
        many = self.db.get_many(ids)
        matches = 0
        found_henry = False
        found_margaux = False
        for x in many:
            self.assertIn('first', x.keys())
            self.assertIn('last', x.keys())
            self.assertIn(ID_KEY, x.keys())
            if x['first'] == 'Henry' and x['last'] == 'McCallum' and not found_henry:
                matches = matches + 1
                found_henry = True
                
            if x['first'] == 'Margaux' and x['last'] == 'LaFleur' and not found_margaux:
                matches = matches + 1
                found_margaux = True
                
        self.assertEqual(matches, 2)
        
        many = self.db.get_many(ids, fields=('first',))
        matches = 0
        found_henry = False
        found_margaux = False
        for x in many:
            self.assertIn('first', x.keys())
            self.assertNotIn('last', x.keys())
            self.assertNotIn(ID_KEY, x.keys())
            if x['first'] == 'Henry' and not found_henry:
                matches = matches + 1
                found_henry = True
            if x['first'] == 'Margaux' and not found_margaux:
                matches = matches + 1
                found_margaux = True
                
        self.assertEqual(matches, 2)
        
        d2['occupation'] = 'magician'
        self.db.update(d2)
        
        many = self.db.get_many(ids, fields=('occupation',))
        self.assertEqual(len(many), 2)
        self.assertEqual(len(many[0].keys()), 0)
        self.assertEqual(len(many[1].keys()), 1)
    
    def test_get_all(self):
        d1 = {'first': 'Henry', 'last': 'McCallum'}
        d2 = {'first': 'Margaux', 'last': 'LaFleur'}
        d3 = {'first': 'Stephen', 'occupation': 'king'}
        d1 = self.db.insert(d1)
        d2 = self.db.insert(d2)
        d3 = self.db.insert(d3)
        
        all = self.db.all()
        self.assertEqual(len(all), 3)
        first = ['Henry', 'Margaux', 'Stephen']
        last = ['McCallum', 'LaFleur']
        occupation = ['king',]
        for x in all:
            if x['first'] in first:
                first.remove(x['first'])
            if 'last' in x.keys() and x['last'] in last:
                last.remove(x['last'])
            if 'occupation' in x.keys() and x['occupation'] in occupation:
                occupation.remove(x['occupation'])
        self.assertEqual(len(first), 0)
        self.assertEqual(len(last), 0)
        self.assertEqual(len(occupation), 0)
        
        all = self.db.all(fields=('last'))
        self.assertEqual(len(all), 3)
        last = ['McCallum', 'LaFleur']
        for x in all:
            if 'last' in x.keys() and x['last'] in last:
                last.remove(x['last'])
            self.assertNotIn('first', x.keys())
            self.assertNotIn('occupation', x.keys())
            self.assertNotIn(ID_KEY, x.keys())
        self.assertEqual(len(last), 0)
        
    def test_find_one(self):
        d1 = {'first': 'Henry', 'last': 'McCallum'}
        d2 = {'first': 'Margaux', 'last': 'LaFleur', 'siblings': ['Phillip', 'Jonelle']}
        d3 = {'first': 'Stephen', 'occupation': 'king'}
        d1 = self.db.insert(d1)
        d2 = self.db.insert(d2)
        d3 = self.db.insert(d3)
        
        res = self.db.find_one('occupation', 'king')
        self.assertIsNotNone(res)
        self.assertEqual(d3[ID_KEY], res[ID_KEY])
        
        res = self.db.find_one('first', 'Erin')
        self.assertIsNone(res)
        
        res = self.db.find_one('siblings', 'Phillip')
        self.assertEqual(res['first'], 'Margaux')
        
    def test_random_entries(self):
        d1 = {'first': 'Henry', 'last': 'McCallum'}
        d2 = {'first': 'Margaux', 'last': 'LaFleur', 'siblings': ['Phillip', 'Jonelle']}
        d3 = {'first': 'Stephen', 'occupation': 'king'}
        d1 = self.db.insert(d1)
        d2 = self.db.insert(d2)
        d3 = self.db.insert(d3)
        
        res = self.db.random_entries(2)
        self.assertEqual(len(res), 2)
        for x in res:
            self.assertIn(x['first'], ['Henry', 'Margaux', 'Stephen'])
        
    def test_random_entry(self):
        d1 = {'first': 'Henry', 'last': 'McCallum'}
        d2 = {'first': 'Margaux', 'last': 'LaFleur', 'siblings': ['Phillip', 'Jonelle']}
        d3 = {'first': 'Stephen', 'occupation': 'king'}
        d1 = self.db.insert(d1)
        d2 = self.db.insert(d2)
        d3 = self.db.insert(d3)
        
        res = self.db.random_entry()
        self.assertIsNotNone(res)
        self.assertIn(res['first'], ['Henry', 'Margaux', 'Stephen'])
        
    def test_find_field(self):
        d1 = {'first': 'Henry', 'last': 'McCallum', 'occupation': 'magician'}
        d2 = {'first': 'Margaux', 'last': 'LaFleur', 'occupation': ['magician', 'illusionist']}
        d3 = {'first': 'Stephen', 'occupation': 'king'}
        d4 = {'first': 'Erin', 'age': 17}
        d1 = self.db.insert(d1)
        d2 = self.db.insert(d2)
        d3 = self.db.insert(d3)
        d4 = self.db.insert(d4)
        
        res = self.db.find_field('occupation', 'magician')
        self.assertEqual(len(res), 2)
        self.assertIn(d1[ID_KEY], res)
        self.assertIn(d2[ID_KEY], res)
        
        res = self.db.find_field('first', 'Phillip')
        self.assertEqual(len(res), 0)
        
        res = self.db.find_field('first', 'Erin')
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], d4[ID_KEY])

        res = self.db.find_field('age', 17)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], d4[ID_KEY])
        
        res = self.db.find_field('age', '17', compare_function=lambda x,y: int(x) == int(y))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], d4[ID_KEY])
