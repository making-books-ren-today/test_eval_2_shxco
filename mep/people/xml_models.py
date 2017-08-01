from django.core.exceptions import ObjectDoesNotExist
from eulxml import xmlmap

from mep.people import models


class TeiXmlObject(xmlmap.XmlObject):
    ROOT_NAMESPACES = {
        't': 'http://www.tei-c.org/ns/1.0'
    }

class Nationality(TeiXmlObject):
    code = xmlmap.StringField('@key')
    label = xmlmap.StringField('normalize-space(.)')


class Residence(TeiXmlObject):
    name = xmlmap.StringField('t:address/t:name|t:address/t:name', normalize=True)
    street = xmlmap.StringField('t:address/t:street', normalize=True)
    postcode = xmlmap.StringField('t:address/t:postCode', normalize=True)
    city = xmlmap.StringField('t:address/t:settlement', normalize=True)
    # lat/long are in a single <geo> field, separated by a comma
    geo = xmlmap.StringField('t:geo')
    latitude = xmlmap.FloatField('substring-before(t:geo, ",")')
    longitude = xmlmap.FloatField('substring-after(t:geo, ",")')

    def db_address(self):
        '''Get the corresponding :class:`mep.people.models.Address` in the
        database, creating a new address if it does not exist.'''
        addr, created = models.Address.objects.get_or_create(
            name=self.name or '',
            street_address=self.street or '',
            city=self.city or '',
            postal_code=self.postcode or '',
            # NOTE: including lat/long in the get or create call
            # results in a new address getting created with the same values.
            defaults={
                'latitude': self.latitude,
                'longitude': self.longitude,
            }
        )

        # NOTE: if an existing address is found, could check
        # and warn if lat/long do not match
        return addr

class Name(TeiXmlObject):
    name_type = xmlmap.StringField('@type')
    sort = xmlmap.StringField('@sort')
    full = xmlmap.StringField('@full')
    value = xmlmap.StringField('text()')

    def __str__(self):
        if self.full == 'init':
            return '%s.' % self.value.strip('.')
        return self.value


class PersonName(TeiXmlObject):
    last_names = xmlmap.NodeListField('t:surname', Name)
    first_names = xmlmap.NodeListField('t:forename', Name)
    married_name = xmlmap.NodeField('t:surname[@type="married"]', Name)
    birth_name = xmlmap.NodeField('t:surname[@type="birth"]', Name)

    namelink = xmlmap.StringField('t:nameLink')
    birth_namelink = xmlmap.StringField('t:nameLink[@type="birth"]')
    married_namelink = xmlmap.StringField('t:nameLink[@type="married"]')

    def full_name(self):
        '''Combine first and last names into "firstname lastname" or
        "firstname (birth name) married name".  Handles multiple first names,
        initials, etc.'''
        return ' '.join(
            # exclude any empty values
            [name for name in
                [self.first_name(), self.display_birthname(), self.last_name()]
            if name])

    def sort_name(self):
        '''Combine first and last names into "lastname, firstname" or
        "married name, firstname (birth name)".  Handles multiple first names,
        initials, etc.'''
        first_name = ' '.join(
            [name for name in [self.first_name(), self.display_birthname()]
             if name])
        return ', '.join([n for n in [self.last_name(), first_name] if n])

    def display_birthname(self):
        # in some cases only one name is present but it is tagged as birth name
        if self.birth_name and self.married_name:
            birth_name = ' '.join([self.birth_namelink or '',
                                   str(self.birth_name)])
            return '(%s)' % birth_name.strip()
        return ''

    def last_name(self):
        # if married name is set, return that
        if self.married_name:
            lastname = str(self.married_name)
        # otherwise, just use the first last name
        else:
            lastname = str(self.last_names[0])

        # if a namelink is present (de, du, de la, etc - include it)
        if self.married_namelink or self.namelink:
            return ' '.join([self.married_namelink or self.namelink, lastname])

        return lastname

    def first_name(self):
        # handle multiple first names
        sorted_names = sorted(self.first_names, key=lambda n: n.sort or 0)
        return ' '.join([str(n) for n in sorted_names])


class Person(TeiXmlObject):
    mep_id = xmlmap.StringField('@xml:id')
    viaf_id = xmlmap.StringField('t:idno[@type="viaf"]')
    title = xmlmap.StringField('t:persName/t:roleName')
    names = xmlmap.NodeListField('t:persName', PersonName)
    last_name = xmlmap.StringField('t:persName/t:surname')
    first_name = xmlmap.StringField('t:persName/t:forename')
    birth = xmlmap.IntegerField('t:birth')
    death = xmlmap.IntegerField('t:death')
    sex = xmlmap.StringField('t:sex/@value')
    notes = xmlmap.StringListField('t:note')
    urls = xmlmap.StringListField('.//t:ref/@target')
    nationalities = xmlmap.NodeListField('t:nationality', Nationality)
    # todo: handle ref target in notes
    residences = xmlmap.NodeListField('t:residence', Residence)

    def is_imported(self):
        return models.Person.objects.filter(mep_id=self.mep_id).exists()

    def to_db_person(self):
        '''Create a new :class:`mep.people.models.Person` database record
        and populate based on data in the xml.'''
        db_person = models.Person(
            mep_id=self.mep_id,
            title=self.title or '',
            birth_year=self.birth or None,
            death_year=self.death or None,
            sex=self.sex or ''
        )

        # handle names
        # - simple case: only one name in the xml
        if len(self.names) == 1:
            db_person.name = self.names[0].full_name()
            db_person.sort_name = self.names[0].sort_name()

        # temporary; should be in viaf code eventually
        if self.viaf_id:
            db_person.viaf_id = "http://viaf.org/viaf/%s" % self.viaf_id

        # Combine any non-empty notes from the xml and put them in the
        # database notes field. (URLs are handled elsewhere)
        db_person.notes = '\n'.join(note for note in self.notes
                                    if note.strip())
        # record must be saved before adding relations to other tables
        db_person.save()

        # handle nationalities; could be multiple
        for nation in self.nationalities:
            try:
                # if a country has already been created, find it
                country = models.Country.objects.get(code=nation.code)
            except models.Country.DoesNotExist:
                # otherwise, create a new country entry
                country = models.Country.objects.create(code=nation.code,
                    name=nation.label)

            db_person.nationalities.add(country)

        # handle URLs included in notes
        for link in self.urls:
            db_person.urls.add(models.InfoURL.objects.create(url=link,
                person=db_person, notes='URL from XML import'))

        # handle residence addresses
        for res in self.residences:
            db_person.addresses.add(res.db_address())

        return db_person


class Personography(xmlmap.XmlObject):
    ROOT_NAMESPACES = {
        't': 'http://www.tei-c.org/ns/1.0'
    }

    people = xmlmap.NodeListField('//t:person', Person)

    @classmethod
    def from_file(cls, filename):
        return xmlmap.load_xmlobject_from_file(filename, cls)
