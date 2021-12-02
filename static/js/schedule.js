function booking(obj, day) {
    var booked_date = new Date();
    var time = parseInt($(obj).data("start").substr(0, 2));

    booked_date.setDate(booked_date.getDate() + ($DAYS[day] - booked_date.getDay()));

    // console.log($(obj).children('a').length)
    var datetimepicker = $('.datetimepicker');
    var timepicker = $('.timepicker');
    datetimepicker.css("pointer-events", "none");
    datetimepicker.css("color", "rgba(0,0,0,.5)");
    datetimepicker.val(`${booked_date.getDate()}/${booked_date.getMonth() + 1}/${booked_date.getFullYear()}`);
    timepicker.val(`${time % 12}:00 ${time > 12 ? 'PM' : 'AM'}`);
    timepicker.css("pointer-events", "none");
    timepicker.css("color", "rgba(0,0,0,.5)");
}

function loadSchedule() {
    for (let day in $DAYS) {
        for (let i = 8; i < 20; i++) {
            if (!(i in {12: 0, 19: 0})) {
                var date = new Date();
                date.setDate(date.getDate() + ($DAYS[day] - date.getDay()));
                $.ajax({
                    dataType: "json",
                    url: "/api/load-schedule",
                    data: {
                        bookingtime: i,
                        bookingdate: `${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()}`
                    },
                    success: function (data) {
                        var period = $(`li[data-start="${("0" + i).slice(-2)}:00"][data-day="${day}"]`)
                        period.children("a")
                            .html(`${data.amount}/${$BOOKING_MAX} <div class="doctor-time">${("0" + i).slice(-2)}:00 - ${("0" + (i + 1)).slice(-2)}:00</div>`);
                        if (data.amount === 2){
                            period.css('background-color', '#50c878')
                            period.children("a").css("color","#ffffff")
                            period.css("pointer-events", "none");
                        } else if (data.amount === 1){
                            period.css('background-color', '#55a2e485')
                            period.children("a").css("color", "#1e76bd")
                        }
                    },
                    error: function (e){
                        alert("ERROR: " + e);
                    }
                });
            }
        }
    }
}

setTimeout(function(){loadSchedule()},400)
