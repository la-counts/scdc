NOTE: This may be outside scope. Discussion needed.

Reputation tracking and permission advancement.

Badges will be provided by 3rd party app: https://github.com/jiaaro/django-badges

Reputation is categorized into specialties.
Karma is the grand sum of all reputation points.

CONSIDER: this level of integration would be simpler with a built-in commenting system.


Users should be rewarded when:

- someone up votes their content or message
- a moderator change is approved
- user is linked/verified to a publisher
- completes special profile fields
- receives a badge


Reputation points and badges unlock actions to the specialties:

- flag content
- leave a comment (possibly disabled for negative rep)
- submit dataset
- suggest dataset modification
- submit story
- moderation actions (badge only)
- award badges or reputation (staff badge)


CONSIDER: a badge may be associated to a particular focus area as well as the unlocks...
SOLUTION: m2m between badge, permission, and null focus area

CONSIDER: does categorical reputation constrict where a story maybe submitted from?
How do we perform the permission check? Is it against the focus area?

Submitted with focus object:

- focus_area.can_submit_story
- focus_area.can_moderate
- focus_area.can_comment

CONSIDER: this would likely structure the entire site into focus areas.
All moderated actions would require a focus area as part of their action.
