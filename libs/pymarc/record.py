import re
import hashlib

from exceptions import BaseAddressInvalid, RecordLeaderInvalid,\
    BaseAddressNotFound, RecordDirectoryInvalid, NoFieldsFound,\
    FieldNotFound
from constants import LEADER_LEN, DIRECTORY_ENTRY_LEN, END_OF_RECORD
from field import Field, SUBFIELD_INDICATOR, END_OF_FIELD,\
    map_marc8_field
from marc8 import marc8_to_unicode

isbn_regex = re.compile(r'([0-9\-]+)')

class Record(object):
    """
    A class for representing a MARC record. Each Record object is made up of
    multiple Field objects. You'll probably want to look at the docs for Field
    to see how to fully use a Record object.

    Basic usage:

        field = Field(
            tag = '245', 
            indicators = ['0','1'],
            subfields = [
                'a', 'The pragmatic programmer : ',
                'b', 'from journeyman to master /', 
                'c', 'Andrew Hunt, David Thomas.',
            ])

        record.add_field(field)

    Or creating a record from a chunk of MARC in transmission format:

        record = Record(data=chunk)

    Or getting a record as serialized MARC21.

        raw = record.as_marc()

    You'll normally want to use a MARCReader object to iterate through 
    MARC records in a file.  
    """

    def __init__(self, data='', to_unicode=True, force_utf8=True, encoding='utf-8',
                 hide_utf8_warnings=False, utf8_handling='strict'):
        self.leader = (' ' * 10) + '22' + (' ' * 8) + '4500'
        self.fields = []
        self.pos = 0
        self.force_utf8 = force_utf8
        if len(data) > 0:
            self.decode_marc(data, to_unicode=to_unicode,
                             force_utf8=force_utf8,
                             encoding=encoding,
                             hide_utf8_warnings=hide_utf8_warnings,
                             utf8_handling=utf8_handling)
        elif force_utf8:
            self.leader = self.leader[0:9] + 'a' + self.leader[10:]

    def set_leader_index(self, index, value):
        if index > 23:
            raise IndexError(u'Max index value: 23')

        self.leader = self.leader[:index] + value + self.leader[index + 1:]

    def __str__(self):
        """
        In a string context a Record object will return a prettified version
        of the record in MARCMaker format. See the docstring for Field.__str__
        for more information.
        """
        # join is significantly faster than concatenation
        self.fields = sorted(self.fields, key=lambda x: x.tag)
            
        text_list = ['%s' % self.leader]
        text_list.extend([unicode(field) for field in self.fields])
        text = u'\n'.join(text_list) + '\n'
        return text.encode('utf-8')

    def __getitem__(self, tag):
        """
        Allows a shorthand lookup by tag:
        
            record['245']

        """
        fields = self.get_fields(tag)
        if len(fields) > 0:
            return fields[0]
        return None

    def __iter__(self):
        self.__pos = 0
        return self

    def next(self):
        if self.__pos >= len(self.fields):
            raise StopIteration
        self.__pos += 1
        return self.fields[self.__pos - 1]

    def add_field(self, *fields):
        """
        add_field() will add pymarc.Field objects to a Record object.
        Optionally you can pass in multiple fields.
        """
        self.fields.extend(fields)

    def remove_field(self, *fields):
        """
        remove_field() will remove one or more pymarc.Field objects from
        a Record object.
        """
        for f in fields:
            try:
                self.fields.remove(f)
            except ValueError:
                raise FieldNotFound

    def get_fields(self, *args):
        """
        When passed a tag ('245'), get_fields() will return a list of all the 
        fields in a record with a given tag. 

            title = record.get_fields('245')
        
        If no fields with the specified 
        tag are found then an empty list is returned. If you are interested
        in more than one tag you can pass in a list:

            subjects = record.get_fields('600', '610', '650') 

        If no tag is passed in to get_fields() a list of all the fields will be 
        returned.
        """
        if (len(args) == 0):
            return self.fields

        return [f for f in self.fields if f.tag in args]

    def get_first_subfield(self,tag,subfield):
        """
        return first coincidence of field and subfield or None
        """
        for field in self.fields:
            if field.tag == tag:
                subfields = field.get_subfields(subfield)
                if len(subfields) > 0:
                    return subfields[0]
        return None

    def decode_marc(self, marc, to_unicode=False, force_utf8=False, encoding=None,
                    hide_utf8_warnings=False, utf8_handling='strict'):
        """
        decode_marc() accepts a MARC record in transmission format as a
        a string argument, and will populate the object based on the data
        found. The Record constructor actually uses decode_marc() behind
        the scenes when you pass in a chunk of MARC data to it.

        """
        # extract record leader
        self.marc = marc
        try:
            self.leader = marc[0:LEADER_LEN]
            if len(self.leader) != LEADER_LEN:
                raise RecordLeaderInvalid

            # extract the byte offset where the record data starts
            base_address = int(marc[12:17])
            if base_address <= 0:
                raise BaseAddressNotFound
            if base_address >= len(marc):
                raise BaseAddressInvalid

            # extract directory, base_address-1 is used since the
            # director ends with an END_OF_FIELD byte
            directory = marc[LEADER_LEN:base_address - 1]

            # determine the number of fields in record
            if len(directory) % DIRECTORY_ENTRY_LEN != 0:
                raise RecordDirectoryInvalid
            field_total = len(directory) / DIRECTORY_ENTRY_LEN

            # add fields to our record using directory offsets
            field_count = 0
            while field_count < field_total:
                entry_start = field_count * DIRECTORY_ENTRY_LEN
                entry_end = entry_start + DIRECTORY_ENTRY_LEN
                entry = directory[entry_start:entry_end]
                entry_tag = entry[0:3]
                entry_length = int(entry[3:7])
                entry_offset = int(entry[7:12])
                entry_data = marc[base_address + entry_offset:
                base_address + entry_offset + entry_length - 1]

                # assume controlfields are numeric; replicates ruby-marc behavior
                if entry_tag < '010' and entry_tag.isdigit():
                    field = Field(tag=entry_tag, data=entry_data)
                else:
                    subfields = list()
                    subs = entry_data.split(SUBFIELD_INDICATOR)
                    first_indicator = subs[0][0]
                    second_indicator = subs[0][1]
                    for subfield in subs[1:]:
                        if len(subfield) == 0:
                            continue
                        code = subfield[0]
                        data = subfield[1:]
                        if to_unicode:
                            if self.leader[9] == 'a' or force_utf8:
                                data = data.decode('utf-8', utf8_handling)
                            elif encoding and (encoding != 'marc-8'):
                                try:
                                    data = data.decode(encoding, utf8_handling)
                                except UnicodeDecodeError:
                                    data = u"Can't decode string"
                            else:
                                data = marc8_to_unicode(data, hide_utf8_warnings)
                        subfields.append(code)
                        subfields.append(data)
                    field = Field(
                        tag=entry_tag,
                        indicators=[first_indicator, second_indicator],
                        subfields=subfields,
                        )

                self.add_field(field)
                field_count += 1
        except Exception:
            print marc
            raise Exception()

        if field_count == 0:
            raise NoFieldsFound

    def as_marc(self, encoding='UTF-8', sorted_fields=True):
        """
        encoding - encoding of serialized record
        returns the record serialized as MARC21
        """

        if sorted_fields:
            self.fields = sorted(self.fields, key=lambda x: x.tag)

        if encoding:
            encoding = encoding.lower()
            if encoding == 'utf-8' or encoding == 'utf8':
                self.set_leader_index(9, 'a')

        fields = []
        directory = ''
        offset = 0

        # build the directory
        # each element of the directory includes the tag, the byte length of 
        # the field and the offset from the base address where the field data
        # can be found
        for field in self.fields:
            field_data = field.as_marc()
            if self.force_utf8:
                self.set_leader_index(9, 'a')

            if self.leader[9] == 'a':
                field_data = field_data.encode('utf-8')
            elif encoding:
                field_data = field_data.encode(encoding)

            fields.append(field_data)
            if field.tag.isdigit():
                directory += '%03d' % int(field.tag)
            else:
                directory += '%03s' % field.tag
            directory += '%04d%05d' % (len(field_data), offset)

            offset += len(field_data)

        # directory ends with an end of field
        directory += END_OF_FIELD

        # field data ends with an end of record
        fields.append(END_OF_RECORD)
        fields = ''.join(fields)
        # the base address where the directory ends and the field data begins
        base_address = LEADER_LEN + len(directory)

        # figure out the length of the record 
        record_length = base_address + len(fields)

        # update the leader with the current record length and base address
        # the lengths are fixed width and zero padded
        self.leader = '%05d%s%05d%s' %\
                      (record_length, self.leader[5:12], base_address, self.leader[17:])

        # return the encoded record
        return ''.join((self.leader,directory,fields))

    def md5(self):

        fields = []

        # build the directory
        # each element of the directory includes the tag, the byte length of
        # the field and the offset from the base address where the field data
        # can be found
        for field in self.fields:
            if field.is_control_field(): continue
            field_data = field.as_marc()
            field_data = field_data.encode('utf-8')


            fields.append(field_data)

        fields = ''.join(fields)


        # return the encoded record
        return hashlib.md5(fields).hexdigest()
        # alias for backwards compatability

    def as_dict(self, syntax=u'1.2.840.10003.5.28'):

        record_dict = {
            'syntax': syntax,
            'leader': self.leader,
            'controlfields': {},
            'datafields': {}
        }

        for field in self.fields:
            if field.is_control_field():
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

    def title(self):
        """
        Returns the title of the record (245 $a an $b).
        """
        try:
            title = self['245']['a']
        except TypeError:
            title = None
        if title:
            try:
                title += self['245']['b']
            except TypeError:
                pass
        return title

    def isbn(self):
        """
        Returns the first ISBN in the record or None if one is not
        present. The returned ISBN will be all numberic; so dashes and 
        extraneous information will be automatically removed. If you need 
        this information you'll want to look directly at the 020 field, 
        e.g. record['020']['a']
        """
        try:
            isbn_number = self['020']['a']
            match = isbn_regex.search(isbn_number)
            if match:
                return match.group(1).replace('-', '')
        except TypeError:
            # ISBN not set
            pass
        return None

    def author(self):
        if self['100']:
            return self['100'].format_field()
        elif self['110']:
            return self['110'].format_field()
        elif self['111']:
            return self['111'].format_field()
        return None

    def uniformtitle(self):
        if self['130']:
            return self['130'].format_field()
        elif self['240']:
            return self['240'].format_field()
        return None

    def subjects(self):
        """
        Note: Fields 690-699 are considered "local" added entry fields but
        occur with some frequency in OCLC and RLIN records.
        """
        subjlist = self.get_fields('600', '610', '611', '630', '648', '650',
                                   '651', '653', '654', '655', '656', '657', '658', '662', '690',
                                   '691', '696', '697', '698', '699')
        return subjlist

    def addedentries(self):
        """
        Note: Fields 790-799 are considered "local" added entry fields but
        occur with some frequency in OCLC and RLIN records.
        """
        aelist = self.get_fields('700', '710', '711', '720', '730', '740',
                                 '752', '753', '754', '790', '791', '792', '793', '796', '797',
                                 '798', '799')
        return aelist

    def location(self):
        loc = self.get_fields('852')
        return loc

    def notes(self):
        """
        Return all 5xx fields in an array.
        """
        notelist = self.get_fields('500', '501', '502', '504', '505',
                                   '506', '507', '508', '510', '511', '513', '514', '515',
                                   '516', '518', '520', '521', '522', '524', '525', '526',
                                   '530', '533', '534', '535', '536', '538', '540', '541',
                                   '544', '545', '546', '547', '550', '552', '555', '556',
                                   '561', '562', '563', '565', '567', '580', '581', '583',
                                   '584', '585', '586', '590', '591', '592', '593', '594',
                                   '595', '596', '597', '598', '599')
        return notelist

    def physicaldescription(self):
        """
        Return all 300 fields in an array
        """
        return self.get_fields('300')

    def publisher(self):
        if self['260']:
            return self['260']['b']
        return None

    def pubyear(self):
        if self['260']:
            return self['260']['c']
        return None


