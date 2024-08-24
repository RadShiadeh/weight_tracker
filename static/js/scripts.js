$("form[name=signup_form").submit(function(e) {
    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();

    $.ajax({
        url: "/users/signup",
        type: "POST",
        data: data,
        success: function(response) {
            window.location.href = "/"
        },
        error: function(res) {
            $error.text(res.responseJSON.error).removeClass("error--hidden")
        }
    });

    e.preventDefault();
});