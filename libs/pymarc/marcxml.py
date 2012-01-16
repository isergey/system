# encoding: utf-8
"pymarc marcxml file."

from xml.sax import make_parser
from xml.sax.handler import ContentHandler, feature_namespaces
import re



try:
    import xml.etree.cElementTree as ET  
except ImportError:
    import elementtree.ElementTree as ET

from record import Record
from field import Field
from marc8 import MARC8ToUnicode

XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
MARC_XML_NS = "http://www.loc.gov/MARC21/slim"
MARC_XML_SCHEMA = "http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd"


RE_XML_ILLEGAL = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
                 u'|' + \
                 u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                  (unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                   unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                   unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff))

def replace_illegal(xml_string):
        return re.sub(RE_XML_ILLEGAL, " ", xml_string)

class XmlHandler(ContentHandler):
    """
    You can subclass XmlHandler and add your own process_record 
    method that'll be passed a pymarc.Record as it becomes 
    available. This could be useful if you want to stream the 
    records elsewhere (like to a rdbms) without having to store 
    them all in memory.
    """

    def __init__(self, strict=False):
        self.records = []
        self._record = None
        self._field = None
        self._subfield_code = None
        self._text = []
        self._strict = strict

    def startElementNS(self, name, qname, attrs):
        if self._strict and name[0] != MARC_XML_NS:
            return

        element = name[1]
        self._text = []

        if element == 'record':
            self._record = Record()
        elif element == 'controlfield':
            tag = attrs.getValue((None, u'tag'))
            self._field = Field(tag)
        elif element == 'datafield':
            tag = attrs.getValue((None, u'tag'))
            ind1 = attrs.getValue((None, u'ind1'))
            ind2 = attrs.getValue((None, u'ind2'))
            self._field = Field(tag, [ind1, ind2])
        elif element == 'subfield':
            self._subfield_code = attrs[(None, 'code')]

    def endElementNS(self, name, qname):
        if self._strict and name[0] != MARC_XML_NS:
            return

        element = name[1]
        text = u''.join(self._text)

        if element == 'record':
            self.process_record(self._record)
            self._record = None
        elif element == 'leader':
            self._record.leader = text
        elif element == 'controlfield':
            self._field.data = text
            self._record.add_field(self._field)
            self._field = None
        elif element == 'datafield':
            self._record.add_field(self._field)
            self._field = None
        elif element == 'subfield':
            self._field.subfields.append(self._subfield_code)
            self._field.subfields.append(text)
            self._subfield_code = None

        self._text = []

    def characters(self, chars):
        self._text.append(chars)

    def process_record(self, record):
        self.records.append(record)


def parse_xml(xml_file, handler):
    """
    parse a file with a given subclass of xml.sax.handler.ContentHandler
    """
    parser = make_parser()
    parser.setContentHandler(handler)
    parser.setFeature(feature_namespaces, 1)
    parser.parse(xml_file)


def map_xml(function, *files):
    """
    map a function onto the file, so that for each record that is
    parsed the function will get called with the extracted record

    def do_it(r):
      print r

    map_xml(do_it, 'marc.xml')
    """
    handler = XmlHandler()
    handler.process_record = function
    for xml_file in files:
        parse_xml(xml_file, handler)


def parse_xml_to_array(xml_file, strict=False):
    """
    parse an xml file and return the records as an array. If you would
    like the parser to explicitly check the namespaces for the MARCSlim
    namespace use the strict=True option.
    """
    handler = XmlHandler(strict)
    parse_xml(xml_file, handler)
    return handler.records


def record_to_xml(record, quiet=False, namespace=False):
    """
    converts a record object to a chunk of xml

    # include the marcxml namespace in the root tag (default: False)
    record_to_xml(record, namespace=True)
    """
    # helper for converting non-unicode data to unicode
    # TODO: maybe should set g0 and g1 appropriately using 066 $a and $b?

    #    marc8 = MARC8ToUnicode(quiet=quiet)
    #    def translate(data):
    #        if type(data) == unicode:
    #            return data
    #        else:
    #            return marc8.translate(data)

    root = ET.Element('record')
    if namespace:
        root.set('xmlns', MARC_XML_NS)
        root.set('xmlns:xsi', XSI_NS)
        root.set('xsi:schemaLocation', MARC_XML_SCHEMA)
    leader = ET.SubElement(root, 'leader')
    leader.text = record.leader
    for field in record:
        if field.is_control_field():
            control_field = ET.SubElement(root, 'controlfield')
            control_field.set('tag', field.tag)
            control_field.text = field.data
        else:
            data_field = ET.SubElement(root, 'datafield')
            data_field.set('tag', field.tag)
            data_field.set('ind1', field.indicators[0])
            data_field.set('ind2', field.indicators[1])
            for subfield in field:
                data_subfield = ET.SubElement(data_field, 'subfield')
                data_subfield.set('code', subfield[0])
                data_subfield.text = subfield[1]

    return replace_illegal(''.join(ET.tostringlist(root, encoding='utf-8')))


