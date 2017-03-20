# SVD module
from lxml import etree as et

arights = ('read-only', 'read-write', 'write-only', 'writeOnce', 'read-writeOnce')

__version__ = '1.0.1'

default_xml = ('<device><name>NEW_DEVICE</name>'
               '<version>1.0</version>'
               '<description>Default CMSIS device</description>'
               '<addressUnitBits>8</addressUnitBits>'
               '<width>32</width>'
               '<size>0x20</size>'
               '<access>read-write</access>'
               '<resetValue>0x00000000</resetValue>'
               '<resetMask>0xFFFFFFFF</resetMask>'
               '<peripherals><peripheral>'
               '<name>NEW_PERIPHERAL</name>'
               '<groupName>DEVICE PERIPHERALS</groupName>'
               '<baseAddress>0xDEADBEEF</baseAddress>'
               '<addressBlock><offset>0x00</offset><size>0x400</size><usage>registers</usage></addressBlock>'
               '<interrupt><name>NEW_INTERRUPT</name><description>Default interrupt</description><value>1</value></interrupt>'
               '<registers><register>'
               '<name>NEW_REGISTER</name><displayName>NEW_REGISTER</displayName>'
               '<description>Default register</description>'
               '<addressOffset>0x00</addressOffset>'
               '<fields><field><name>NEW_BITFIELD</name><description>Default bitfield</description>'
               '<bitOffset>0</bitOffset><bitWidth>1</bitWidth></field></fields>'
               '</register></registers>'
               '</peripheral></peripherals></device>'
               )


def str_cleanup(s):
    try:
        s = s.encode('ascii', errors='ignore')
        return ' '.join(s.split())
    except:
        return None


def toInt(val, fault=None):
    try:
        return int(val, 0)
    except:
        return fault


def get_from_xml(node, attr):
    try:
        return node.find(attr).text
    except:
        return None


class basedata(object):
    def __init__(self, parent=None):
        self.parent = parent
        self._name = 'new'
        self._desc = None
        self._rsize = None
        self.rvalue = None
        self._access = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        try:
            s = val.encode('ascii', errors='ignore')
            self._name = '_'.join(s.split())
        except:
            pass

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, val):
        self._desc = str_cleanup(val)

    @property
    def access(self):
        return self._access

    @access.setter
    def access(self, val):
        self._access = val if val in arights else None

    @property
    def rsize(self):
        return '0x{0:02X}'.format(self._rsize) if self._rsize else None

    @rsize.setter
    def rsize(self, val):
        self._rsize = toInt(val)

    @property
    def vsize(self):
        if self._rsize:
            return self.rsize
        else:
            if self.parent:
                return self.parent.vsize
            else:
                return 0

    @property
    def vvalue(self):
        if self.rvalue:
            return self.rvalue
        else:
            if self.parent:
                return self.parent.vvalue
            else:
                return None

    @property
    def vaccess(self):
        if self.access:
            return self.access
        else:
            if self.parent:
                return self.parent.vaccess
            else:
                return 'undefined'


class field(basedata):
    def __init__(self, parent, xml=None):
        basedata.__init__(self, parent)
        self._bitw = 1
        self._bito = 0
        if xml is not None:
            self.fromXML(xml)

    @property
    def bitw(self):
        return str(self._bitw)

    @bitw.setter
    def bitw(self, val):
        self._bitw = toInt(val, self._bitw)

    @property
    def bito(self):
        return str(self._bito)

    @bito.setter
    def bito(self, val):
        self._bito = toInt(val, self._bito)

    @property
    def valid(self):
        if self.name and self.desc and self.bito and self.bitw:
            if (self._bito + self._bitw) <= int(self.vsize, 0):
                return True
        return False

    def fromXML(self, node):
        self.name = get_from_xml(node, 'name')
        self.desc = get_from_xml(node, 'description')
        self.bitw = get_from_xml(node, 'bitWidth')
        self.bito = get_from_xml(node, 'bitOffset')
        self.access = get_from_xml(node, 'access')

    def toXML(self, node=None):
        if node is None:
            node = et.Element('field')
        et.SubElement(node, 'name').text = self.name
        if self.desc:
            et.SubElement(node, 'description').text = self.desc
        et.SubElement(node, 'bitOffset').text = self.bito
        et.SubElement(node, 'bitWidth').text = self.bitw
        if self.access:
            et.SubElement(node, 'access').text = self.access
        return node


