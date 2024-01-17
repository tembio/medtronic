import unittest
from mock import patch, Mock
from reporters import HttpReporter

class TestHttpReporter(unittest.TestCase):
    testData = "data"

    @patch('requests.post')
    def test_send_calls_right_url(self, mocked_post):
        mocked_post.return_value = Mock(status_code=200)
        testUrl = 'http://valid.com'
        testData = "data"

        reporter = HttpReporter(testUrl)
        reporter.send(testData)

        mocked_post.assert_called_once_with(url=testUrl,data=testData)

    @patch('requests.post')
    def test_send_raise_exception_if_connection_error(self, mocked_post):
        mocked_post.side_effect = ConnectionError("Could not send message")
        testData = "data"

        reporter = HttpReporter("url")
        
        self.assertRaises(ConnectionError, HttpReporter.send, reporter, testData)

        mocked_post.assert_called_once_with(url="url",data=testData)

    @patch('requests.post')
    def test_send_raise_exception_if_not_200_response(self, mocked_post):
        mocked_post.return_value = Mock(status_code=404)
        testData = "data"

        reporter = HttpReporter("invalid url")
        
        self.assertRaises(ValueError, HttpReporter.send, reporter, testData)

        mocked_post.assert_called_once_with(url="invalid url",data=testData)

if __name__ == '__main__':
    unittest.main()