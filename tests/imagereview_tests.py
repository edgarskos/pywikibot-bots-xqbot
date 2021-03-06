# -*- coding: utf-8  -*-
"""Test imagereview modules."""
#
# (C) xqt, 2016
#
# Distributed under the terms of the MIT license.
#
from __future__ import absolute_import, print_function, unicode_literals

__version__ = '$Id $'

import unittest

from tests import utils  # noqa
import imagereview

import pywikibot

from pywikibot import Timestamp, config
from pywikibot.tools import StringTypes


class TestMessages(unittest.TestCase):

    """Test messages."""

    def test_message_keys(self):
        """Test message keys for mail and talk page."""
        self.assertEqual(imagereview.remark.keys(),
                         imagereview.remark_mail.keys())
        self.assertEqual(set(imagereview.remark.keys()),
                         set(imagereview.DUP_REASONS))

    def test_message_exist(self):
        """Test whether messages exists."""
        self.assertTrue(hasattr(imagereview, 'msg'))
        self.assertTrue(hasattr(imagereview, 'mail_msg'))


class TestDUP_Image(unittest.TestCase):

    """Test DUP_Image class."""

    REMARK = 'Urheber und Uploader sind nicht identisch.'
    TMPL = '{{düp|Lizenz|Freigabe | Quelle| Urheber | Hinweis = %s }}' % REMARK

    @classmethod
    def setUpClass(cls):
        """Setup class."""
        super(TestDUP_Image, cls).setUpClass()
        cls.site = pywikibot.Site('de', 'wikipedia')
        cls.review_tpl = pywikibot.Page(cls.site, 'düp', 10)

    @classmethod
    def tearDownClass(cls):
        """Cleanup Class."""
        del cls.site
        del cls.review_tpl
        super(TestDUP_Image, cls).tearDownClass()

    def tearDown(self):
        """Cleanup methods."""
        del self.image
        super(TestDUP_Image, self).tearDown()

    def init_content(self):
        """Instantiate DUP_Image."""
        self.image = imagereview.DUP_Image(self.site, 'Sample.jpg', self.TMPL)
        self.image._templates.append(self.review_tpl)
        self.image.text += self.TMPL
        self.assertEqual(self.image.text, self.image._text)
        self.image.__init__(self.image.site, self.image.title(),
                            self.image.text)
        self.assertEqual(self.image._contents, self.image.text)

    def test_empty_instance(self):
        """Test instance variables."""
        self.image = imagereview.DUP_Image(self.site, 'Sample.jpg')
        self.assertIsNone(self.image._contents)
        self.assertIsNone(self.image._editTime)
        self.assertEqual(self.image._file_revisions, dict())
        self.assertEqual(self.image._revisions, dict())
        self.assertIsNone(self.image.done)
        self.assertFalse(self.image.info)
        self.assertEqual(self.image.reasons, set([]))
        self.assertIsNone(self.image.remark)
        self.assertEqual(self.image.review_tpl, list())

    def test_instance_with_content(self):
        """Test instance variables with content given."""
        self.init_content()
        self.assertIsNone(self.image._editTime)
        self.assertFalse(self.image.done)
        self.assertTrue(self.image.info)
        self.assertEqual(len(self.image.reasons), 5)
        self.assertIsNone(self.image.remark)
        self.assertEqual(self.image.review_tpl[0], self.review_tpl)

    def test_valid_reasons(self):
        """Test validReasons method."""
        self.init_content()
        self.assertTrue(self.image.validReasons)
        self.assertEqual(self.image.remark, self.REMARK)
        self.assertLessEqual(self.image.reasons, set(imagereview.DUP_REASONS))

    def test_hasRefs(self):
        """Test hasRefs method."""
        self.init_content()
        self.assertTrue(self.image.hasRefs)


class TestCheckImageBot(unittest.TestCase):

    """Test CheckImageBot."""

    @classmethod
    def setUpClass(cls):
        """Setup Class."""
        config.family = 'wikipedia'
        config.mylang = 'de'

    def test_invalid_option(self):
        """Test run method without options."""
        with self.assertRaises(NotImplementedError):
            imagereview.CheckImageBot()

    def test_list_option(self):
        """Test run method with list options."""
        bot = imagereview.CheckImageBot(list=True, total=1)
        self.assertEqual(bot.sort, 1)
        self.assertTrue(bot.filter)
        self.assertEqual(bot.total, 1)

    def test_check_option(self):
        """Test run method with check options."""
        bot = imagereview.CheckImageBot(check=True)
        self.assertEqual(bot.sort, 0)
        self.assertFalse(bot.filter)
        self.assertIsNone(bot.total)

    def test_build_table_with_list(self):
        """Test buildt table with list option."""
        bot = imagereview.CheckImageBot(list=True)
        table = bot.build_table(False)
        if not table:
            self.skipTest('Table of files to review is empty')
        key = list(table.keys())[0]  # py3 comp
        data = table[key]
        item = data[0]
        self.assertIsInstance(key, StringTypes)
        self.assertIsInstance(data, list)
        self.assertIsInstance(item, list)
        self.assertEqual(len(item), 4)
        linkedtitle, uploader, filepage, reason = item
        user, time = uploader
        self.assertIsInstance(linkedtitle, StringTypes)
        self.assertIsInstance(uploader, list)
        self.assertIsInstance(filepage, imagereview.DUP_Image)
        self.assertIsInstance(reason, StringTypes)
        self.assertIsInstance(user, StringTypes)
        self.assertIsInstance(time, StringTypes)
        self.assertEqual(reason, '')
        self.assertEqual(filepage.title(asLink=True, textlink=True),
                         linkedtitle)
        self.assertEqual(time, key)
        self.assertIsInstance(Timestamp.fromISOformat(time), Timestamp)

    def test_build_table_with_check(self):
        """Test buildt table with check option."""
        bot = imagereview.CheckImageBot(check=True, total=0)
        bot.cat = 'Nonexisting page for imagereview'
        table = bot.build_table(save=False, unittest=True)
        if not table:
            self.skipTest('Table of files to review is empty')
        key = list(table.keys())[0]  # py3 comp
        data = table[key]
        item = data[0]
        self.assertIsInstance(key, StringTypes)
        self.assertIsInstance(data, list)
        self.assertIsInstance(item, list)
        self.assertEqual(len(item), 4)
        linkedtitle, uploader, filepage, reason = item
        user, time = uploader
        self.assertIsInstance(linkedtitle, StringTypes)
        self.assertIsInstance(uploader, list)
        self.assertIsInstance(filepage, imagereview.DUP_Image)
        self.assertIsInstance(reason, StringTypes)
        self.assertIsInstance(user, StringTypes)
        self.assertIsInstance(time, StringTypes)
        self.assertEqual(reason, '')
        self.assertEqual(filepage.title(asLink=True, textlink=True),
                         linkedtitle)
        self.assertEqual(user, key)
        self.assertIsInstance(Timestamp.fromISOformat(time), Timestamp)


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