class register(basedata):
    def __init__(self, parent, xml=None):
        basedata.__init__(self, parent)
        self._dispname = None
        self._offset = 0
        self.fields = []
        if xml is not None:
            self.fromXML(xml)

    @property
    def dispname(self):
        return self._dispname

    @dispname.setter
    def dispname(self, val):
        self._dispname = str_cleanup(val)

    @property
    def offset(self):
        return '0x{0:04X}'.format(self._offset)

    @offset.setter
    def offset(self, val):
        self._offset = toInt(val, self._offset)

    @property
    def valid(self):
        return (self.name and self.desc)

    def fromXML(self, node):
        del self.fields[:]
        self.name = get_from_xml(node, 'name')
        self.dispname = get_from_xml(node, 'displayName')
        self.desc = get_from_xml(node, 'description')
        self.offset = get_from_xml(node, 'addressOffset')
        self.rsize = get_from_xml(node, 'size')
        self.rvalue = get_from_xml(node, 'resetValue')
        self.access = get_from_xml(node, 'access')
        for x in node.findall('./fields/field'):
            self.fields.append(field(self, x))
        self.sortField()

    def toXML(self, node=None):
        if node is None:
            node = et.Element('register')
        et.SubElement(node, 'name').text = self.name
        if self.dispname:
            et.SubElement(node, 'displayName').text = self.dispname
        if self.desc:
            et.SubElement(node, 'description').text = self.desc
        et.SubElement(node, 'addressOffset').text = self.offset
        if self.rsize:
            et.SubElement(node, 'size').text = self.rsize
        if self.access:
            et.SubElement(node, 'access').text = self.access
        if self.rvalue:
            et.SubElement(node, 'resetValue').text = self.rvalue
        if self.fields:
            f = et.SubElement(node, 'fields')
            for x in self.fields:
                x.toXML(et.SubElement(f, 'field'))
        return node

    def newField(self, name=''):
        r = 0
        for x in sorted(self.fields, key=lambda x: x._bito, reverse=False):
            if r < x._bito:
                break
            r = x._bito + x._bitw
        if r < int(self.vsize, 0):
            f = field(self)
            f._bito = r
            if name:
                f.name = name
            return f
        else:
            return None

    def addField(self, field):
        field.parent = self
        self.fields.append(field)
        self.sortField()

    def sortField(self):
        self.fields.sort(key=lambda x: x._bito, reverse=True)

    def delField(self, item):
        self.fields.remove(item)

    def validate(self, callback):
        names = []
        cap = int(self.vsize, 0)
        ofs = 0
        for x in sorted(self.fields, key=lambda x: x._bito):
            if x.name in names:
                if callback('Duplicated bitfield name %s in %s' % (x.name, self.name)):
                    return True
            elif x._bito + x._bitw > cap:
                if callback('Bitfield %s is out of bounds in %s' % (x.name, self.name)):
                    return True
            elif ofs > x._bito:
                if callback('Bitfields %s and %s overlapped in %s' % (x.name, names[-1], self.name)):
                    return True
            elif x.vaccess == 'undefined':
                if callback('Undefined access level for %s in %s' % (x.name, self.name)):
                    return True
            else:
                names.append(x.name)
                ofs = x._bito + x._bitw
        return False


class interrupt(basedata):
    def __init__(self, parent, xml=None):
        basedata.__init__(self, parent)
        self._value = 0
        if xml is not None:
            self.fromXML(xml)

    @property
    def value(self):
        return str(self._value)

    @value.setter
    def value(self, val):
        self._value = toInt(val, self._value)

    @property
    def valid(self):
        return (self.name and self.desc)

    def fromXML(self, node):
        self.name = get_from_xml(node, 'name')
        self.desc = get_from_xml(node, 'description')
        self.value = get_from_xml(node, 'value')

    def toXML(self, node=None):
        if node is None:
            node = et.Element('interrupt')
        et.SubElement(node, 'name').text = self.name
        if self.desc:
            et.SubElement(node, 'description').text = self.desc
        et.SubElement(node, 'value').text = self.value
        return node


