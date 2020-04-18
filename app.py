###		imports		###

from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import json
from pprint import pprint
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators
from wtforms.validators import DataRequired, Email
from cassandra.cluster import Cluster
import requests_cache
import hashlib


###		FlaskForms		###

class LiveForm(FlaskForm):
	message = StringField(u'currency pair (e.g. EURGBP):', validators=[DataRequired()])

class HistForm(FlaskForm):
	message_h = StringField(u'currency pair (e.g. EURGBP):', validators=[DataRequired()])
	date = StringField(u'date (yyyy-mm-dd):', validators=[DataRequired()])

class CryptoForm(FlaskForm):
	message = StringField(u'crypto (e.g. BTCUSD):', validators=[DataRequired()])

class JournalForm(FlaskForm):
	apikey = StringField(u'your API key:', validators=[DataRequired()])
	entry_id = StringField(u'entry id:', validators=[DataRequired()])
	time_o = StringField(u'start time (yyyy-mm-dd hh:mm):', validators=[DataRequired()])
	time_c = StringField(u'close time (yyyy-mm-dd hh:mm):', validators=[DataRequired()])
	pair = StringField(u'currency pair (e.g. GBPUSD):', validators=[DataRequired()])
	price_o = StringField(u'start position price (1.xxxxx):', validators=[DataRequired()])
	price_c = StringField(u'close position price (1.xxxxx):', validators=[DataRequired()])
	buysell = StringField(u'type (buy/sell):', validators=[DataRequired()])
	vol = StringField(u'volume (x.xx):', validators=[DataRequired()])

class RegForm(FlaskForm):
	name = StringField(u'please enter your name:', validators=[DataRequired()])
	email = StringField(u'please enter your email:', validators=[DataRequired(), Email()])
	password = PasswordField(u'please enter your password:', validators=[DataRequired()])

class LoginForm(FlaskForm):
	email = StringField(u'please enter your email:', validators=[DataRequired(), Email()])
	password = PasswordField(u'please enter your password:', validators=[DataRequired()])



requests_cache.install_cache('forex_cache', backend='sqlite', expire_after=36000)
cluster = Cluster(contact_points=['172.17.0.2'], port=9042)
session = cluster.connect('journal')

###		Services		###

app = Flask(__name__)
app.secret_key = '!!!-_-Alohomora-_-!!!'

@app.route('/')
def home():
	return render_template('Home.html')


@app.route('/forex/', methods=['GET', 'POST'])
def get_ticker():
	form_live = LiveForm(request.form)				# live data form - user enters the currency pair symbol
	form_hist = HistForm(request.form) 				# historical data form - user enters the currency pair symbol and the date 
	if request.method == 'POST' and form_live.validate_on_submit():
		requested_ticker_live = str(form_live.message.data)				# currency pair symbol
		ticker_live_url = 'https://financialmodelingprep.com/api/v3/forex/{}'.format(requested_ticker_live) # external API address containing the user's requested currency pair
		resp_ticker_live = requests.get(ticker_live_url).json()				# get the results from the external API and convert to json
		if  resp_ticker_live != {}:				# because if the requested currency pair is not correct, the external API just returns {}
			return render_template('Forex.html', formlive=form_live, formhist=form_hist, resultslive=resp_ticker_live)
		else:
			return jsonify({'Response': 'Fail! 404', 'results':'Currency pair not found!'})


	if request.method == 'POST' and form_hist.validate_on_submit():
		requested_ticker_hist = str(form_hist.message_h.data)
		requested_date = str(form_hist.date.data)
		ticker_hist_url = 'https://financialmodelingprep.com/api/v3/historical-price-full/forex/{}'.format(requested_ticker_hist)
		resp_ticker_hist = requests.get(ticker_hist_url).json()
		resp_ticker_hist_date = list(filter(lambda x:x["date"]==requested_date, resp_ticker_hist['historical']))
		if  resp_ticker_hist_date != {}:
			return render_template('Forex.html', formlive=form_live, formhist=form_hist, resultshist=resp_ticker_hist_date)
		else:
			return jsonify({'Response': 'Fail! 404', 'results':'Currency pair not found!'})

	return render_template('Forex.html', formlive=form_live, formhist=form_hist)



@app.route('/crypto/', methods=['GET', 'POST'])
def get_crypto():
	form_live = CryptoForm(request.form)
	if request.method == 'POST' and form_live.validate_on_submit():
		requested_crypto = str(form_live.message.data)
		crypto_url = 'https://financialmodelingprep.com/api/v3/quote/{}'.format(requested_crypto)
		resp_crypto = requests.get(crypto_url).json()
		if  resp_crypto != []:
			if resp_crypto[0]['changesPercentage'] > 0:
				pred = '💴🔺 BUY'
			else: pred = '💴🔻 SELL'
			return render_template('Crypto.html', formlive=form_live, resultslive=resp_crypto[0], pred=pred)
		else:
			return jsonify({'Response': 'Fail! 404', 'results':'Crypto pair not found!'})
	return render_template('Crypto.html', formlive=form_live)


