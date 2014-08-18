from nblog import app

@app.template_filter('to_date')
def to_date(d):
    return d.strftime('%Y-%m-%d')