class peripheral(basedata):
    def __init__(self, parent, xml=None):
        basedata.__init__(self, parent)
        self.ref = None
        self.group = None
        self._address = 0
        self._aoffset = 0
        self._asize = 0x400
        self.interrupts = []
        self.registers = []
        if xml is not None:
            self.fromXML(xml)

    @property
    def asize(self):
        return '0x{0:04X}'.format(self._asize)

    @asize.setter
    def asize(self, val):
        self._asize = toInt(val, self._asize)

    @property
    def aoffset(self):
        return '0x{0:08X}'.format(self._aoffset)

    @aoffset.setter
    def aoffset(self, val):
        self._aoffset = toInt(val, self._aoffset)

    @property
    def address(self):
        return '0x{0:08X}'.format(self._address)

    @address.setter
    def address(self, val):
        self._address = toInt(val, self._address)

    def fromXML(self, node):
        del self.interrupts[:]
        del self.registers[:]
        self.name = get_from_xml(node, 'name')
        if 'derivedFrom' in node.attrib:
            ref = node.attrib['derivedFrom']
            for x in self.parent.peripherals:
                if x.name == ref:
                    self.ref = x
                    break
        else:
            self.ref = None
        self.desc = get_from_xml(node, 'description')
        self.group = get_from_xml(node, 'groupName')
        self.address = get_from_xml(node, 'baseAddress')
        self.aoffset = get_from_xml(node, './addressBlock/offset')
        self.asize = get_from_xml(node, './addressBlock/size')

        for x in node.findall('./interrupt'):
            self.interrupts.append(interrupt(self, x))

        for x in node.findall('./registers/register'):
            self.registers.append(register(self, x))
        self.registers.sort(key=lambda x: x._offset, reverse=False)

    def toXML(self, node=None):
        if node is None:
            node = et.Element('peripheral')
        if self.ref:
            node.set('derivedFrom', self.ref.name)
        et.SubElement(node, 'name').text = self.name
        if self.group:
            et.SubElement(node, 'groupName').text = self.group
        if self.desc:
            et.SubElement(node, 'description').text = self.desc
        et.SubElement(node, 'baseAddress').text = self.address

        a = et.SubElement(node, 'addressBlock')
        et.SubElement(a, 'offset').text = self.aoffset
        et.SubElement(a, 'size').text = self.asize
        et.SubElement(a, 'usage').text = 'registers'

        for x in self.interrupts:
            x.toXML(et.SubElement(node, 'interrupt'))
        if self.registers:
            r = et.SubElement(node, 'registers')
            for x in self.registers:
                x.toXML(et.SubElement(r, 'register'))
        return node

    def newRegister(self, name=''):
        o = 0
        sz = int(self.vsize, 0) / 8
        for x in sorted(self.registers, key=lambda x: x._offset, reverse=False):
            if o < x._offset:
                break
            o = x._offset + sz
        if o < self._asize:
            r = register(self)
            r._offset = o
            if name:
                r.name = name
            return r
        else:
            return None

    def setRef(self, ref):
        if ref:
            for x in self.parent.peripherals:
                if x == self:
                    return False
                if x.name == ref:
                    self.ref = x
                    return True
            return False
        else:
            self.ref = None
            return True

    def addRegister(self, item):
        item.parent = self
        self.registers.append(item)
        self.registers.sort(key=lambda x: x._offset, reverse=False)

    def delRegister(self, item):
        self.registers.remove(item)

    def newInterrupt(self, name=''):
        ni = interrupt(self)
        if name:
            ni.name = name
        return ni

    def addInterrupt(self, reg):
        if not next((i for i in self.interrupts if i.value == reg.value), None):
            self.interrupts.append(reg)

    def delInterrupt(self, item):
        self.interrupts.remove(item)

    def validate(self, callback):
        names = []
        ofs = 0
        for x in sorted(self.registers, key=lambda x: x._offset, reverse=False):
            rsize = int(x.vsize, 0) / 8
            if x.name in names:
                if callback('Duplicated register name %s in %s' % (x.name, self.name)):
                    return True
            elif x._offset < ofs:
                if callback('Registers %s and %s in %s is overlapped' % (x.name, names[-1], self.name)):
                    return True
            elif x._offset + rsize > self._asize:
                if callback('Register %s is out of bounds in %s' % (x.name, self.name)):
                    return True
            elif x.vaccess == 'undefined':
                if callback('Undefined access level for %s in %s' % (x.name, self.name)):
                    return True
            else:
                if x.validate(callback):
                    return True
                names.append(x.name)
                ofs = x._offset + rsize
        return False


