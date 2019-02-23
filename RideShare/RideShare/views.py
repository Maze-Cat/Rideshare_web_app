#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 vcm <vcm@vcm-5947.vm.duke.edu>
#
# Distributed under terms of the MIT license.

"""

"""
from django.shortcuts import redirect
def login_redirect(request):
    return redirect('/account/home')