class UnimarcRecord(Record):
    def __init__(self, *args, **kwargs):
        super(UnimarcRecord, self).__init__(*args, **kwargs)


    def decode_marc(self, marc, to_unicode=True, force_utf8=False, encoding=None,
                    hide_utf8_warnings=False, utf8_handling='strict'):
        self.marc = marc
        """
        decode_marc() accepts a MARC record in transmission format as a
        a string argument, and will populate the object based on the data
        found. The Record constructor actually uses decode_marc() behind
        the scenes when you pass in a chunk of MARC data to it.

        """
        # extract record leader
        self.leader = marc[0:LEADER_LEN]
        if len(self.leader) != LEADER_LEN:
            raise RecordLeaderInvalid

        # extract the byte offset where the record data starts
        base_address = int(marc[12:17])
        if base_address <= 0:
            raise BaseAddressNotFound
        if base_address >= len(marc):
            raise BaseAddressInvalid

        # extract directory, base_address-1 is used since the
        # director ends with an END_OF_FIELD byte
        directory = marc[LEADER_LEN:base_address - 1]

        # determine the number of fields in record
        if len(directory) % DIRECTORY_ENTRY_LEN != 0:
            raise RecordDirectoryInvalid
        field_total = len(directory) / DIRECTORY_ENTRY_LEN

        # add fields to our record using directory offsets
        field_count = 0
        while field_count < field_total:
            entry_start = field_count * DIRECTORY_ENTRY_LEN
            entry_end = entry_start + DIRECTORY_ENTRY_LEN
            entry = directory[entry_start:entry_end]
            entry_tag = entry[0:3]
            entry_length = int(entry[3:7])
            entry_offset = int(entry[7:12])
            entry_data = marc[base_address + entry_offset:
            base_address + entry_offset + entry_length - 1]

            # assume controlfields are numeric; replicates ruby-marc behavior
            if entry_tag < '010' and entry_tag.isdigit():
                field = Field(tag=entry_tag, data=entry_data)
            elif entry_tag[0] == '4':
                subfields = list()
                subs = entry_data.split(SUBFIELD_INDICATOR)
                first_indicator = subs[0][0]
                second_indicator = subs[0][1]
                field_data = subs[1:]
                i = 0
                field_data_len = len(field_data)
                while i < field_data_len:
                    #if subfield 1, then read embedded field tag number
                    if field_data[i][0] == '1':
                        embedded_field_tag = field_data[i][1:4]
                        if embedded_field_tag == '001':
                            emb_field = Field(tag=embedded_field_tag,
                                              data=field_data[i][4:])
                            subfields.append('1')
                            subfields.append(emb_field)
                            i += 1
                            continue
                        if len(field_data[i]) < 6:
                            i+=1
                            continue
                        embedded_field_i1 = field_data[i][4]
                        embedded_field_i2 = field_data[i][5]




                            
                        embedded_subfields = list()
                        i += 1
                        while i < field_data_len and field_data[i][0] != '1':
                            code = field_data[i][0]
                            data = field_data[i][1:]

                            if to_unicode:
