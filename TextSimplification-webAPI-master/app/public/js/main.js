
(function() {

	var bodyEl = document.body,
		content = document.querySelector( '.content-wrap' ),
		openbtn = document.getElementById( 'open-button' ),
		isOpen = false;

	function init() {
		initEvents();
	}

	function initEvents() {
		openbtn?.addEventListener( 'click', toggleMenu );

		// close the menu element if the target it´s not the menu element or one of its descendants..
		content.addEventListener( 'click', function(ev) {
			var target = ev.target;
			if( isOpen && target !== openbtn ) {
				toggleMenu();
			}
		} );
	}

	function toggleMenu() {
		if( isOpen ) {
			classie.remove( bodyEl, 'show-menu' );
		}
		else {
			classie.add( bodyEl, 'show-menu' );
		}
		isOpen = !isOpen;
	}

	init();

})();


jQuery(document).ready(function($){

	var $form_modal = $('.cd-user-modal'),
		$form_login = $form_modal.find('#cd-login');

	//open modal
	$('.cd-login').on('click', function(){
		$('.openSidebarMenu').prop('checked', false);
		$form_modal.addClass('is-visible');
		//show the selected form
		$form_login.addClass('is-selected');

	});


	//close modal
	$('.cd-close-form').on('click', function(event){
		$form_modal.removeClass('is-visible');
	});

	//close modal when clicking the esc keyboard button
	$(document).keyup(function(event){
		if(event.which=='27'){
			$form_modal.removeClass('is-visible');
		}
	});


	//hide or show password
	$('.hide-password').on('click', function(){
		var $this= $(this),
			$password_field = $this.prev().prev('input');

		( 'password' === $password_field.attr('type') ) ? $password_field.attr('type', 'text') : $password_field.attr('type', 'password');
		( '/css/visibility.png' === $this.children("img").attr('src') ) ? $this.children("img").attr('src','/css/invisible.png') : $this.children("img").attr('src','/css/visibility.png');
		//focus and move cursor to the end of input field
		$password_field.putCursorAtEnd();
	});


	$('#cd-login').ajaxForm({
		type: 'POST',
		url: '/login',
		success: function (responseText, status, xhr, $form) {
			if (status == 'success') window.location.href = '/home';
		},
		error: function (e) {
			$('#alert-modal-title').html('Login Failure!');
			$('#alert-modal-body').html('Please check your username and/or password.');
			$('#alert-modal').modal('show');
		}
	});

	$('#btn-delete').click(function () {
		$('#delete-modal-title').html('Warning!');
		$('#delete-modal-body').html('Are you sure you want to delete your account?.');
		$('#delete-modal').modal('show');
	});


	$('#btn-logout, #btn-logout2').click(function () {
		console.log("wow");
		$.ajax({
			url: '/logout',
			type: 'POST',
			data: {logout: true},
			xhrFields: {
				withCredentials: true
			},
			success: function (data) {
				$('#alert-modal-title').html('Log-Out Successful!');
				$('#alert-modal-body').html('Redirecting you back to the homepage.');
				$('#alert-modal').modal('show');
				setTimeout(function () {
					window.location.href = '/';
				}, 3000);
			},
			error: function (jqXHR) {
				console.log(jqXHR.responseText + ' :: ' + jqXHR.statusText);
			}
		});
	});

	$('#edit-user-form').ajaxForm({
		type: 'POST',
		url: '/edit-user',
		success: function (responseText, status, xhr, $form) {
			if (status == 'success'){
				$('#alert-modal-title').html('Edit Successful!');
				$('#alert-modal-body').html('Your account has been edited.. <br>Redirecting you back to the homepage.');
				$('#alert-modal').modal('show');
				setTimeout(function(){window.location.href = '/';}, 3000);
			}
		},
		error: function (e) {
			$('#alert-modal-title').html('Edit Failure!');
			$('#alert-modal-body').html('The email address has already been allocated to another user.');
			$('#alert-modal').modal('show');
		}
	});

	$('#delete-access').click(function () {
		$('#delete-modal').modal('hide');
		$.ajax({
			url: '/delete-myuser',
			type: 'POST',
			success: function (data) {
				$('#alert-modal-title').html('Delete successful!');
				$('#alert-modal-body').html('Your account has been deleted.<br>Redirecting you back to the homepage.');
				$('#alert-modal').modal('show');
				setTimeout(function () {
					window.location.href = '/';
				}, 3000);
			},
			error: function (jqXHR) {
				console.log(jqXHR.responseText + ' :: ' + jqXHR.statusText);
			}
		});
	});

});


//credits https://css-tricks.com/snippets/jquery/move-cursor-to-end-of-textarea-or-input/
jQuery.fn.putCursorAtEnd = function() {
	return this.each(function() {
		// If this function exists...
		if (this.setSelectionRange) {
			// ... then use it (Doesn't work in IE)
			// Double the length because Opera is inconsistent about whether a carriage return is one character or two. Sigh.
			var len = $(this).val().length * 2;
			this.setSelectionRange(len, len);
		} else {
			// ... otherwise replace the contents with itself
			// (Doesn't work in Google Chrome)
			$(this).val($(this).val());
		}
	});
};
