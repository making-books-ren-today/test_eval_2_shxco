# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-02-22 21:01
from __future__ import unicode_literals

from django.db import migrations, models


def copy_items_to_generic_event(apps, schema_editor):
    '''
    Copy items from event subclasses that have them to generic
    event item.
    '''
    Borrow = apps.get_model('accounts', 'Borrow')
    Purchase = apps.get_model('accounts', 'Purchase')

    # update generic item to use the value of item
    for borrow in Borrow.objects.filter(item__isnull=False).iterator():
        borrow.generic_item = borrow.item
        borrow.save()

    assert Borrow.objects.filter(item__isnull=False).count() == \
        Borrow.objects.filter(generic_item__isnull=False).count()

    for purchase in Purchase.objects.filter(item__isnull=False):
        purchase.generic_item = purchase.item
        purchase.save()

    assert Purchase.objects.filter(item__isnull=False).count() == \
        Purchase.objects.filter(generic_item__isnull=False).count()


    # NOTE: should be possible to use update with a field reference,
    # but django complains that it can't resolve 'item' into a field
    # Borrow.objects.filter(item__isnull=False) \
    #        .update(generic_item=models.F('item'))
    # Purchase.objects.filter(item__isnull=False) \
    #       .update(generic_item=models.F('item'))


def copy_items_from_generic_event(apps, schema_editor):
    '''
    Copy generic event item to subclass item.
    '''

    Borrow = apps.get_model('accounts', 'Borrow')
    Purchase = apps.get_model('accounts', 'Purchase')

    for borrow in Borrow.objects.filter(item__isnull=False):
        borrow.item = borrow.generic_item
        borrow.save()

    for purchase in Purchase.objects.filter(item__isnull=False):
        purchase.item = purchase.generic_item
        purchase.save()

    # copy generic item back to item so we don't lose data
    # if we  migrate backwards too far
    # NOTE: this doesn't work either
    # Borrow.objects.filter(generic_item__isnull=False) \
    #       .update(item=models.F('generic_item'))
    # Purchase.objects.filter(generic_item__isnull=False) \
    #       .update(item=models.F('generic_item'))


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0024_event_generic_item'),
    ]

    operations = [
        migrations.RunPython(copy_items_to_generic_event,
                             copy_items_from_generic_event)
    ]
