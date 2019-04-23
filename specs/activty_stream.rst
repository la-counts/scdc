Describe how django-activity-stream fulfills user activity requirements.

Docs: http://django-activity-stream.readthedocs.io

Required object/event tracking:

- save search
- save dataset
- save story
- view dataset
- view story
- view search


CONSIDER: do we want to story EVERY view?
Alternatively update or create Action instances.
Better yet: store views in browser, do it in js

We can store a search in a model or as an event parameter.
But non-action obj will require more verbose verbs (anti-pattern)

Problem: too many saved search objects from each view, or
complex pool routine

Divide and conquer: implement saving first.

"Saving" a content object is the same as following in django-activity-stream.

Searches are saved in a model with a hash value (ie hash(json_object))
Multiple users may reference the same saved search.
divergence: activity-stream is optimized for following actions, not listing "saves"
bonus: if a story links to a followed dataset, user is notified


Each of these tracked content types will live on their own page.
activity-stream provides default views but are generic.
Default user view provides an activity feed.
Default following view provides an entire list of following by user id.
Thus custom listing pages will be built.

Template tags will be needed for displaying a save feed and will link to listing pages.
