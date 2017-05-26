# coding: utf-8

from google.appengine.ext import ndb
import flask
import flask_wtf
import wtforms

import auth
import config
import model
import util

from main import app


###############################################################################
# Update
###############################################################################
class ContactUpdateForm(flask_wtf.FlaskForm):
  name = wtforms.StringField(
    model.Contact.name._verbose_name,
    [wtforms.validators.required(), wtforms.validators.length(max=500)],
    filters=[util.strip_filter],
  )
  email = wtforms.StringField(
    model.Contact.email._verbose_name,
    [wtforms.validators.optional(), wtforms.validators.length(max=500)],
    filters=[util.email_filter],
  )
  phone = wtforms.StringField(
    model.Contact.phone._verbose_name,
    [wtforms.validators.optional(), wtforms.validators.length(max=500)],
    filters=[util.strip_filter],
  )
  address = wtforms.TextAreaField(
    model.Contact.address._verbose_name,
    [wtforms.validators.optional(), wtforms.validators.length(max=500)],
    filters=[util.strip_filter],
  )
  birthdate = wtforms.DateField(
    model.Contact.birthdate._verbose_name,
    [wtforms.validators.optional()],
  )


@app.route('/contact/create/', methods=['GET', 'POST'])
@app.route('/contact/<int:contact_id>/update/', methods=['GET', 'POST'])
@auth.login_required
def contact_update(contact_id=0):
  if contact_id:
    contact_db = model.Contact.get_by_id(contact_id)
  else:
    contact_db = model.Contact(user_key=auth.current_user_key())

  if not contact_db or contact_db.user_key != auth.current_user_key():
    flask.abort(404)

  form = ContactUpdateForm(obj=contact_db)

  user_dbs, user_cursor = model.User.get_dbs(limit=-1)
  if form.validate_on_submit():
    form.populate_obj(contact_db)
    contact_db.put()
    return flask.redirect(flask.url_for('contact_view', contact_id=contact_db.key.id()))

  return flask.render_template(
    'contact/contact_update.html',
    title=contact_db.name if contact_id else 'New Contact',
    html_class='contact-update',
    form=form,
    contact_db=contact_db,
  )


###############################################################################
# List
###############################################################################
@app.route('/contact/')
@auth.login_required
def contact_list():
  contact_dbs, contact_cursor = model.Contact.get_dbs(user_key=auth.current_user_key())
  return flask.render_template(
    'contact/contact_list.html',
    html_class='contact-list',
    title='Contact List',
    contact_dbs=contact_dbs,
    next_url=util.generate_next_url(contact_cursor),
    api_url=flask.url_for('api.contact.list'),
  )


###############################################################################
# View
###############################################################################
@app.route('/contact/<int:contact_id>/')
@auth.login_required
def contact_view(contact_id):
  contact_db = model.Contact.get_by_id(contact_id)
  if not contact_db or contact_db.user_key != auth.current_user_key():
    flask.abort(404)

  return flask.render_template(
    'contact/contact_view.html',
    html_class='contact-view',
    title=contact_db.name,
    contact_db=contact_db,
    api_url=flask.url_for('api.contact', contact_key=contact_db.key.urlsafe() if contact_db.key else ''),
  )


###############################################################################
# Admin List
###############################################################################
@app.route('/admin/contact/')
@auth.admin_required
def admin_contact_list():
  contact_dbs, contact_cursor = model.Contact.get_dbs(
    order=util.param('order') or '-modified',
  )
  return flask.render_template(
    'contact/admin_contact_list.html',
    html_class='admin-contact-list',
    title='Contact List',
    contact_dbs=contact_dbs,
    next_url=util.generate_next_url(contact_cursor),
    api_url=flask.url_for('api.admin.contact.list'),
  )


###############################################################################
# Admin Update
###############################################################################
class ContactUpdateAdminForm(ContactUpdateForm):
  pass


@app.route('/admin/contact/create/', methods=['GET', 'POST'])
@app.route('/admin/contact/<int:contact_id>/update/', methods=['GET', 'POST'])
@auth.admin_required
def admin_contact_update(contact_id=0):
  if contact_id:
    contact_db = model.Contact.get_by_id(contact_id)
  else:
    contact_db = model.Contact(user_key=auth.current_user_key())

  if not contact_db:
    flask.abort(404)

  form = ContactUpdateAdminForm(obj=contact_db)

  user_dbs, user_cursor = model.User.get_dbs(limit=-1)
  if form.validate_on_submit():
    form.populate_obj(contact_db)
    contact_db.put()
    return flask.redirect(flask.url_for('admin_contact_list', order='-modified'))

  return flask.render_template(
    'contact/admin_contact_update.html',
    title=contact_db.name,
    html_class='admin-contact-update',
    form=form,
    contact_db=contact_db,
    back_url_for='admin_contact_list',
    api_url=flask.url_for('api.admin.contact', contact_key=contact_db.key.urlsafe() if contact_db.key else ''),
  )


###############################################################################
# Admin Delete
###############################################################################
@app.route('/admin/contact/<int:contact_id>/delete/', methods=['POST'])
@auth.admin_required
def admin_contact_delete(contact_id):
  contact_db = model.Contact.get_by_id(contact_id)
  contact_db.key.delete()
  flask.flash('Contact deleted.', category='success')
  return flask.redirect(flask.url_for('admin_contact_list'))
