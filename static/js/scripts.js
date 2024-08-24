$("form[name=signup_form").submit(function(e) {
    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();

    $.ajax({
        url: "/users/signup",
        type: "POST",
        data: data,
        success: function(response) {
            window.location.href = "/home/"
        },
        error: function(res) {
            $error.text(res.responseJSON.error).removeClass("error--hidden")
        }
    });

    e.preventDefault();
});

$("form[name=login_form").submit(function(e) {
    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();

    $.ajax({
        url: "/users/login",
        type: "POST",
        data: data,
        success: function(response) {
            window.location.href = "/home/"
        },
        error: function(res) {
            $error.text(res.responseJSON.error).removeClass("error--hidden")
        }
    });

    e.preventDefault();
});