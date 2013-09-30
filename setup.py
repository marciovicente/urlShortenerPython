from flask import Flask, render_template, url_for, request, redirect, flash
import redis
import string
import random

app = Flask(__name__)
app.secret_key = 'uQv8EhIAx1hCTFCQNoFgCACtEQWUfnQy'

r = redis.StrictRedis(host='localhost', port=6379, db=0)

URL_ID = 'count'


def generate_alias(id):
	# encode the url and return
	return ''.join(random.choice(string.ascii_letters + string.digits + str(id)) for i in range(6))


# routes and methods
@app.route('/')
def index():
	num_registros = r.lrange('records', 0, -1)
	urls = []
	for i in num_registros:
		urls.append(r.hgetall('urls:%s' % i))
	# error
	return render_template('index.html', alias=None, registros=num_registros, urls=urls)

@app.route('/save/', methods=['POST'])
def save_url():
	if request.method == 'POST':
		url = request.form['url']
		id = int(r.incr(URL_ID))
		alias = generate_alias(id)
		record = {'alias': alias, 'url': url}
		r.hset('urls:%d' % id, 'alias', alias)
		r.hset('urls:%d' % id, 'url', url)
		r.lpush('records', id) 
		flash('http://localhost:5000/%s' % alias)

	return redirect(url_for('index'))

@app.route('/<string:alias>/')
def find(alias):
	num_registros = r.lrange('records', 0, -1)
	url = None
	for id in num_registros:
		record_alias = r.hget('urls:%s' % id, 'alias')
		if record_alias == alias:
			url = r.hget('urls:%s' % id, 'url')
	if url:
		return redirect(url)
	else:
		return False
# run the app
if __name__ == '__main__':
	app.run(debug=True)