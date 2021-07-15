CREDITS
sidenav edge right taken from mini project

PROBLEMS
1. register bugs.. return what? empty open modal if username already exists (clear form) previous page if registration successful, whatever previous page was.. Make flash messages go away after flashing.   Need to confirm password before making dictionary... How?? notes p53...


2. Everywhere in login register and logout return render_template("base.html") it is not ok

3. confirm password at registration

4. username id twice

5. ADD A NEW THEME OPTION!! Javascript??

Once added, must also be selected for that quote

Defensive.. alert.. are you sure you want to add this theme.. please check spelling .. ok

6. Dropdown number pickers for chapter and verse
Dropdown select for book

7.  Editing themes.. spelling mistake? only edit My themes.. other users added quotes to that theme: don't delete the theme. PROFILE PAGE: my quotes and my themes.  Delete a quote, only edit a theme.



9. Collapsible header overlayed with card panel to enable formatting

10.  No quotes on my quotes page.. show message not empty collapsible

CODE FOR LATER

{{ url_for('add_theme') }}

_theme = {
            "theme": request.form.get("theme")
        }
{{ url_for('edit_quote', quote_id=quote._id) }}
{{ url_for('delete_quote', quote_id=quote._id) }}


 <!-- <a href="#" class="btn-small"><i class="fas fa-pencil-alt"></i>Edit</a>
            <a href="#" class="btn-small"><i class="far fa-trash-alt"></i>Delete</a>
  -->

  <!-- 8. <h4 class="red-text text-darken-4 center-align">You have not added any quotes yet.  Click <a href="{{ url_for('add_quote') }}">here</a>to add a quote.</h4>
   -->

   <!-- <form method="POST" action="">
                            <div class="input-field">
                                <i class="far fa-plus-square prefix"></i>
                            <input type="text" id="new_theme" name="new_theme">
                            <label for="new_theme">Or add a New Theme</label>
                        </div>
                        </form> -->

<!-- {{ url_for('add_theme') }} -->


DON'T FORGET

CHANGE DUBUG TO FALSE

FEATURES TO ADD.. 
Defensive programming.. empty themes?  Values in add a quote

Editing themes? Maybe.. the edited theme needs to then update in the quote documents for all with that theme..could change meaning of theme.. not ok for others who have now used that theme
Problem if just correcting spelling mistake
