Define the various user submissions and their approval processes.

Note: dataset in the client UI is CatalogRecord in the backend.

Commenting is exempt from this spec but it might be a good idea to allow for general object flagging that could support comment moderation.


============
User Stories
============

Story Submission
================

1. User fills out a form to submit a story
2. The form sends the submission to the moderator panel
3. Moderator clicks on story from moderator panel
4. Moderator may make changes and publish, or reject
5. Story is marked as resolved and no longer shows up in the default listing


Dataset Submission
==================

1. User fills out a form to suggest a dataset
2. The form sends the submission to the moderator panel
3. Moderator clicks on dataset from moderator panel
4. Moderator may make changes and approve, or reject
5. Dataset is marked as resolved and no longer shows up in the default listing


Flag Broken Dataset Link
========================

1. User attempts to acquire dataset and notices the link is broken
2. User clicks flag icon next to dataset
3. User is presented a form with a dropdown for a reason and an optional message
4. The form sends a flag to the moderator panel
5. Moderator clicks on flag from moderator panel
6. Moderator reviews the flag type, message, and the dataset (flagged object) (admin link provided)
7. Moderator may hit a `resolved` button to resolve the flag
8. Flag is marked as resolved and no longer shows up in default listing

Note: this is to be handled by django-flag , implementation my not be covered here.


Suggest Dataset Change
======================

1. User is presented with a catalog record form pre-filled with the current values
2. The user may change any value in the form and submit the changes for review
3. The form sends only the changed values (change set) to the moderator panel
4. Moderator clicks on change set from moderator panel
5. Moderator reviews purposed changes vs current values of the dataset
6. Moderator may individually approve field changes, accept all changes, or reject all changes
7. Change set is marked as processed and no longer shows up in default listing


==============
Implementation
==============

Each app defines its own creation and moderation logic.
An app can request a moderation action via an API call.
The topic specified for the action will route the moderation view? or action?

View:
- full control
- must import moderation
- less standard desgin, not DRY

Action:
- difficult with multiple models or forms

Recommended pattern is to have the submission view create the instance desired but in an unpublished state.

Seems each app should have their own publishing/moderation views.
Therefor lets look at some patterns:

- https://gist.github.com/Nagyman/9502133
- https://github.com/kmmbvnr/django-fsm
- https://github.com/gadventures/django-fsm-admin

Conclusion: Use FSMField

Users still post unpublished, but the published checkbox becomes a state field that includes `rejected`
moderation can just be done in the admin.


Tag Widget
==========

User needs to autocomplete from concepts but also "suggest" new tags.
Suggested tags do not automatically create concepts, that is done by staff.

Django-Select2 might be the best bet:
http://django-select2.readthedocs.io/en/latest/django_select2.html#module-django_select2.conf
https://github.com/applegrew/django-select2

Select2 itself supports this scenario.
We can do a custom ModelSelect2TagWidget that returns a tuple of lists (concepts, keywords)