def record_to_json(record, syntax=u'1.2.840.10003.5.28'):
    print record.fields
    record_dict = {
        'syntax': syntax,
        'leader': record.leader,
        'controlfields': [],
        'datafields': []
    }

    for field in record:
        if field.is_control_field():
            record_dict['controlfields'].append({'tag': field.tag, 'data': field.data})

        elif field.tag[0] == '4':
            field_dict = {
                'tag': field.tag,
                'i1': field.indicator1,
                'i2': field.indicator2,
                'subfields': []
            }

            for subfield in field:
                subfield_dict = {
                    'code': subfield[0],
                    'datafields': []
                }
                if isinstance(subfield[1], Field):
                    inner_field = subfield[1]
                    inner_field_dict = {
                        'tag': inner_field.tag,
                        'i1': inner_field.indicators[0],
                        'i2': inner_field.indicators[1],
                        'subfields': []
                    }
                    for inner_subfield in inner_field:
                        inner_field_dict['subfields'].append(
                                {
                                'code': inner_subfield[0],
                                'data': inner_subfield[1]
                            }
                        )
                    subfield_dict['datafields'].append(inner_field_dict)
                field_dict['subfields'].append(subfield_dict)
            record_dict['datafields'].append(field_dict)
        else:
            field_dict = {
                'tag': field.tag,
                'i1': field.indicator1,
                'i2': field.indicator2,
                'subfields': []
            }

            for subfield in field:
                field_dict['subfields'].append(
                        {
                        'code': subfield[0],
                        'data': subfield[1]
                    }
                )
            record_dict['datafields'].append(field_dict)
    return record_dict


def record_to_dict(record, syntax=u'1.2.840.10003.5.28'):
    record_dict = {
        'syntax': syntax,
        'leader': record.leader,
        'controlfields': {},
        'datafields': {}
    }

    for field in record:
        if field.is_control_field():
            print 'c', field.tag, field.data
            record_dict['controlfields'][field.tag] = field.data

        elif field.tag[0] == '4':
            if field.tag not in record_dict['datafields']:
                record_dict['datafields'][field.tag] = []

            field_dict = {
                'i1': field.indicator1,
                'i2': field.indicator2,
                'subfields': {}
            }

            for subfield in field:
                if not isinstance(subfield[1], Field): continue

                inner_field = subfield[1]

                if subfield[0] not in field_dict['subfields']:
                    field_dict['subfields'][subfield[0]] = {'datafields': []}

                if inner_field.tag not in field_dict['subfields'][subfield[0]]['datafields']:
                    field_dict['subfields'][subfield[0]]['datafields'] = { inner_field.tag: [] }

                inner_field_dict = {
                    'i1': field.indicator1,
                    'i2': field.indicator2,
                    'subfields': {}
                }
                for inner_subfield in inner_field:
                    if inner_subfield[0] not in inner_field_dict['subfields']:
                        inner_field_dict['subfields'][inner_subfield[0]] = []

                    inner_field_dict['subfields'][inner_subfield[0]].append(inner_subfield[1])

                field_dict['subfields'][subfield[0]]['datafields'][inner_field.tag].append(inner_field_dict)

            record_dict['datafields'][field.tag].append(field_dict)

        else:
            if field.tag not in record_dict['datafields']:
                record_dict['datafields'][field.tag] = []

            field_dict = {
                'i1': field.indicator1,
                'i2': field.indicator2,
                'subfields': {}
            }

            for subfield in field:
                if subfield[0] not in field_dict['subfields']:
                    field_dict['subfields'][subfield[0]] = []

                field_dict['subfields'][subfield[0]].append(subfield[1])

            record_dict['datafields'][field.tag].append(field_dict)
    return record_dict


