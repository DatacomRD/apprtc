import unittest
import TWR

class TWRUnitTest(unittest.TestCase):
  def setUp(self):
    # First, create an instance of the Testbed class.
    self.srv = TWR.iServer()

  def tearDown(self):
    self.srv.close()
    self.srv = None

  def testSendEnterCommand(self):
    #self.assertEqual(17, len(apprtc.generate_random(17)))
    self.srv.user_enter_concall('user1', 'room1')

  def testSendLeaveCommand(self):
    self.srv.user_leave_concall('user1', 'room1')


if __name__ == '__main__':
    unittest.main()

