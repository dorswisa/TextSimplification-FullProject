
var http = require('http');
var express = require('express');
var session = require('express-session');
var bodyParser = require('body-parser');
var cookieParser = require('cookie-parser');
var MongoStore = require('connect-mongo')(session);
var cors = require('cors')
var axios = require('axios')

var app = express();

app.locals.pretty = true;
app.set('port', process.env.PORT || 3000);
app.set('views', __dirname + '/app/server/views');
app.set('view engine', 'pug');
app.use(cookieParser());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(require('stylus').middleware({ src: __dirname + '/app/public' }));
app.use(express.static(__dirname + '/app/public'));
app.use(cors())

// build mongo database connection url //

process.env.DB_HOST = process.env.DB_HOST || 'localhost'
process.env.DB_PORT = process.env.DB_PORT || 27017;
process.env.DB_NAME = process.env.DB_NAME || 'TextSimplification';

if (app.get('env') != 'live'){
	process.env.DB_URL = 'mongodb+srv://ICBUSER:80T1275i394csZE3@cluster0.gitpd.mongodb.net/test';
}	else {
// prepend url with authentication credentials //
	process.env.DB_URL = 'mongodb+srv://ICBUSER:80T1275i394csZE3@cluster0.gitpd.mongodb.net/test';
}

app.use(session({
		secret: 'faeb4453e5d14fe6f6d04637f78077c76c73d1b4',
		proxy: true,
		resave: true,
		saveUninitialized: true,
		store: new MongoStore({ url: process.env.DB_URL })
	})
);

var DBM = require('./app/server/modules/manager');

app.get('/', function(req, res){
	res.redirect('/home');
});

app.get('/home', function(req, res) {
	if (req.session.user == null && req.cookies.login != null) {
		DBM.validateLoginKey(req.cookies.login, req.ip, function (e, o) {
			if (o) {
				DBM.autoLogin(o.email, o.pass, function (o) {
					req.session.user = o;
				});
			}
		});
	}
	res.render('home', {udata: req.session.user});
});

app.post('/login', function(req, res){
	DBM.manualLogin(req.body['signin-email'], req.body['signin-password'], function(e, o){
		if (!o){
			res.status(400).send(e);
		}	else{
			req.session.user = o;
			if (req.body['remember-me'] != 'on'){
				res.status(200).send(o);
			}	else{
				DBM.generateLoginKey(o.email, req.ip, function(key){
					res.cookie('login', key, { maxAge: 900000 });
					res.status(200).send(o);
				});
			}
		}
	});
});

app.post('/logout', function(req, res)
{
	res.clearCookie('login');
	req.session.destroy(function(e){ res.status(200).send('ok'); });
});

app.get('/edit-user', function(req, res) {
	if (req.session.user == null){
		res.redirect('/');
	}	else{
		res.render('edit-user', {
			udata : req.session.user
		});
	}
});

app.get('/users-manager', function(req, res) {
	if (req.session.user == null){
		res.redirect(url+'/');
	}	else{
		DBM.getAllUsers(function(e, users) {
			res.render('users-manager', {
				udata: req.session.user,
				users: users
			});
		});
	}
});

app.post('/edit-user', function(req, res){
	if (req.session.user == null){
		res.redirect('/');
	}	else{
		DBM.updateAccount( req.session.user._id,{
			name	: req.body['edit-username'],
			email	: req.body['edit-email'],
			pass	: req.body['edit-password']
		}, function(e, o){
			if (e){
				res.status(400).send(e);
			}	else{
				req.session.user = o;
				res.status(200).send('ok');
			}
		});
	}
});

app.post('/delete-myuser', function(req, res){
	DBM.deleteMyAccount(req.session.user._id, function(e, obj){
		if (!e){
			res.clearCookie('login');
			req.session.destroy(function(e){ res.status(200).send('ok'); });
		}	else{
			res.status(400).send('record not found');
		}
	});
});

app.post('/delete-user', function(req, res){
	if (req.session.user == null){
		res.redirect('/');
	}
	else if(req.session.user.class != "admin")
	{
		res.status(400).send("error");
	}
	else{
		DBM.deleteAccount(req.body['email'], function(e){
			if (e){
				res.status(400).send(e);
			}	else{
				res.status(200).send('ok');
			}
		});
	}
});

app.post('/tokenize', function (req, res) {
	axios.post("http://34.76.106.188:8000/yap/heb/joint", req.body.body)
	.then(function (response) {
		res.send(response.data)
	})
	.catch(function (error) {
		res.send(error)
	});
});

app.get('*', function(req, res) { res.render('home'); });

http.createServer(app).listen(app.get('port'), function(){
	console.log('Express server listening on port ' + app.get('port'));
});

