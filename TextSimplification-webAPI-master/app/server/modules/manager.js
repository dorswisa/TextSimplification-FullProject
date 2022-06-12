const crypto 		= require('crypto');
const MongoClient 	= require('mongodb').MongoClient;

var db, users, words;
MongoClient.connect(process.env.DB_URL, { useUnifiedTopology: true, useNewUrlParser: true }, function(e, client) {
	if (e){
		console.log(e);
	}	else{
		db = client.db(process.env.DB_NAME);
		users = db.collection('Users');
		words = db.collection('Words');
		// index fields 'user' & 'email' for faster new account validation //
		users.createIndex({user: 1, email: 1});
		words.createIndex({word: 1, syn: 1});
		console.log('mongo :: connected to database :: "'+process.env.DB_NAME+'"');
		users.findOne({email:"dormo1@ac.sce.ac.il"}, function(e, o) {					// insert admin user
			if (o == null) {
				users.insertOne({
					name: "Dor Swisa",
					email: "dormo1@ac.sce.ac.il",
					pass: "aUmcRG0F0Gfed7118d6e923bc42e36116c4da69b48",					// 123456
					class: "admin",
				});
				users.insertOne({
					name: "Ami Bitan",
					email: "amibi@ac.sce.ac.il",
					pass: "aUmcRG0F0Gfed7118d6e923bc42e36116c4da69b48",					// 123456
					class: "admin",
				});
				users.insertOne({
					name: "Tamir Abutbul",
					email: "abutbab1@ac.sce.ac.il",
					pass: "aUmcRG0F0Gfed7118d6e923bc42e36116c4da69b48",					// 123456
					class: "admin",
				});
			}
		});
	}
});

const guid = function(){return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {var r = Math.random()*16|0,v=c=='x'?r:r&0x3|0x8;return v.toString(16);});}

/*
	login validation methods
*/

exports.autoLogin = function(email, pass, callback)
{
	users.findOne({email:email}, function(e, o) {
		if (o){
			o.pass == pass ? callback(o) : callback(null);
		}	else{
			callback(null);
		}
	});
}

exports.manualLogin = function(email, pass, callback)
{
	users.findOne({email:email}, function(e, o) {
		if (o == null){
			console.log(email + " Not found in the data base!");
			callback('user-not-found');
		}	else{
			validatePassword(pass, o.pass, function(err, res) {
				if (res){
					console.log("Connecting to: "+ email);
					callback(null, o);
				}	else{
					console.log(email + " found but the password does not match!");
					callback('invalid-password');
				}
			});
		}
	});
}

exports.generateLoginKey = function(email, ipAddress, callback)
{
	let cookie = guid();
	users.findOneAndUpdate({email:email}, {$set:{
		ip : ipAddress,
		cookie : cookie
	}}, {returnOriginal : false}, function(e, o){ 
		callback(cookie);
	});
}

exports.validateLoginKey = function(cookie, ipAddress, callback)
{
// ensure the cookie maps to the user's last recorded ip address //
	users.findOne({cookie:cookie, ip:ipAddress}, callback);
}

exports.generatePasswordKey = function(email, ipAddress, callback)
{
	let passKey = guid();
	users.findOneAndUpdate({email:email}, {$set:{
		ip : ipAddress,
		passKey : passKey
	}, $unset:{cookie:''}}, {returnOriginal : false}, function(e, o){
		if (o.value != null){
			callback(null, o.value);
		}	else{
			callback(e || 'account not found');
		}
	});
}

exports.validatePasswordKey = function (passKey, ipAddress, callback) {
// ensure the passKey maps to the user's last recorded ip address //
	users.findOne({passKey:passKey, ip:ipAddress}, callback);
}

