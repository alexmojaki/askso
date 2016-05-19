# coding=utf-8
import inspect
import unittest
from functools import partial

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


class IDs(object):
    next_button = 'next-button'
    code_editor = 'code-editor'
    run = 'run'
    stdin_error = 'stdin-error'
    code_too_long = 'code-too-long'
    expected_output = 'expected-output'
    question = 'question'
    code_message = 'code-message'


all_ids = [v for k, v in inspect.getmembers(IDs) if k[0] != '_']


class Test(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.PhantomJS(service_args=['--webdriver-loglevel=DEBUG'])

    def test(self):
        try:
            self._do_test()
        except:
            self.driver.save_screenshot('screenshot.png')
            raise

    def _do_test(self):
        driver = self.driver
        driver.get('http://localhost:5000')
        self.assertEqual('AskSO - StackOverflow Python Question Assistant', driver.title)
        next_button = WebDriverWait(driver, 20).until(
            expected_conditions.visibility_of_element_located((By.ID, IDs.next_button)))
        assert isinstance(next_button, WebElement)
        driver.implicitly_wait(0.3)

        find = driver.find_element_by_id

        def button_text(text):
            self.assertEqual(text, next_button.get_attribute('value'))

        def starts_with(elem, text):
            self.assertEqual(text, elem.text[:len(text)])

        main_message = find('main-message')

        always_displayed = set()

        def displayed(*elems):
            self.assertEqual(always_displayed.union(elems),
                             set([i for i in all_ids
                                  if driver.find_element_by_id(i).is_displayed()]))

        button_text('Start')
        starts_with(main_message, "Welcome! I'm going to help you")
        displayed(IDs.next_button)

        next_button.click()
        always_displayed |= set([IDs.code_editor, IDs.run])
        displayed()

        run = find(IDs.run)

        def set_editor_text(name, text):
            driver.execute_script(u"%s_editor.setValue('%s')" % (name, text))

        set_code = partial(set_editor_text, 'code')
        set_output = partial(set_editor_text, 'output')

        def run_code(code):
            set_code(code)
            run.click()

        def results(*texts):
            children = find('results').find_elements_by_xpath("./*")
            self.assertEqual(len(texts), len(children))
            for child, text in zip(children, texts):
                starts_with(child, text)

        run_code('input()')
        displayed(IDs.stdin_error)
        results()

        run_code('test_error')
        results('There was an error on the server!',
                'Traceback')
        displayed()

        run_code('print("hi.")')
        always_displayed |= set([IDs.next_button])
        displayed()
        results('Output:',
                'hi.')

        next_button.click()
        starts_with(main_message, 'Is the code as short as possible?')
        button_text('Yes')
        displayed()

        next_button.click()
        starts_with(main_message, 'Have you tried your best to solve the problem?')
        button_text('Yes')
        displayed()

        next_button.click()
        starts_with(main_message, 'What result are you trying to get?')
        button_text('Done')
        self.assertFalse(next_button.is_enabled())
        always_displayed |= set([IDs.expected_output])
        displayed()

        set_output('a')
        self.assertTrue(next_button.is_enabled())
        set_output('')
        self.assertFalse(next_button.is_enabled())

        set_output('a\\nb')
        next_button.click()
        always_displayed |= set([IDs.question])
        displayed()
        starts_with(main_message, 'Congratulations! Here is the basic text')
        button_text('Regenerate question')

        question = find(IDs.question)

        def question_text(text):
            actual_text = question.get_attribute('value')
            self.assertTrue(actual_text.startswith(
                "*Explain what you're trying to do and why*\n\nHere is my code:\n\n    "))
            self.assertTrue(actual_text.endswith(
                "\n\n"
                "*Maybe add some more explanation and details. Make it clear what you're asking.*\n\n"
                "I am running Python 2.7.10.\n\n"
                "----------\n\n"
                "*This question was written with the help of [AskSO](https://github.com/alexmojaki/askso).*"))
            self.assertTrue('This is the result I want:\n\n    ' in actual_text)
            self.assertTrue(text in actual_text)

        question_text('\n\n    a\n    b')

        set_code('x\\n' * 51)
        displayed(IDs.code_too_long)
        set_code('x\\n' * 49)
        displayed()
        button_text('Run your code again before regenerating the question')
        self.assertFalse(next_button.is_enabled())
        the_code = 'this is the code'
        run_code(the_code)
        results('Error:',
                'Traceback')
        button_text('Regenerate question')
        self.assertTrue(next_button.is_enabled())
        next_button.click()  # regenerate question
        question_text('\n\nThere is no output. There is an error:\n\n    ')
        question_text('SyntaxError')
        question_text('my_script.py"')
        run_code('print("some output");d')
        results('Output:',
                'some output',
                'Error:',
                'Traceback')
        displayed()
        run_code('import time;time.sleep(1)')
        displayed(IDs.code_message)
        self.assertEqual(find(IDs.code_message).text, 'Running...')
        time.sleep(1.2)
        self.assertEqual(find(IDs.code_message).text, 'There was no output at all.')
        results()
        run_code(u'open("/tmp/__empty", "w"); open("/tmp/__unicode", "w").write("é"); '
                 u'[open("/tmp/__n%s" % i, "w").write(str(i)) for i in range(3)]')
        results('The file /tmp/__empty is empty.',
                'Contents of the file /tmp/__n0:',
                '0',
                'Contents of the file /tmp/__n1:',
                '1',
                'Contents of the file /tmp/__n2:',
                '2',
                "You're opening too many different files",
                "Try to avoid using files",
                'Some of the files opened did not consist of only plain ASCII')
        next_button.click()
        question_text('There is no output. No error is raised. `/tmp/__empty` is empty. '
                      'Here are the contents of `/tmp/__n0`:\n\n    0\n\n'
                      'Here are the contents of `/tmp/__n1`:\n\n    1\n\n'
                      'Here are the contents of `/tmp/__n2`:\n\n    2\n\n')

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()
