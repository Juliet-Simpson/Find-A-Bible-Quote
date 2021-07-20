{% extends "base.html" %}
{% block content %}
<h3 class="center">My Quotes</h3>

<!-- NEW IDEA -->
{% if my_quotes|length > 0 %}

<ul class="collapsible">
    {% for quote in my_quotes %}
    <li>
        <div class="collapsible-header">
            <div class="card-panel collapsible-card">
                <div class="row">
                    <div class="col m4 s8">
                        <h6 class="justify-left">{{ quote.book }} {{ quote.chapter }} :
                            {{ quote.start_verse }}{% if quote.end_verse%}-{{quote.end_verse}}{% endif %}</h6>
                    </div>
                    <div class="col s8 m4">
                        <h6 class="justify-center">Theme: <strong>{{ quote.theme }}.</strong></h6>
                    </div>
                    <div class="col s4 btn-col">
                        <a href="{{ url_for('edit_quote', quote_id=quote._id) }}" class="btn-small"><i
                                class="fas fa-pencil-alt"></i></a>
                        <a href="#modal{{quote._id}}" class="btn-small modal-trigger"><i
                                class="far fa-trash-alt"></i></a>
                    </div>
                </div>
                <div class="row">
                    <div class="col s12">
                        <h5>"{{quote.text}}"</h5>
                    </div>
                </div>
                <div class="row">
                    <div class="col s12 btn-col">
                        <i class="fas fa-caret-down"></i>Comments
                    </div>
                </div>
            </div>
        </div>
        <div class="collapsible-body comment-body">
            <ul>
              {% if quote.id in comments|map(attribute="quote_id") %}
                {% if comment.quote_id == quote.id %}
                <li>
                    <div class="card-panel">
                        <div class="row">
                            <h6>{{ comment.comment }} {{ comment.user }}</h6>
                        </div>
                    </div>
                </li>
                {% endif %}
                {% else %}
                <li>There are no comments about this quote yet. </li>
                {% endif %}
                <li>
                    <div class="card-panel make-comment-card">
                        <div class="row">
                                <form method="POST" action="{{ url_for('comment', quote_id=quote._id) }}">
                                <div class="input-field">
                                    <input name="comment" id="comment" minlength="3" type="text">
                                    <label for="comment"><i class="fas fa-search search-label"></i> Make a
                                        comment</label>
                                </div>
                            </form>
                        </div>
                    </div>
                </li>
                
                
            </ul>
        </div>
        <!-- Modal Structure-->
        <div id="modal{{quote._id}}" class="modal">
            <div class="modal-content">
                <h3>Confirm Delete</h3>
                <h5>Are you sure that you want to delete this quote?</h5>
                <p>(Comments will also be deleted).</p>
            </div>
            <div class="modal-footer">
                <a href="#!" class="modal-close btn blue text-shadow">
                    Cancel<i class="far fa-times-circle right"></i></a>
                <a href="{{ url_for('delete_quote', quote_id=quote._id, delete_theme=quote.theme) }}" class="modal-close btn red text-shadow">
                    Delete<i class="fas fa-times-circle right"></i></a>
            </div>
        </div>
    </li>
    {% endfor %}
</ul>

{% else %}
<h4 class="red-text text-darken-4 center-align">You have not added any quotes yet. Click <a
        href="{{ url_for('add_quote') }}"> here </a>to add a quote.</h4>
{% endif %}

{% endblock %}