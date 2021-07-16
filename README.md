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


11. MOBILE LAYOUT.. logo.. edit and delete quotes

12.  refreshing page adds quote again


CODE FOR LATER

{{ url_for('add_theme') }}

{{ url_for('comment') }}

_theme = {
            "theme": request.form.get("theme")
        }
{{ url_for('edit_quote', quote_id=quote._id) }}
{{ url_for('delete_quote', quote_id=quote._id) }}


 <!-- <a href="#" class="btn-small"><i class="fas fa-pencil-alt"></i>Edit</a>
            <a href="#" class="btn-small"><i class="far fa-trash-alt"></i>Delete</a>
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

Validate Dropdown

FEATURES TO ADD.. 
Defensive programming.. empty themes?  Values in add a quote

MAJOR ISSUES 
Add theme.. send to themes and quotes collection
my_quotes need new variable fo quotes matching username, like search resuts, load that in page.. better do before starting comments
browse results page needs to pick up browse results: browsed from themes collection, need to match to quotes collection
Modals closing, what to render/return.. WANT TO REFRESH WEBSITE

comments will be difficult.. own collection.. comment, comment_author, relevant quote

BUGS/FIXES
Collapsible header overlayed with card panel to enable formatting


 <div class="collapsible-body">
            <ul>
                {% if quote_comments|length > 0%}
                {for _comment in quote_comments}

                <li>
                    <div class="card-panel">
                        <div class="row">
                            Comment + user
                            Comment {{ _comment.comment }} + user {{ _comment.user }}
                        </div>
                    </div>
                </li>
                {% endfor %}
                    
                
                {% else %} 

                <li>There are no comments about this quote yet. {% if not session.user %} <a href="#modal2"
                        class="modal-trigger">Login</a> or <a href="#modal1" class="modal-trigger">register</a> to add a
                    Comment.</li>
                {% endif %}
                {% endif %}
                {% if session.user %}
                <li>
                    <div class="card-panel">
                        <div class="row">
                            <form method="POST" action="">
                                <div class="input-field">
                                    <input name="comment" id="comment" minlength="3" type="text">
                                    <label for="comment"><i class="far fa-comment search-label"></i> Make a
                                        comment</label>
                                </div>
                            </form>
                        </div>
                    </div>
                </li>
                {% endif %}
                
            </ul>
        </div>