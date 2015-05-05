""" Put in integration/
because it requires psutil to function properly
"""

# stdlib
import os

# 3p
from mock import patch
import psutil

# project
from tests.checks.common import AgentCheckTest


class ProcessCheckTest(AgentCheckTest):
    CHECK_NAME = 'process'

    def get_psutil_proc(self):
        return psutil.Process(os.getpid())

    def test_psutil_wrapper_simple(self):
        # Load check with empty config
        self.run_check({})
        name = self.check.psutil_wrapper(
            self.get_psutil_proc(),
            'name',
            None
        )

        self.assertNotEquals(name, None)

    def test_psutil_wrapper_simple_fail(self):
        # Load check with empty config
        self.run_check({})
        name = self.check.psutil_wrapper(
            self.get_psutil_proc(),
            'blah',
            None
        )

        self.assertEquals(name, None)

    def test_psutil_wrapper_accessors(self):
        # Load check with empty config
        self.run_check({})
        meminfo = self.check.psutil_wrapper(
            self.get_psutil_proc(),
            'memory_info',
            ['rss', 'vms', 'foo']
        )

        self.assertIn('rss', meminfo)
        self.assertIn('vms', meminfo)
        self.assertNotIn('foo', meminfo)

    def test_psutil_wrapper_accessors_fail(self):
        # Load check with empty config
        self.run_check({})
        meminfo = self.check.psutil_wrapper(
            self.get_psutil_proc(),
            'memory_infoo',
            ['rss', 'vms']
        )

        self.assertNotIn('rss', meminfo)
        self.assertNotIn('vms', meminfo)

    def test_ad_cache(self):
        config = {
            'instances': [{
                'name': 'python',
                'search_string': ['python'],
                'ignore_denied_access': 'false'
            }]
        }

        def deny_cmdline(obj):
            raise psutil.AccessDenied()

        try:
            with patch.object(psutil.Process, 'name', deny_cmdline):
                self.run_check(config)
        except psutil.AccessDenied:
            pass

        self.assertTrue(len(self.check.ad_cache) > 0)
        # The next run shoudn't throw an exception
        self.run_check(config)

        # Reset the cache now
        self.check.last_ad_cache_ts = 0
        self.assertRaises(Exception, lambda: self.run_check, config)
