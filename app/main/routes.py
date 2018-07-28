from flask import render_template, g, request, current_app, url_for
from flask_login import current_user, login_required
from app.main import bp
from app.main.forms import SearchForm
from app.models import Patient

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        g.search_form = SearchForm()

@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    patients, total = Patient.search(g.search_form.q.data, page,
                                current_app.config['PATIENTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page+1) \
        if total > page * current_app.config['PATIENTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page-1) \
        if page > 1 else None
    return render_template('search.html', title='Search', patients=patients,
                            next_url=next_url, prev_url=prev_url)
