#!/usr/bin/env python3
#
# Copyright (C) 2021 IBM Corporation.
#
# Authors:
# Frederico Araujo <frederico.araujo@ibm.com>
# Teryl Taylor <terylt@ibm.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# -------------------------------------------------------------------------------
#
# Helper for periodic task execution
#
# Instructions:
#      ./gitops -h for help and command line options
#
#
# -------------------------------------------------------------------------------
#
import threading, time


class PeriodicExecutor(threading.Thread):
    """Periodic task executor"""

    def __init__(self, sleep, func, params):
        """execute func(params) every 'sleep' seconds"""
        self.func = func
        self.params = params
        self.sleep = sleep
        threading.Thread.__init__(self, name="PeriodicExecutor")
        self.setDaemon(1)

    def run(self):
        while 1:
            self.func(*self.params)
            time.sleep(self.sleep)
