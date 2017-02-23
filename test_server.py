import server

import unittest


class ServerIntegrationTestCase(unittest.TestCase):

    def setUp(self):
        server.app.config['TESTING'] = True
        self.client = server.app.test_client()

    def test_login(self):
        result = self.client.get('/login')
        self.assertEqual(result.status_code, 200)
        self.assertIn('<h1>Login</h1>', result.data)


class ServerIntegrationUserLoggedInTestCase(unittest.TestCase):

    def setUp(self):
        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = 'key'
        self.client = server.app.test_client()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['is_admin'] = False

    def test_login(self):
        """If the user is already logged in, this should redirect the user to
        the user profile
        """

        result = self.client.get('/login')
        self.assertIn("s World</h1>", result.data)


class ServerIntegrationUserLoggedInAndAdminTestCase(unittest.TestCase):

    def setUp(self):
        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = 'key'
        self.client = server.app.test_client()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 3
                sess['is_admin'] = True

    def test_login(self):
        """If the user is already logged in, this should redirect the user to
        the user profile
        """

        result = self.client.get('/login')
        self.assertIn("s World</h1>", result.data)







if __name__ == '__main__':
    unittest.main()