def record_to_rustam_xml(record, syntax='1.2.840.10003.5.28', quiet=False, namespace=False):
    """
    converts a record object to a chunk of xml

    # include the marcxml namespace in the root tag (default: False)
    record_to_xml(record, namespace=True)
    """
    # helper for converting non-unicode data to unicode
    # TODO: maybe should set g0 and g1 appropriately using 066 $a and $b?
    #    marc8 = MARC8ToUnicode(quiet=quiet)
    #    def translate(data):
    #        if type(data) == unicode:
    #            return data
    #        else:
    #            return marc8.translate(data)

    root = ET.Element('record')
    root.set('syntax', syntax)
    #    if namespace:
    #        root.set('xmlns', MARC_XML_NS)
    #        root.set('xmlns:xsi', XSI_NS)
    #        root.set('xsi:schemaLocation', MARC_XML_SCHEMA)
    leader = ET.SubElement(root, 'leader')
    #leader.text = record.leader
    length = ET.SubElement(leader, 'length')
    length.text = record.leader[0:5]

    status = ET.SubElement(leader, 'status')
    status.text = record.leader[5]

    type = ET.SubElement(leader, 'type')
    type.text = record.leader[6]

    leader07 = ET.SubElement(leader, 'leader07')
    leader07.text = record.leader[7]

    leader08 = ET.SubElement(leader, 'leader08')
    leader08.text = record.leader[8]

    leader09 = ET.SubElement(leader, 'leader09')
    leader09.text = record.leader[9]

    indicatorCount = ET.SubElement(leader, 'indicatorCount')
    indicatorCount.text = record.leader[10]

    identifierLength = ET.SubElement(leader, 'identifierLength')
    identifierLength.text = record.leader[11]

    dataBaseAddress = ET.SubElement(leader, 'dataBaseAddress')
    dataBaseAddress.text = record.leader[12:17]

    leader17 = ET.SubElement(leader, 'leader17')
    leader17.text = record.leader[17]

    leader18 = ET.SubElement(leader, 'leader18')
    leader18.text = record.leader[18]

    leader19 = ET.SubElement(leader, 'leader19')
    leader19.text = record.leader[19]

    entryMap = ET.SubElement(leader, 'entryMap')
    entryMap.text = record.leader[20:24]

    for field in record:
        if field.is_control_field():
            control_field = ET.SubElement(root, 'field')
            control_field.set('id', field.tag)
            control_field.text = field.data
        elif field.tag[0] == '4':
            data_field = ET.SubElement(root, 'field')
            data_field.set('id', field.tag)

            ind1 = ET.SubElement(data_field, 'indicator')
            ind1.set('id', '1')
            ind1.text = field.indicators[0]

            ind2 = ET.SubElement(data_field, 'indicator')
            ind2.set('id', '2')
            ind2.text = field.indicators[1]

            for subfield in field:
                data_subfield = ET.SubElement(data_field, 'subfield')
                data_subfield.set('id', subfield[0])
                #data_subfield.text = translate(subfield[1])
                if isinstance(subfield[1], Field):
                    inner_field = subfield[1]

                    inner_data_field = ET.SubElement(data_subfield, 'field')
                    inner_data_field.set('id', inner_field.tag)

                    if int(inner_field.tag) < 10:
                        inner_data_field.text = inner_field.data
                        continue

                    inner_ind1 = ET.SubElement(inner_data_field, 'indicator')
                    inner_ind1.set('id', '1')
                    inner_ind1.text = inner_field.indicators[0]

                    inner_ind2 = ET.SubElement(inner_data_field, 'indicator')
                    inner_ind2.set('id', '2')
                    inner_ind2.text = inner_field.indicators[1]

                    for inner_subfield in inner_field:
                        inner_data_subfield = ET.SubElement(inner_data_field, 'subfield')
                        inner_data_subfield.set('id', inner_subfield[0])
                        inner_data_subfield.text = inner_subfield[1]

        else:
            data_field = ET.SubElement(root, 'field')
            data_field.set('id', field.tag)

            ind1 = ET.SubElement(data_field, 'indicator')
            ind1.set('id', '1')
            ind1.text = field.indicators[0]

            ind2 = ET.SubElement(data_field, 'indicator')
            ind2.set('id', '2')
            ind2.text = field.indicators[1]

            for subfield in field:
                data_subfield = ET.SubElement(data_field, 'subfield')
                data_subfield.set('id', subfield[0])
                data_subfield.text = subfield[1]

    return replace_illegal(''.join(ET.tostringlist(root, encoding='utf-8')))


