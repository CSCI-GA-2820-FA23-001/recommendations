$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#rec_id").val(res.id);
        $("#rec_src_item_id").val(res.source_item_id);
        $("#rec_tgt_item_id").val(res.target_item_id);
        $("#rec_type").val(res.recommendation_type);
        $("#rec_status").val(res.status);
        $("#rec_weight").val(res.recommendation_weight);
        $("#rec_num_of_likes").val(res.number_of_likes);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#rec_src_item_id").val("");
        $("#rec_tgt_item_id").val("");
        $("#rec_type").val("");
        $("#rec_status").val("");
        $("#rec_weight").val("");
        $("#rec_num_of_likes").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Recommendation
    // ****************************************

    $("#create-btn").click(function () {
        let src_item_id = parseInt($("#rec_src_item_id").val());
        let tgt_item_id = parseInt($("#rec_tgt_item_id").val());
        let type = $("#rec_type").val();
        let status = $("#rec_status").val();
        let weight = parseFloat($("#rec_weight").val());
        let likes = parseInt($("#rec_num_of_likes").val());

        let data = {
            "source_item_id": src_item_id,
            "target_item_id": tgt_item_id,
            "recommendation_type": type,
            "status": status,
            "recommendation_weight": weight,
            "number_of_likes": likes
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: "/api/recommendations",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Recommendation
    // ****************************************

    $("#update-btn").click(function () {

        let rec_id = $("#rec_id").val();
        let src_item_id = parseInt($("#rec_src_item_id").val());
        console.log(src_item_id)
        let tgt_item_id = parseInt($("#rec_tgt_item_id").val());
        let type = $("#rec_type").val();
        let status = $("#rec_status").val();
        let weight = parseFloat($("#rec_weight").val());
        let likes = parseInt($("#rec_num_of_likes").val());

        let data = {
            "source_item_id": src_item_id,
            "target_item_id": tgt_item_id,
            "recommendation_type": type,
            "status": status,
            "recommendation_weight": weight,
            "number_of_likes": likes
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/recommendations/${rec_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Recommendation
    // ****************************************

    $("#retrieve-btn").click(function () {

        let rec_id = $("#rec_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/recommendations/${rec_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            // console.log(res)
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });
    // ****************************************
    // Retrieve a Recommendation by src-item-id
    // ****************************************
    $("#retrieve-by-src-item-id-btn").click(function () {
        let rec_src_item_id = $("#rec_src_item_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/recommendations/source-product?source_item_id=${rec_src_item_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            // console.log(res)
            if (res.length > 0) {
                update_form_data(res[0]) // src-item-id is not a unique id, so only update the form with the first returned value
                recQuery()
                flash_message("Success")
            }
            else {
                flash_message("No recommendations found!")
            }
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });
    });
    // ****************************************
    // Delete a Recommendation
    // ****************************************

    $("#delete-btn").click(function () {

        let rec_id = $("#rec_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/recommendations/${rec_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            clear_form_data()
            flash_message("Recommendation has been deleted!")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#rec_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Recommendation
    // ****************************************
    function recQuery() {
        let page_index = $("#page_index").val();
        let page_size = $("#page_size").val();
        let rec_type = $("#rec_type").val();
        let rec_status = $("#rec_status").val();

        let queryString = "" + 'page-index=' + page_index + '&page-size=' + page_size

        if (rec_type) {
            queryString += '&type=' + rec_type
        }

        if (rec_status) {
            queryString += '&status=' + rec_status
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/recommendations?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //console.log(res)

            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">ID</th>'
            table += '<th class="col-md-1">Source</th>'
            table += '<th class="col-md-1">Target</th>'
            table += '<th class="col-md-1">Type</th >'
            table += '<th class="col-md-1">Status</th>'
            table += '<th class="col-md-1">Weight</th>'
            table += '<th class="col-md-1">Likes</th>'
            table += '<th class="col-md-2">Created Time</th>'
            table += '<th class="col-md-2">Updated Time</th>'
            table += '</tr></thead><tbody>'
            let firstRec = "";
            for (let i = 0; i < res["items"].length; i++) {
                let rec = res["items"][i];
                table += `<tr id="row_${i}"><td>${rec.id}</td><td>${rec.source_item_id}</td><td>${rec.target_item_id}</td><td>${rec.recommendation_type}</td><td>${rec.status}</td><td>${rec.recommendation_weight}</td><td>${rec.number_of_likes}</td><td>${rec.created_at}</td><td>${rec.updated_at}</td></tr>`;
                if (i == 0) {
                    firstRec = rec;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstRec != "") {
                update_form_data(firstRec)
            }

            // update search summary
            let entry_start = (res["page"] - 1) * res["per_page"] + 1;
            let entry_end = entry_start + res["items"].length - 1;
            if (entry_start > entry_end) {
                entry_start = -1
                entry_end = -1
            }
            let search_summary = `Search Summary: Showing ${entry_start} to ${entry_end} of ${res["total"]} entries`;
            $("#search_summary").empty();
            $("#search_summary").append(search_summary);

            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    }

    $("#search-btn").click(function () {
        recQuery()
    });
})
