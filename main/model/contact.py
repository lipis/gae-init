# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb

from api import fields
import model
import util


class Contact(model.Base):
  user_key = ndb.KeyProperty(kind=model.User, required=True, verbose_name=u'User')
  name = ndb.StringProperty(required=True)
  email = ndb.StringProperty(default='')
  phone = ndb.StringProperty(default='')
  address = ndb.StringProperty(default='')
  birthdate = ndb.DateProperty()

  FIELDS = {
    'user_key': fields.Key,
    'name': fields.String,
    'email': fields.String,
    'phone': fields.String,
    'address': fields.String,
    'birthdate': fields.DateTime,
  }

  FIELDS.update(model.Base.FIELDS)
