var csrftoken = Cookies.get('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function addWarning(message) {
    $('#alerts').append(
        '<div class="alert alert-warning alert-dismissible fade show" role="alert">' +
            '<button type="button" class="close" data-dismiss="alert">' +
            '&times;</button>' + message + '</div>');
}

$(document).ready(function() {
    $("#delete-credit-button").click(function(e) {
        e.preventDefault();
        $.ajax({
          type: "DELETE",
          url: window.location.href + "/delete",
          success: function(result) {
            window.location.href = result.success_url || '/'
          },
          error: function(result) {
            addWarning(result.responseText);
          }
        });
      });
})