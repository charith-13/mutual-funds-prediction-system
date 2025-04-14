import unittest
from new_app import app

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # Test home page loads successfully
    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mutual Fund Predictor', response.data)

    # Test input validation with valid data (SIP type)
    def test_recommend_valid_sip_input(self):
        response = self.app.post('/recommend', data=dict(
            fund_house='HDFC Mutual Fund',
            fund_type='Equity',
            min_sip=1000,
            min_LumpSum=0,
            years=3,
            investment_type='SIP'
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Suggested F unds', response.data)

    # Test input validation with valid LumpSum data
    def test_recommend_valid_lumpsum_input(self):
        response = self.app.post('/recommend', data=dict(
            fund_house='HDFC Mutual Fund',
            fund_type='Equity',
            min_sip=0,
            min_LumpSum=5000,
            years=5,
            investment_type='LumpSum'
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Suggested Funds', response.data)

    # Test input validation with missing fields
    def test_missing_input(self):
        response = self.app.post('/recommend', data=dict(
            fund_house='',
            fund_type='',
            min_sip='',
            min_LumpSum='',
            years='',
            investment_type=''
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No matching funds found', response.data)

    # Test that returns error or handles invalid years
    def test_invalid_years_input(self):
        response = self.app.post('/recommend', data=dict(
            fund_house='HDFC Mutual Fund',
            fund_type='Equity',
            min_sip=1000,
            min_LumpSum=0,
            years=10,
            investment_type='SIP'
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Suggested Funds', response.data)  # if fallback for returns is handled

if __name__ == '__main__':
    unittest.main()