#                                if encoding != 'marc-8' and force_utf8:
#                                    data = data.decode('utf-8', 'replace')
                                if encoding != 'marc-8':
                                    data = data.decode(encoding, utf8_handling)
                                else:
                                    data = data.decode(encoding, 'replace')
                            embedded_subfields.append(code)
                            embedded_subfields.append(data)
                            i += 1

                        emb_field = Field(tag=embedded_field_tag,
                                          indicators=[embedded_field_i1, embedded_field_i2],
                                          subfields=embedded_subfields)
                        subfields.append('1')
                        subfields.append(emb_field)

                field = Field(
                    tag=entry_tag,
                    indicators=[first_indicator, second_indicator],
                    subfields=subfields,
                    )

            else:
                subfields = list()
                subs = entry_data.split(SUBFIELD_INDICATOR)
                first_indicator = subs[0][0]
                second_indicator = subs[0][1]
                for subfield in subs[1:]:
                    if len(subfield) == 0:
                        continue
                    code = subfield[0]
                    data = subfield[1:]

                    if to_unicode:
                        if encoding != 'marc-8':
                            data = data.decode(encoding, utf8_handling)
                        else:
                            data = marc8_to_unicode(data, hide_utf8_warnings)
                    subfields.append(code)
                    subfields.append(data)
                field = Field(
                    tag=entry_tag,
                    indicators=[first_indicator, second_indicator],
                    subfields=subfields,
                    )

            self.add_field(field)
            field_count += 1


        if field_count == 0:
            raise NoFieldsFound
        #del  self.marc


def map_marc8_record(r):
    r.fields = map(map_marc8_field, r.fields)
    l = list(r.leader)
    l[9] = 'a' # see http://www.loc.gov/marc/specifications/speccharucs.html
    r.leader = "".join(l)
    return r