@app.route('/register/', methods=['GET', 'POST'])
def register():
	form = RegForm(request.form)
	if request.method == 'POST' and form.validate_on_submit():
		name = form.name.data
		email = form.email.data
		password = form.password.data
		u = email + password
		apikey = hashlib.sha256(u.encode('utf-8')).hexdigest()
		password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
		user_check = session.execute("""select COUNT(*) from journal.users where email='{}' ALLOW FILTERING""".format(email))
		if user_check.was_applied == 0:
			query = "INSERT INTO journal.users(name, email, password, apikey) VALUES ('{}', '{}', '{}', '{}')".format(name, email, password_hash, apikey)
			session.execute(query)
			return render_template('Register.html', msg='successful! 201', APIKey='your API Key is:  '+apikey)
		else:
			return render_template('Register.html', msg_fail='failed! Username taken :( 409')
	return render_template('Register.html', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
	form = LoginForm(request.form)
	if request.method == 'POST' and form.validate_on_submit():
		email = form.email.data
		password = form.password.data
		u = email + password
		apikey = hashlib.sha256(u.encode('utf-8')).hexdigest()
		login_check = session.execute("""select COUNT(*) from journal.users where apikey='{}' ALLOW FILTERING""".format(apikey))
		if login_check.was_applied == 1:
			return render_template('Login.html', msg='successful!')
		else:
			return render_template('Login.html', msg_fail='failed! Wrong username or password 401')
	return render_template('Login.html', form=form)



@app.route('/journal/', methods=['GET', 'POST'])
def journal():
	form = JournalForm(request.form)
	if request.method == 'POST' and form.validate_on_submit():
		apikey = form.apikey.data #############
		entry_id = form.entry_id.data #############
		pair = form.pair.data
		type = form.buysell.data
		vol = form.vol.data
		time_o = form.time_o.data
		time_c = form.time_c.data
		price_o = form.price_o.data
		price_c = form.price_c.data
		if type == 'buy':
			sgn = 1
		else:
			sgn = -1
		profit = (float(price_c) - float(price_o))*float(vol)*100000*sgn
		user_check = session.execute("""SELECT COUNT(*) from journal.users where apikey='{}' ALLOW FILTERING""".format(apikey))
		if user_check.was_applied == 1:
			id_check = session.execute("""SELECT COUNT(*) from journal.entry_records where api__id='{}' ALLOW FILTERING""".format(str(apikey)+'--'+str(entry_id)))
			if id_check.was_applied == 0:
				query = "INSERT INTO journal.entry_records(apikey, api__id, id, pair, type, volume, start_time, close_time, start_price, close_price, profit) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(apikey, str(apikey)+'--'+str(entry_id), entry_id, pair, type, vol, time_o, time_c, price_o, price_c, profit)
				session.execute(query)
				query_res = "SELECT * from journal.entry_records where apikey='{}'".format(apikey)
				res = session.execute(query_res)
				table = [['id', 'pair', 'type', 'volume', 'close time', 'profit']]
				for row in res:
					new_entry = [row[2], row[5], row[9], row[10], row[4], row[6]]
					table.append(new_entry)
				return render_template('Journal.html', form=form, res=table)
			else:
				return(jsonify({'Response': 'Fail! 409', 'results':'entry id already exists!'}))
		else:
			return(jsonify({'Response': 'Fail! 401', 'results':'incorrect API key!!'}))
	return render_template('Journal.html', form=form)



@app.route('/del_entry/', methods=['DELETE'])
def delete_entry():
	if 'apikey' in request.json:
		if 'id' in request.json:
			apikey = request.json['apikey']
			entry_id = request.json['id']
			api__id = str(apikey)+'--'+str(entry_id)
			user_check = session.execute("""select COUNT(*) from journal.entry_records where apikey='{}' ALLOW FILTERING""".format(apikey))
			if user_check.was_applied != 0:
				id_check = session.execute("""select COUNT(*) from journal.entry_records where api__id='{}' ALLOW FILTERING""".format(api__id))
				if id_check.was_applied != 0:
					query = "DELETE from journal.entry_records where apikey='{}' AND api__id='{}'".format(apikey, api__id)
					session.execute(query)
				else:
					return jsonify({'Response': 'Fail! 404', 'results':'no entry with this id!'})

				return jsonify({'Response': 'Success! 200', 'results':'Entry deleted!'})
			else:
				return jsonify({'Response': 'Fail! 401', 'results':'wrong API key!'})
		else:
			return jsonify({'Response': 'Fail! 400', 'results':'entry id needed!'})
	else:
		return jsonify({'Response': 'Fail! 400', 'results':'API key needed!'})


@app.route('/update_entry/', methods=['PUT'])
def update_entry():
	if 'apikey' in request.json:
		if 'id' in request.json:
			apikey = request.json['apikey']
			entry_id = request.json['id']
			api__id = str(apikey)+'--'+str(entry_id)
			pair = request.json['pair']
			buysell = request.json['type']
			vol = request.json['volume']
			t_o = request.json['open_time']
			t_c = request.json['close_time']
			p_o = request.json['open_price']
			p_c = request.json['close_price']
			if type == 'buy':
				sgn = 1
			else:
				sgn = -1
			profit = (float(p_c) - float(p_o))*float(vol)*100000*sgn
			user_check = session.execute("""select COUNT(*) from journal.entry_records where apikey='{}' ALLOW FILTERING""".format(apikey))
			if user_check.was_applied != 0:
				id_check = session.execute("""select COUNT(*) from journal.entry_records where api__id='{}' ALLOW FILTERING""".format(api__id))
				if id_check.was_applied != 0:
					query = "UPDATE journal.entry_records SET close_price='{}', close_time='{}', pair='{}', profit='{}', start_price='{}', start_time='{}', type='{}', volume='{}' where apikey='{}' AND api__id='{}' AND id='{}'".format(p_c, t_c, pair, profit, p_o, t_o, buysell, vol, apikey, api__id, entry_id)
					session.execute(query)
					return jsonify({'Response': 'Success! 200', 'results':'Entry updated!'})
				else:
					return jsonify({'Response': 'Fail! 404', 'results':'no entry with this id!'})
			else:
				return jsonify({'Response': 'Fail! 401', 'results':'wrong API key!'})
		else:
			return jsonify({'Response': 'Fail! 400', 'results':'entry id needed!'})
	else:
		return jsonify({'Response': 'Fail! 400', 'results':'API key needed!'})


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80, debug=True)
