# -*- coding: utf-8 -*-

import balrogworker as bw
import unittest
from nose.tools import raises, with_setup
import json
import os


class BalrogworkerTest(unittest.TestCase):
    def test_get_hash(self):
        test_content = "wow. much text. very hash ☺️"
        test_md5 = "d0bfbdf85fac3ccd5a9d9a458bf39ab3"
        assert bw.get_hash(test_content) == test_md5

    def test_get_hash_fail(self):
        test_content = "sometimes i swordfight with pocky ⚔⚔"
        test_md5 = "thisisnot⚔arealhash"
        assert bw.get_hash(test_content) != test_md5

    def test_get_hash_sha512(self):
        test_content = "wow. much text. مرحبا"
        test_sha = "e643580dcb98a8d9a7b95890d12f793baf5ef09a79695003" \
                   "fbcaf3b54c1c96cb56aeccbd360209c5cd234117dea1cc88aa60b2a250dd4858ee1d6847cb7a8c7e"
        assert bw.get_hash(test_content, hash_type="sha512") == test_sha

    def test_possible_names(self):
        initial = "/Users/tester/file.exe"
        names = bw.possible_names(initial, 2)
        exp = ["/Users/tester/file.exe", "/Users/tester/file-1.exe", "/Users/tester/file-2.exe"]
        assert set(names) == set(exp)

    def test_possible_names_neg(self):
        initial = "file.exe"
        names = bw.possible_names(initial, -1)
        exp = ["file.exe"]
        assert set(names) == set(exp)

    def test_verify_task_schema(self):
        test_taskdef = {'payload': {'parent_task_artifacts_url': 500,
                                    'signing_cert': 'nightly'}}
        assert not bw.verify_task_schema(test_taskdef)

    @raises(KeyError)
    def test_verify_task_schema_missing_cert(self):
        test_taskdef = {'payload': {'parent_task_artifacts_url': 500}}
        assert bw.verify_task_schema(test_taskdef)

    @raises(KeyError)
    def test_verify_task_schema_invalid_cert(self):
        test_taskdef = {'payload': {'parent_task_artifacts_url': 500,
                                    'signing_cert': os}}
        assert bw.verify_task_schema(test_taskdef)

    @raises(KeyError)
    def test_verify_task_schema_missing_url(self):
        test_taskdef = {'payload': {'signing_cert': 'release'}}
        assert bw.verify_task_schema(test_taskdef)

    @classmethod
    def setUpClass(cls):
        taskdef = {
            'payload': {
                'parent_task_artifacts_url': 'www.taskcluster.net',
                'signing_cert': 'nightly'
            }
        }
        with open('test_taskdef.json', 'w') as f:
            json.dump(taskdef, f)

    @classmethod
    def tearDownClass(cls):
        os.remove('test_taskdef.json')

    def get_args(self):
        return ["--taskdef", "test_taskdef.json",
                "--balrog-api-root", "TEST_API_ROOT",
                "--balrog-username", "fake balrog user",
                "--balrog-password", "very good passwrod",
                "--s3-bucket", "bucket walrus",
                "--aws-access-key-id", "cocoa butter",
                "--aws-secret-access-key", "shhhhhhhhhhh",
                "--disable-s3"]

    def get_args_processed(self):
        return {
            "taskdef": "test_taskdef.json",
            "api_root": "TEST_API_ROOT",
            "balrog_username": "fake balrog user",
            "balrog_password": "very good passwrod",
            "s3_bucket": "bucket walrus",
            "aws_key_id": "cocoa butter",
            "aws_key_secret": "shhhhhhhhhhh",
            "disable_s3": True,
            "dummy": False,
            "loglevel": 20  # corresponds to default value of logging.INFO
        }

    def get_args_as_environ(self):
        return {
            "BALROG_API_ROOT": "TEST_API_ROOT",
            "BALROG_USERNAME": "fake balrog user",
            "BALROG_PASSWORD": "very good passwrod",
            "S3_BUCKET": "bucket walrus",
            "AWS_ACCESS_KEY_ID": "cocoa butter",
            "AWS_SECRET_ACCESS_KEY": "shhhhhhhhhhh",
        }

    def test_verify_args(self):
        args = vars(bw.verify_args(self.get_args()))
        exp = self.get_args_processed()
        for key in args:
            assert exp[key] == args[key]

    def test_verify_args_from_environ(self):
        os.environ.update(self.get_args_as_environ())

        expected = self.get_args_processed()
        for key, value in vars(bw.verify_args(["--taskdef","test_taskdef.json","--disable-s3"])).iteritems():
            assert expected[key] == value