/*
	record insertion, update & deletion methods
*/
/*
exports.addNewMovie = function(newData, callback)
{
	movies.findOne({title:newData.title}, function(e, o) {
		if (o){
			console.log(newData.title + " already in database!");
			callback('movie-already-in-database');
		}
		else
		{
			console.log(newData.title + " has been added to database!");
			movies.insertOne(newData, callback);
		}
	});
}

exports.addNewScreening = function(newData, callback)
{
	screenings.findOne({date:moment(newData.date, "DD/MM/YYYY").toDate(), hall:newData.hall, time:newData.time}, function(e, o) {
		if (o){
			console.log("There is already a screening at " + newData.date + " - " + newData.time + " in hall " + newData.hall + "!");
			callback('too-many-screenings-at-a-time');
		}
		else
		{
			newData.seats = {};
			if(newData.hall.includes("VIP"))
			{
				for(var j='A'; j<='F'; j = String.fromCharCode(j.charCodeAt(0) + 1) )
				{
					for(var i=1; i<=5; i++)
					{
						newData.seats[""+j+i] = undefined;
					}
				}
				if(newData.price < 100)
				{
					newData.sale = true;
				}
				else
				{
					newData.sale = false;
				}
			}
			else if (newData.hall.includes("IMAX"))
			{
				for(var j='A'; j<='R'; j = String.fromCharCode(j.charCodeAt(0) + 1) )
				{
					for(var i=1; i<=18; i++)
					{
						newData.seats[""+j+i] = undefined;
					}
				}
				if(newData.price < 60)
				{
					newData.sale = true;
				}
				else
				{
					newData.sale = false;
				}
			}
			else
			{
				for(var j='A'; j<='I'; j = String.fromCharCode(j.charCodeAt(0) + 1) )
				{
					for(var i=1; i<=18; i++)
					{
						newData.seats[""+j+i] = undefined;
					}
				}
				if(newData.price < 50)
				{
					newData.sale = true;
				}
				else
				{
					newData.sale = false;
				}
			}
			newData.date = moment(newData.date, "DD/MM/YYYY").toDate();
			console.log("The Screening " + newData.movie + " - " + newData.date + ", " + newData.time + " has been added to database!");
			screenings.insertOne(newData, callback);
		}
	});
}

exports.getScreening = function(id, callback)
{
	screenings.findOne({_id:getObjectId(id)}, function(e, o) {
		if(o)
		{
			for (var key in o.seats) {
				if(o.seats[key] != null && typeof o.seats[key] === 'string' && o.seats[key] < new Date().getTime())
				{
					o.seats[key] = null;
				}
			}
			screenings.findOneAndUpdate({_id: getObjectId(id)}, {$set: o}, {returnOriginal: false}, callback(null, o));
		}
		else callback(e)
	});
}

exports.getMovie = function(title, callback)
{
	movies.findOne({title:title}, function(e, o) {
		if(o) callback(null, o)
		else callback(e)
	});
}

exports.updateSeats = function(newData, callback)
{
	screenings.findOne({_id:getObjectId(newData.screenId)}, function(e, o) {
		if (o) {
			var flag = false;
			if(newData.expiry != 'null')
			{
				newData.seats.forEach(el => o.seats[el] == null ? o.seats[el] = newData.expiry : flag = true);
				if(flag)
					callback('seat-taken');
				else
					screenings.findOneAndUpdate({_id: getObjectId(newData.screenId)}, {$set: o}, {returnOriginal: false}, callback(null, o));
			}
			else
			{
				newData.seats.forEach(el => o.seats[el] = null);
				screenings.findOneAndUpdate({_id: getObjectId(newData.screenId)}, {$set: o}, {returnOriginal: false}, callback(null, o));
			}

		}
		else
		{
			callback('not-found');
		}
	});
}

exports.updateMovie = function(newData, callback)
{
	movies.findOne({title:newData.title}, function(e, o) {
		if (o) {
			newData._id = o._id;
			var oldtitle = newData.title;
			newData.title = newData.newtitle;
			delete newData.newtitle;
			movies.findOneAndUpdate({title: oldtitle}, {$set: newData}, {returnOriginal: false});
			screenings.find({movie:oldtitle}).toArray(function(e, res) {
				for(var i=0;i<res.length; i++)
				{
					res[i].movie = newData.title;
					screenings.findOneAndUpdate({_id: res[i]._id}, {$set: res[i]}, {returnOriginal: false});
				}
			});
			callback(null);
		}
		else
		{
			callback('not-found');
		}
	});
}*/

exports.updateUser = function(email,newData, callback)
{
	users.findOne({email:newData.email}, function(e, o) {
		if (o && o.email != email) {
			console.log(newData.email + " is taken!");
			callback('email-taken');
		}
		else
		{
			users.findOne({email:email}, function(e, o) {
				if(newData.pass != "")
				{
					saltAndHash(newData.pass, function(hash){
						o.pass = hash;
						o.name = newData.name;
						o.email = newData.email;
						o.class = newData.class;
						users.findOneAndUpdate({email:email}, {$set:o}, {returnOriginal : false}, callback(null,o));
					});
				}
				else
				{
					o.name = newData.name;
					o.email = newData.email;
					o.class = newData.class;
					users.findOneAndUpdate({email:email}, {$set: o}, {returnOriginal: false}, callback(null, o));
				}
			});
		}
	});
}

