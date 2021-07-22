CREDITS
sidenav edge right taken from mini project

https://stackoverflow.com/questions/52226293/jinja2-check-if-value-exists-in-list-of-dictionaries

PROBLEMS!!!!


2. Everywhere in login register and logout return render_template("base.html") it is not ok, want to rerender current page
ALSO after COMMNENTING in comment view, rerender current page


4. HEEELP HOW TO FILTER COMMENTS I"M RUNNING OUT OF TIME!!!!

5. ADD A NEW THEME OPTION VALIDATION IN JS

7. EDIT QUOTE CHECK FOR EMPTY THEME

6. add edit quote fields, specify patterns
PATTERN pattern="[1-150]{1,3}"


12.  refreshing page adds quote again??  Must empty the field.. javascript

13. reusing ids for comment forms as well.

CODE FOR LATER

{{ url_for('add_theme') }}

{{ url_for('comment') }}

_theme = {
            "theme": request.form.get("theme")
        }
{{ url_for('edit_quote', quote_id=quote._id) }}
{{ url_for('delete_quote', quote_id=quote._id) }}


DON'T FORGET

CHANGE DUBUG TO FALSE

PREPOPULATE DATABASE

SCREENREADER INFO

BLOCKSCRIPTS

CRUD testing

Custom 404?


FEATURES TO ADD.. 
Values in add a quote API

MAJOR ISSUES 

comments will be difficult.. own collection.. comment, comment_author, relevant quote

BUGS/FIXES
Collapsible header overlayed with card panel to enable formatting

Fix indentation in add quote and edit quote so that database is updated

Change order of elements on my quotes card on small screens

Overide Materialize logo

Use javascript to show or hide new theme input on 

Needed modal code twice on my_quotes!!

Move endif statement inside closing h6 and li tags in comments collapsible body on browse and search results pages.  Corrects formatting.

Redirect url instead of calling function in views for add and edit quote and comment, prevents form resubmission on refresh page!


 

{% if quote.id in all_comments|map(attribute="quote_id") %}
{% if comment.quote_id == quote.id %}
....code for rendering comment
{% endif %}
{% else %}
<li>There are no comments about this quote yet. </li>
{% endif %}