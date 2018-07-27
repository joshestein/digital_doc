from app import create_app, db
from app.models import Doctor, Patient

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'Doctor': Doctor, 'Patient':Patient}
