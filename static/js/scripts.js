$("form[name=signup_form").submit(function(e) {
    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();

    $.ajax({
        url: "/users/signup",
        type: "POST",
        data: data,
        success: function(response) {
            console.log(response)
        },
        error: function(res) {
            console.log(res)
            $error.text(res.responseJSON.error).removeClass("error--hidden")
        }
    });

    e.preventDefault();
});