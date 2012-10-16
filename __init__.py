#This file is part sale_discount module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from trytond.pool import Pool
from move import *
from sale import *


def register():
    Pool.register(
        SaleLine,
        Move,
        module='sale_discount', type_='model')
