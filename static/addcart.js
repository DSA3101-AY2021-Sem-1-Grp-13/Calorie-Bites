function addtocart() {
    $.ajax({
        type: "POST",
        url: "/add"
        }
    );
}

function removefromcart(clicked_id) {
    var server_data = [
        {"id": clicked_id}
    ];
    
    $.ajax({
        method: "POST",
        url: "/remove",
        data: JSON.stringify(server_data),
        contentType: "application/json",
        dataType : "json",
        success: function(){alert("Done");}
        }
    );
}

function removeall() {    
    $.ajax({
        method: "POST",
        url: "/removeall",
        success: function(){}
        }
    );
}