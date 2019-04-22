function check_quiz(quizid) {

    var selection = $('input[name=question]:checked').val();
    
    if (selection!=1 && selection!=2 && selection!=3 && selection!=4){
        alert("Please make a choice");
        return
    }
    $.ajax({
        url: "/virtualTravel/checkquiz/"+quizid+"/"+selection,
        dataType: "text",
        success: function(response){
            $("#quiz_response").html(response);
        }
    });
    $("#id_quiz_button").remove();
    var new_button = '<button id="id_next_city_button" class="btn btn-primary"'
                    +' onclick="window.location.href=\'next_city\'">'
                    +'Next City</button>'
    $("#id_next_city").html(new_button);
    check_last_city();
}

function check_last_city(){
    $.ajax({
        url: "/virtualTravel/check_last_city",
        dataType: "text",
        success: function(response){
            if(response=="true"){
                $("#id_next_city_button").html("Finish Travel");
            }
        }
    });

}

function finish_travel(){
    $.ajax({
        url: "/virtualTravel/finish_travel",
        dataType: "json",
        success: function(response){
            if(response=="true"){
                $("#id_next_city_button").html("Finish Travel");
            }
        }
    });
}