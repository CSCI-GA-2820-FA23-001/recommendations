$(function () {
    var regexForInt = /^(0|[1-9][0-9]*)$/; // natural number without leading zeros

    var lastId = '';
    $('#rec_id').on('input', function () {
        var value = $(this).val();
        if (regexForInt.test(value) || value === '') {
            lastId = value;
        } else {
            alert("Invalid Input");
            $(this).val(lastId);
        }
    });

    var lastSrcId = '';
    $('#src_item_id').on('input', function () {
        var value = $(this).val();
        if (regexForInt.test(value) || value === '') {
            lastSrcId = value;
        } else {
            alert("Invalid Input");
            $(this).val(lastSrcId);
        }
    });

    var lastTgtId = '';
    $('#tgt_item_id').on('input', function () {
        var value = $(this).val();
        if (regexForInt.test(value) || value === '') {
            lastTgtId = value;
        } else {
            alert("Invalid Input");
            $(this).val(lastTgtId);
        }
    });

    var lastLikes = '';
    $('#num_of_likes').on('input', function () {
        var value = $(this).val();
        if (regexForInt.test(value) || value === '') {
            lastLikes = value;
        } else {
            alert("Invalid Input");
            $(this).val(lastLikes);
        }
    });

    var regexForWeight = /^(0(?:\.\d*)?|1(?:\.0*)?)$/;  // decimal between 0 and 1 without leading zeros
    var lastWeight = '';
    $('#rec_weight').on('input', function () {
        var value = $(this).val();
        if (regexForWeight.test(value) || value === '') {
            lastWeight = value;
        } else {
            alert("Invalid Input");
            $(this).val(lastWeight);
        }
    });
});