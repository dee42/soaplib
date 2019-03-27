#!/usr/bin/env python
#
# soaplib - Copyright (C) Soaplib contributors.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#

import unittest

from zeep import Client
from zeep.exceptions import Error
from datetime import datetime

class TestSuds(unittest.TestCase):
    def setUp(self):
        self.client = Client("http://localhost:9753/?wsdl")
        self.client.default_factory = self.client.type_factory("soaplib.test.interop.server._service")

    def test_echo_simple_boolean_array(self):
        val = [True, False, False, True]
        ret = self.client.service.echo_simple_boolean_array(val)

        assert val == ret

    def test_enum(self):
        DaysOfWeekEnum = self.client.default_factory.DaysOfWeekEnum

        val = DaysOfWeekEnum('Monday')
        ret = self.client.service.echo_enum(val)

        assert val == ret

    def test_validation(self):
        non_nillable_class = self.client.get_type("{hunk.sunk}NonNillableClass")()
        non_nillable_class.i = 6
        non_nillable_class.s = None

        try:
            ret = self.client.service.non_nillable(non_nillable_class)
            raise Exception("must fail")
        except Error as e:
            pass

    def test_echo_integer_array(self):
        ia = self.client.default_factory.integerArray()
        ia.integer.extend([1,2,3,4,5])
        self.client.service.echo_integer_array(ia)

    def test_echo_in_header(self):
        in_header = self.client.default_factory.InHeader(s='a', i=3)

        ret = self.client.service.echo_in_header(_soapheaders=[in_header])

        print(ret)

        self.assertEqual(in_header.s, ret.s)
        self.assertEqual(in_header.i, ret.i)

    def test_send_out_header(self):
        out_header = self.client.default_factory.OutHeader(dt=datetime(year=2000, month=0o1, day=0o1), f= 3.141592653)

        ret = self.client.service.send_out_header()

        self.assertTrue(isinstance(ret,type(out_header)))
        self.assertEqual(ret.dt, out_header.dt)
        self.assertEqual(ret.f, out_header.f)

    def test_echo_string(self):
        test_string = "OK"
        ret = self.client.service.echo_string(test_string)

        self.assertEqual(ret, test_string)

    def __get_xml_test_val(self):
        return {
            "test_sub": {
                "test_subsub1": {
                    "test_subsubsub1" : ["subsubsub1 value"]
                },
                "test_subsub2": ["subsub2 value 1", "subsub2 value 2"],
                "test_subsub3": [
                    {
                        "test_subsub3sub1": ["subsub3sub1 value"]
                    },
                    {
                        "test_subsub3sub2": ["subsub3sub2 value"]
                    },
                ],
                "test_subsub4": [],
                "test_subsub5": ["x"],
            }
        }

    def test_any(self):
        val=self.__get_xml_test_val()
        ret = self.client.service.echo_any(val)

        self.assertEqual(ret, val)

    def test_any_as_dict(self):
        val=self.__get_xml_test_val()
        ret = self.client.service.echo_any_as_dict(val)

        self.assertEqual(ret, val)

    def test_echo_simple_class(self):
        val = self.client.default_factory.SimpleClass(i=45, s="asd")

        ret = self.client.service.echo_simple_class(val)

        assert ret.i == val.i
        assert ret.s == val.s

    def test_echo_nested_class(self):
        val = self.client.get_type("{punk.tunk}NestedClass")()

        val.i = 45
        val.s = "asd"
        val.f = 12.34
        val.ai = self.client.default_factory.integerArray()
        val.ai.integer.extend([1,2,3,45,5,3,2,1,4])

        val.simple = self.client.default_factory.SimpleClassArray()

        val.simple.SimpleClass.append(self.client.default_factory.SimpleClass(i=45,s="asd"))
        val.simple.SimpleClass.append(self.client.default_factory.SimpleClass(i=12,s="qwe"))

        val.other = self.client.default_factory.OtherClass(
            dt = datetime.now(),
            d = 123.456,
            b = True)

        ret = self.client.service.echo_nested_class(val)



        self.assertEqual(ret.i, val.i)
        self.assertEqual(ret.ai[0], val.ai[0])
        self.assertEqual(ret.simple.SimpleClass[0].s, val.simple.SimpleClass[0].s)
        self.assertEqual(ret.other.dt, val.other.dt)


    def test_echo_extension_class(self):
        service_name = "echo_extension_class"
        val = self.client.get_type("{bar}ExtensionClass")()

        val.i = 45
        val.s = "asd"
        val.f = 12.34

        val.simple = self.client.default_factory.SimpleClassArray()

        val.simple.SimpleClass.append(self.client.default_factory.SimpleClass(i=45, s="asd"))
        val.simple.SimpleClass.append(self.client.default_factory.SimpleClass(i=12, s="qwe"))

        val.other = self.client.default_factory.OtherClass(
            dt = datetime.now(),
            d = 123.456,
            b = True)

        val.p = self.client.get_type("{hunk.sunk}NonNillableClass")()
        val.p.dt = datetime(2010,0o6,0o2)
        val.p.i = 123
        val.p.s = "punk"

        val.l = datetime(2010,0o7,0o2)
        val.q = 5

        ret = self.client.service.echo_extension_class(val)
        print(ret)

        self.assertEqual(ret.i, val.i)
        self.assertEqual(ret.s, val.s)
        self.assertEqual(ret.f, val.f)
        self.assertEqual(ret.simple.SimpleClass[0].i, val.simple.SimpleClass[0].i)
        self.assertEqual(ret.other.dt, val.other.dt)
        self.assertEqual(ret.p.s, val.p.s)


    def test_complex_return(self):
        ret = self.client.service.complex_return()

        self.assertEqual(ret.resultCode, 1)
        self.assertEqual(ret.resultDescription, "Test")
        self.assertEqual(ret.transactionId, 123)
        self.assertEqual(ret.roles.role[0], "MEMBER")

if __name__ == '__main__':
    unittest.main()