exports.CreateNewUser = function(newData, callback)
{
	users.findOne({email:newData.email}, function(e, o) {
		if (o){
			console.log(newData.email + " is taken!");
			callback('user-taken');
		}
		else{
				saltAndHash(newData.pass, function (hash) {
					newData.pass = hash;
					console.log(newData.name + " has been created in database!");
					users.insertOne(newData, callback);
			});
		}
	});
}

exports.CreateNewWord = function(newData, callback)
{
	words.findOne({word:newData.word, pos:newData.pos}, function(e, o) {
		if (o){
			if(o.syn.includes(newData.syn))
			{
				console.log(newData.word +" - " + newData.syn + " is already in database!");
				callback('already in database');
			}
			else {
				o.syn.unshift(newData.syn);
				o.rating.unshift([]);
				words.findOneAndUpdate({word:newData.word, pos:newData.pos}, {$set: o}, {returnOriginal: false}, callback(null, o));
			}
		}
		else{
			o = {};
			o.word = newData.word;
			o.pos = newData.pos;
			o.syn = [];
			o.syn.unshift(newData.syn);
			o.rating = [];
			o.rating.unshift([]);
			console.log(newData.word + " - " + newData.syn + " has been created in database!");
			words.insertOne(o, callback);
		}
	});
}

exports.updatePassword = function(passKey, newPass, callback)
{
	saltAndHash(newPass, function(hash){
		newPass = hash;
		users.findOneAndUpdate({passKey:passKey}, {$set:{pass:newPass}, $unset:{passKey:''}}, {returnOriginal : false}, callback);
	});
}

exports.deleteMyUser = function(id, callback)
{
	console.log("The user has been deleted!");
	users.deleteOne({_id: getObjectId(id)}, callback);
}

exports.deleteUser = function(email, callback)
{
	users.findOne({email:email}, function(e, o) {
		if (o) {
			users.deleteOne({email: email});
			console.log("The user" + email + " has been deleted!");
			callback(null);
		}
		else
		{
			callback('not-found');
		}
	});
}

exports.deleteWord = function(wordsynpos, callback)
{
	wordsynpos = wordsynpos.split("-");
	let word = wordsynpos[0];
	let syn = wordsynpos[1];
	let pos = wordsynpos[2];
	words.findOne({word:word, pos:pos}, function(e, o) {
		if (o) {
			if(o.syn.length == 1)
			{
				words.deleteOne({word:word, pos:pos});
				console.log("The word " + word + pos + " has been deleted!");
				callback(null);
			}
			else
			{
				let index = o.syn.indexOf(syn);
				o.syn.splice(index, 1);
				o.rating.splice(index,1);
				words.findOneAndUpdate({word:word, pos:pos}, {$set: o}, {returnOriginal: false}, callback(null, o));
			}
		}
		else
		{
			callback('not-found');
		}
	});
}

exports.getAllUsers = function(callback)
{
	users.find().toArray(
		function(e, res) {
			if (e) callback(e)
			else callback(null, res);
		});
}

exports.getAllWords = function(callback)
{
	words.find().toArray(
		function(e, res) {
			if (e) callback(e)
			else callback(null, res);
		});
}

/*
	private encryption & validation methods
*/

var generateSalt = function()
{
	var set = '0123456789abcdefghijklmnopqurstuvwxyzABCDEFGHIJKLMNOPQURSTUVWXYZ';
	var salt = '';
	for (var i = 0; i < 10; i++) {
		var p = Math.floor(Math.random() * set.length);
		salt += set[p];
	}
	return salt;
}

var md5 = function(str) {
	return crypto.createHash('md5').update(str).digest('hex');
};

var saltAndHash = function(pass, callback)
{
	var salt = generateSalt();
	callback(salt + md5(pass + salt));
};

var validatePassword = function(plainPass, hashedPass, callback)
{
	var salt = hashedPass.substr(0, 10);
	var validHash = salt + md5(plainPass + salt);
	callback(null, hashedPass === validHash);
};

var getObjectId = function(id)
{
	return new require('mongodb').ObjectID(id);
};
