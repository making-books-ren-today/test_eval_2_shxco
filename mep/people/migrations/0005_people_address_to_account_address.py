# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-08 18:20
from __future__ import unicode_literals

from django.db import migrations


def associate_people_addresses_with_accounts(apps, schema_editor):
    # all address data imported via personography should be associated
    # with accounts rather than directly with people

    Person = apps.get_model("people", "Person")
    Account = apps.get_model("accounts", "Account")
    Address = apps.get_model("accounts", "Address")

    for person in Person.objects.filter(addresses__isnull=False).distinct():
        # use the first available account for the person, if there is one
        # (could be multiple, but don't expect in current data)
        account = person.account_set.first()
        # create account if no account exists yet (i.e., person in cards
        # but not in logbooks or not harmonized)
        if not account:
            account = Account.objects.create()
            account.persons.add(person)

        # for each location, create an address associated with the account
        for location in person.addresses.all():
            Address.objects.create(location=location, account=account)


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0004_rename_address_to_location'),
    ]

    operations = [
        migrations.RunPython(associate_people_addresses_with_accounts,
                             migrations.RunPython.noop)
    ]
