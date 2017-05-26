# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb
import flask
import flask_restful

from api import helpers
import auth
import model
import util

from main import api_v1


@api_v1.resource('/contact/', endpoint='api.contact.list')
class ContactListAPI(flask_restful.Resource):
  @auth.login_required
  def get(self):
    contact_dbs, contact_cursor = model.Contact.get_dbs(user_key=auth.current_user_key())
    return helpers.make_response(contact_dbs, model.Contact.FIELDS, contact_cursor)


@api_v1.resource('/contact/<string:contact_key>/', endpoint='api.contact')
class ContactAPI(flask_restful.Resource):
  @auth.login_required
  def get(self, contact_key):
    contact_db = ndb.Key(urlsafe=contact_key).get()
    if not contact_db or contact_db.user_key != auth.current_user_key():
      helpers.make_not_found_exception('Contact %s not found' % contact_key)
    return helpers.make_response(contact_db, model.Contact.FIELDS)


###############################################################################
# Admin
###############################################################################
@api_v1.resource('/admin/contact/', endpoint='api.admin.contact.list')
class AdminContactListAPI(flask_restful.Resource):
  @auth.admin_required
  def get(self):
    contact_keys = util.param('contact_keys', list)
    if contact_keys:
      contact_db_keys = [ndb.Key(urlsafe=k) for k in contact_keys]
      contact_dbs = ndb.get_multi(contact_db_keys)
      return helpers.make_response(contact_dbs, model.contact.FIELDS)

    contact_dbs, contact_cursor = model.Contact.get_dbs()
    return helpers.make_response(contact_dbs, model.Contact.FIELDS, contact_cursor)

  @auth.admin_required
  def delete(self):
    contact_keys = util.param('contact_keys', list)
    if not contact_keys:
      helpers.make_not_found_exception('Contact(s) %s not found' % contact_keys)
    contact_db_keys = [ndb.Key(urlsafe=k) for k in contact_keys]
    ndb.delete_multi(contact_db_keys)
    return flask.jsonify({
      'result': contact_keys,
      'status': 'success',
    })


@api_v1.resource('/admin/contact/<string:contact_key>/', endpoint='api.admin.contact')
class AdminContactAPI(flask_restful.Resource):
  @auth.admin_required
  def get(self, contact_key):
    contact_db = ndb.Key(urlsafe=contact_key).get()
    if not contact_db:
      helpers.make_not_found_exception('Contact %s not found' % contact_key)
    return helpers.make_response(contact_db, model.Contact.FIELDS)

  @auth.admin_required
  def delete(self, contact_key):
    contact_db = ndb.Key(urlsafe=contact_key).get()
    if not contact_db:
      helpers.make_not_found_exception('Contact %s not found' % contact_key)
    contact_db.key.delete()
    return helpers.make_response(contact_db, model.Contact.FIELDS)
