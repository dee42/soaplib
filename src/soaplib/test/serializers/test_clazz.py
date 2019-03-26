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

import datetime
import unittest

from soaplib.serializers.clazz import ClassSerializer
from soaplib.serializers.clazz import Array

from soaplib.serializers.primitive import DateTime
from soaplib.serializers.primitive import Float
from soaplib.serializers.primitive import Integer
from soaplib.serializers.primitive import String

from lxml import etree

ns_test = 'test_namespace'

class Address(ClassSerializer):
    street = String
    city = String
    zip = Integer
    since = DateTime
    lattitude = Float
    longitude = Float

Address.resolve_namespace(Address,__name__)

class Person(ClassSerializer):
    name = String
    birthdate = DateTime
    age = Integer
    addresses = Array(Address)
    titles = Array(String)

Person.resolve_namespace(Person,__name__)

class Employee(Person):
    employee_id = Integer
    salary = Float

Employee.resolve_namespace(Employee,__name__)

class Level2(ClassSerializer):
    arg1 = String
    arg2 = Float

Level2.resolve_namespace(Level2, __name__)

class Level3(ClassSerializer):
    arg1 = Integer

Level3.resolve_namespace(Level3, __name__)

class Level4(ClassSerializer):
    arg1 = String

Level4.resolve_namespace(Level4, __name__)

class Level1(ClassSerializer):
    level2 = Level2
    level3 = Array(Level3)
    level4 = Array(Level4)

Level1.resolve_namespace(Level1, __name__)

class TestClassSerializer(unittest.TestCase):
    def test_simple_class(self):
        a = Address()
        a.street = '123 happy way'
        a.city = 'badtown'
        a.zip = 32
        a.lattitude = 4.3
        a.longitude = 88.0

        element = etree.Element('test')
        Address.to_xml(a, ns_test, element)
        element = element[0]
        self.assertEqual(6, len(element.getchildren()))

        r = Address.from_xml(element)

        self.assertEqual(a.street, r.street)
        self.assertEqual(a.city, r.city)
        self.assertEqual(a.zip, r.zip)
        self.assertEqual(a.lattitude, r.lattitude)
        self.assertEqual(a.longitude, r.longitude)
        self.assertEqual(a.since, r.since)

    def test_nested_class(self): # FIXME: this test is incomplete
        p = Person()
        element = etree.Element('test')
        Person.to_xml(p, ns_test, element)
        element = element[0]

        self.assertEqual(None, p.name)
        self.assertEqual(None, p.birthdate)
        self.assertEqual(None, p.age)
        self.assertEqual(None, p.addresses)

    def test_class_array(self):
        peeps = []
        names = ['bob', 'jim', 'peabody', 'mumblesleves']
        for name in names:
            a = Person()
            a.name = name
            a.birthdate = datetime.datetime(1979, 1, 1)
            a.age = 27
            peeps.append(a)

        serializer = Array(Person)
        serializer.resolve_namespace(serializer,__name__)

        element = etree.Element('test')
        serializer.to_xml(peeps, ns_test, element)
        element = element[0]

        self.assertEqual(4, len(element.getchildren()))

        peeps2 = serializer.from_xml(element)
        for i in range(0, 4):
            self.assertEqual(peeps2[i].name, names[i])
            self.assertEqual(peeps2[i].birthdate,
                datetime.datetime(1979, 1, 1))

    def test_class_nested_array(self):
        peeps = []
        names = ['bob', 'jim', 'peabody', 'mumblesleves']

        for name in names:
            a = Person()
            a.name = name
            a.birthdate = datetime.datetime(1979, 1, 1)
            a.age = 27
            a.addresses = []

            for i in range(0, 25):
                addr = Address()
                addr.street = '555 downtown'
                addr.city = 'funkytown'
                a.addresses.append(addr)
            peeps.append(a)

        serializer = Array(Person)
        serializer.resolve_namespace(serializer,__name__)
        element = etree.Element('test')
        serializer.to_xml(peeps, ns_test, element)
        element = element[0]

        self.assertEqual(4, len(element.getchildren()))

        peeps2 = serializer.from_xml(element)
        for peep in peeps2:
            self.assertEqual(27, peep.age)
            self.assertEqual(25, len(peep.addresses))
            self.assertEqual('funkytown', peep.addresses[18].city)

    def test_complex_class(self):
        l = Level1()
        l.level2 = Level2()
        l.level2.arg1 = 'abcd'
        l.level2.arg2 = 1.444
        l.level3 = []
        l.level4 = []

        for i in range(0, 100):
            a = Level3()
            a.arg1 = i
            l.level3.append(a)

        for i in range(0, 4):
            a = Level4()
            a.arg1 = str(i)
            l.level4.append(a)

        element = etree.Element('test')
        Level1.to_xml(l, ns_test, element)
        element = element[0]
        l1 = Level1.from_xml(element)

        self.assertEqual(l1.level2.arg1, l.level2.arg1)
        self.assertEqual(l1.level2.arg2, l.level2.arg2)
        self.assertEqual(len(l1.level4), len(l.level4))
        self.assertEqual(100, len(l.level3))

    def test_customize(self):
        class Base(ClassSerializer):
            class Attributes(ClassSerializer.Attributes):
                prop1=3
                prop2=6

        Base2 = Base.customize(prop1=4)

        self.assertNotEqual(Base.Attributes.prop1, Base2.Attributes.prop1)
        self.assertEqual(Base.Attributes.prop2, Base2.Attributes.prop2)

        class Derived(Base):
            class Attributes(Base.Attributes):
                prop3 = 9
                prop4 = 12

        Derived2 = Derived.customize(prop1=5, prop3=12)

        self.assertEqual(Base.Attributes.prop1, 3)
        self.assertEqual(Base2.Attributes.prop1, 4)

        self.assertEqual(Derived.Attributes.prop1, 3)
        self.assertEqual(Derived2.Attributes.prop1, 5)

        self.assertNotEqual(Derived.Attributes.prop3, Derived2.Attributes.prop3)
        self.assertEqual(Derived.Attributes.prop4, Derived2.Attributes.prop4)

        Derived3 = Derived.customize(prop3=12)
        Base.prop1 = 4

        # changes made to bases propagate, unless overridden
        self.assertEqual(Derived.Attributes.prop1, Base.Attributes.prop1)
        self.assertNotEqual(Derived2.Attributes.prop1, Base.Attributes.prop1)
        self.assertEqual(Derived3.Attributes.prop1, Base.Attributes.prop1)

if __name__ == '__main__':
    unittest.main()