class device(basedata):
    def __init__(self, xml=None):
        basedata.__init__(self, None)
        self.vendor = None
        self.width = '32'
        self.rsize = '0x20'
        self.rvalue = '0x00000000'
        self.rmask = '0xFFFFFFFF'
        self.access = 'read-write'
        self.peripherals = []
        if xml is not None:
            self.fromXML(xml)

    def fromString(self, str):
        xml = et.fromstring(str)
        self.fromXML(xml)

    def fromXML(self, node):
        del self.peripherals[:]
        self.vendor = get_from_xml(node, 'vendor')
        self.name = get_from_xml(node, 'name')
        self.desc = get_from_xml(node, 'description')
        self.width = get_from_xml(node, 'width')
        self.rsize = get_from_xml(node, 'size')
        self.access = get_from_xml(node, 'access')
        self.rvalue = get_from_xml(node, 'resetValue')
        self.rmask = get_from_xml(node, 'resetMask')
        for x in node.findall('./peripherals/peripheral'):
            self.peripherals.append(peripheral(self, x))

    def toXML(self, node=None):
        if node is None:
            node = et.Element('export_device')
        if self.vendor:
            et.SubElement(node, 'vendor').text = self.vendor
        et.SubElement(node, 'name').text = self.name
        et.SubElement(node, 'version').text = '1.0'
        et.SubElement(node, 'description').text = self.desc
        et.SubElement(node, 'addressUnitBits').text = '8'
        et.SubElement(node, 'width').text = self.width
        et.SubElement(node, 'size').text = self.rsize
        et.SubElement(node, 'access').text = self.access
        et.SubElement(node, 'resetValue').text = self.rvalue
        et.SubElement(node, 'resetMask').text = self.rmask
        p = et.SubElement(node, 'peripherals')
        for per in self.peripherals:
            per.toXML(et.SubElement(p, 'peripheral'))
        return node

    def newPeripheral(self, name=''):
        p = peripheral(self)
        p.name = name
        return p

    def delPeripheral(self, item):
        self.peripherals.remove(item)

    def addPeripheral(self, item):
        item.parent = self
        self.peripherals.append(item)

    def movePeripheral(self, dest, item):
        uindex = 1 + self.peripherals.index(dest)
        iindex = self.peripherals.index(item)
        if iindex != uindex:
            self.peripherals.insert(uindex, self.peripherals.pop(iindex))

    def validate(self, callback):
        names = []
        vectors = []
        ofs = 0
        for x in sorted(self.peripherals, key=lambda x: x._address + x._aoffset):
            if x.name in names:
                if callback('Duplicated peripheral name %s' % (x.name)):
                    return True
            if ofs > x._address + x._aoffset:
                if callback('Peripherals %s and %s is overlapped' % (x.name, names[-1])):
                    return True
            if x.validate(callback):
                return True
            names.append(x.name)
            ofs = x._address + x._aoffset + x._asize
            for i in x.interrupts:
                if i.value in vectors:
                    if callback('Duplicated interrupt vector %s' % (i.name)):
                        return True
                vectors.append(i.value)
        return False

    def load(self, name):
        xml = et.parse(name)
        self.fromXML(xml)

    def save(self, name):
        xs = 'http://www.w3.org/2001/XMLSchema-instance'
        xml = et.Element('device', schemaVersion='1.1',
                         nsmap={'xs': xs},
                         attrib={'{' + xs + '}noNamespaceSchemaLocation': 'CMSIS-SVD_Schema_1_1.xsd'})
        xml.addprevious(et.Comment('generated by SVD editor ' + __version__))
        self.toXML(xml)
        tree = et.ElementTree(xml)
        tree.write(name, encoding='utf-8', xml_declaration=True, standalone=True, pretty_print=True)
