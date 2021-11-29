(function ($) {

    "use strict";

    var $document = $(document),
        $window = $(window),
        forms = {
            contactForm: $('#contactForm'),
            questionForm: $('#questionForm'),
            bookForm: $('#bookForm'),
            loginForm: $('#loginForm'),
            registerForm: $('#registerForm'),
            changePasswordForm: $('#changePasswordForm'),
        };

    $document.ready(function (e) {

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
                        },
                        bookingdate: {
                            required: true,
                            remote: {
                                url: '/api/check-booking-date',
                                type: "post",
                                data:
                                    {
                                        date: function () {
                                            return $('.datetimepicker').val();
                                        }
                                    }
                            }
                        },
                        bookingtime: {
                            required: true,
                            remote: {
                                url: '/api/check-booking-time',
                                type: "post",
                                data:
                                    {
                                        time: function () {
                                            return $('.timepicker').val();
                                        }
                                    }
                            }
                        }
                    },
                    messages: {
                        bookingname: {
                            required: "Please enter your name",
                            minlength: "Your name must consist of at least 2 characters"
                        },
                        bookingemail: {
                            required: "Please enter your email"
                        },
                        bookingdate: {
                            required: "Please, choose date!",
                            remote: "Invalid date!"
                        },
                        bookingtime: {
                            required: "Please, choose time!",
                            remote: "Invalid time!"
                        }
                    },
                    submitHandler: function submitHandler(form) {
                        $(form).ajaxSubmit({
                            type: "POST",
                            data: $(form).serialize(),
                            url: "/api/add-booking",
                            success: function success(data) {
                                if (window.location.pathname === "/schedule") {
                                    var timeStr = $('input[name="bookingtime"]', $bookForm).val();
                                    var dateStr = $('input[name="bookingdate"]', $bookForm).val();
                                    var dataSplit = dateStr.split('/');
                                    var date = new Date(parseInt(dataSplit[2]), parseInt(dataSplit[1]) - 1, parseInt(dataSplit[0]))

                                    var time = parseInt(timeStr.substring(0, timeStr.indexOf(":"))) + parseInt(timeStr.includes("PM") ? '12' : '0');
                                    var day = Object.keys($DAYS).find((key => $DAYS[key] === date.getDay()))

                                    var period = $(`li[data-start="${("0" + time).slice(-2)}:00"][data-day="${day}"]`)
                                    period.children("a")
                                        .html(`${data.amount}/${$BOOKING_MAX} <div class="doctor-time">${("0" + time).slice(-2)}:00 - ${("0" + (time + 1)).slice(-2)}:00</div>`);
                                    if (data.amount === 2) {
                                        period.css('background-color', '#50c878')
                                        period.children("a").css("color", "#ffffff")
                                        period.css("pointer-events", "none");
                                    } else if (data.amount === 1) {
                                        period.css('background-color', '#55a2e485')
                                        period.children("a").css("color", "#1e76bd")
                                    }
                                }

                                $bookForm.get(0).reset();
                                $('.modal-content button.close').click();
                            },
                            error: function error(jqXHR, textStatus, errorThrown) {
                                $('.errorform', $bookForm).fadeIn();
                                alert(textStatus + "\n" + jqXHR.responseJSON.message);
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

            // change password form
            if (forms.changePasswordForm.length) {
                var $changePasswordForm = forms.changePasswordForm;
                $changePasswordForm.submit(function () {
                    $.ajax({
                        type: "POST",
                        data: $changePasswordForm.serialize(),
                        url: "/api/change-password",
                        success: function success(data, textStatus, jqXHR) {
                            alert(data.message);
                            $changePasswordForm.get(0).reset();
                        },
                        error: function error(jqXHR, textStatus, errorThrown) {
                            alert(jqXHR.responseJSON.message);
                        }
                    })
                    return false;
                })

            }
        }
    );
})(jQuery);