(function ($) {

    "use strict";

    var $document = $(document),
        $window = $(window),
        forms = {
            contactForm: $('#contactForm'),
            questionForm: $('#questionForm'),
            bookForm: $('#bookForm'),
            loginForm: $('#loginForm'),
            registerForm: $('#registerForm')
        };

    $document.ready(function () {

            // datepicker
            if ($('.datetimepicker').length) {
                $('.datetimepicker').datetimepicker({
                    format: 'DD/MM/YYYY',
                    ignoreReadonly: true,
                    icons: {
                        time: 'icon icon-clock',
                        date: 'icon icon-calendar2',
                        up: 'icon icon-top',
                        down: 'icon icon-bottom',
                        previous: 'icon icon-left',
                        next: 'icon icon-right',
                        today: 'icon icon-tick',
                        clear: 'icon icon-close',
                        close: 'icon icon-close'
                    }
                });
            }
            if ($('.timepicker').length) {
                $('.timepicker').datetimepicker({
                    format: 'LT',
                    ignoreReadonly: true,
                    icons: {
                        time: 'icon icon-clock',
                        up: 'icon icon-top',
                        down: 'icon icon-bottom',
                        previous: 'icon icon-left',
                        next: 'icon icon-right'
                    }
                });
            }

            // contact form
            if (forms.contactForm.length) {
                var $contactform = forms.contactForm;
                $contactform.validate({
                    rules: {
                        name: {
                            required: true,
                            minlength: 2
                        },
                        message: {
                            required: true,
                            minlength: 20
                        },
                        email: {
                            required: true,
                            email: true
                        }

                    },
                    messages: {
                        name: {
                            required: "Please enter your name",
                            minlength: "Your name must consist of at least 2 characters"
                        },
                        message: {
                            required: "Please enter message",
                            minlength: "Your message must consist of at least 20 characters"
                        },
                        email: {
                            required: "Please enter your email"
                        }
                    },
                    submitHandler: function submitHandler(form) {
                        $(form).ajaxSubmit({
                            type: "POST",
                            data: $(form).serialize(),
                            url: "form/process-contact.php",
                            success: function success() {
                                $('.successform', $contactform).fadeIn();
                                $contactform.get(0).reset();
                            },
                            error: function error() {
                                $('.errorform', $contactform).fadeIn();
                            }
                        });
                    }
                });
            }

            // question form
            if (forms.questionForm.length) {
                var $questionForm = forms.questionForm;
                $questionForm.validate({
                    rules: {
                        name: {
                            required: true,
                            minlength: 2
                        },
                        messages: {
                            required: true,
                            minlength: 20
                        },
                        email: {
                            required: true,
                            email: true
                        }
                    },
                    messages: {
                        name: {
                            required: "Please enter your name",
                            minlength: "Your name must consist of at least 2 characters"
                        },
                        message: {
                            required: "Please enter message",
                            minlength: "Your message must consist of at least 20 characters"
                        },
                        email: {
                            required: "Please enter your email"
                        }
                    },
                    submitHandler: function submitHandler(form) {
                        $(form).ajaxSubmit({
                            type: "POST",
                            data: $(form).serialize(),
                            url: "/api/add-questions",
                            success: function success() {
                                $('.successform', $questionForm).fadeIn();
                                $questionForm.get(0).reset();
                            },
                            error: function error() {
                                $('.errorform', $questionForm).fadeIn();
                            }
                        });
                    }
                });
            }

            // booking form
            if (forms.bookForm.length) {
                var $bookForm = forms.bookForm;
                $bookForm.validate({
                    rules: {
                        bookingname: {
                            required: true,
                            minlength: 2
                        },
                        bookingemail: {
                            required: true,
                            email: true
                        }
                    },
                    messages: {
                        bookingname: {
                            required: "Please enter your name",
                            minlength: "Your name must consist of at least 2 characters"
                        },
                        bookingemail: {
                            required: "Please enter your email"
                        }
                    },
                    submitHandler: function submitHandler(form) {
                        $(form).ajaxSubmit({
                            type: "POST",
                            data: $(form).serialize(),
                            url: "/api/add-booking",
                            success: function success() {
                                $('.successform', $bookingForm).fadeIn();
                                $bookingForm.get(0).reset();
                            },
                            error: function error() {
                                $('.errorform', $bookingForm).fadeIn();
                            }
                        });
                    }
                });
            }

            // login form
            if (forms.loginForm.length) {
                var $loginForm = forms.loginForm;
                $loginForm.validate({
                    rules: {
                        email: {
                            required: true,
                            email: true
                        },
                        password: {
                            required: true
                        }
                    },
                    messages: {
                        email: {
                            required: "Please enter your email"
                        },
                        password: {
                            required: "Please enter your password"
                        }
                    },
                    submitHandler: function (form) {
                        $(form).ajaxSubmit({
                            type: "POST",
                            data: $(form).serialize(),
                            url: "/user-login",
                            success: function success(data, textStatus, jqXHR) {
                                window.location.href = data.redirect;
                            },
                            error: function error(jqXHR, textStatus, errorThrown) {
                                alert(textStatus + "\n" + jqXHR.responseJSON.message);
                            }
                        });
                    }
                });
            }

            // register form
            if (forms.registerForm.length) {
                var $registerForm = forms.registerForm;
                $registerForm.validate({
                    rules: {
                        registerName: {
                            required: true
                        },
                        registerEmail: {
                            required: true,
                            email: true,
                            remote: {
                                url: '/api/validate-email',
                                type: "post",
                                data:
                                    {
                                        email: function () {
                                            return $('#registerForm :input[name="registerEmail"]').val();
                                        }
                                    }
                            }
                        },
                        registerPassword: {
                            required: true,
                            minlength: 8
                        },
                        registerConfirmPassword: {
                            required: true,
                            equalTo: registerPassword,
                        }
                    },
                    messages: {
                        registerName: {
                            required: "Please enter your name"
                        },
                        registerEmail: {
                            required: "Please enter your email",
                            remote: jQuery.validator.format("{0} is already taken.")
                        },
                        registerPassword: {
                            required: "Please enter your password",
                            minlength: "your password must be at least 8 characters"
                        },
                        registerConfirmPassword: {
                            required: "Confirm your password",
                            equalTo: "Passwords must match."
                        }
                    },
                    submitHandler: function (form) {
                        $(form).ajaxSubmit({
                            type: "POST",
                            data: $(form).serialize(),
                            url: "/user-register",
                            success: function success(data, textStatus, jqXHR) {
                                alert(data.message);
                                location.reload();
                            },
                            error: function error(jqXHR, textStatus, errorThrown) {
                                alert(textStatus + "\n" + jqXHR.responseJSON.message);
                            }
                        })
                    }
                });
            }
        }
    );
})(jQuery);