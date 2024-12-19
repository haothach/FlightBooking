document.addEventListener("DOMContentLoaded", function () {
    // Logic cho "Điểm đi" và "Điểm đến"
    const departureSelect = document.getElementById('departure');
    const destinationSelect = document.getElementById('destination');

    if (departureSelect && destinationSelect) {
        function updateOptions() {
            const departureValue = departureSelect.value;
            const destinationValue = destinationSelect.value;

            // Hiện tất cả các tùy chọn trước khi áp dụng ẩn
            for (let option of departureSelect.options) {
                option.style.display = 'block';
            }
            for (let option of destinationSelect.options) {
                option.style.display = 'block';
            }

            // Ẩn lựa chọn "Điểm đến" ở "Điểm đi" và ngược lại
            if (departureValue) {
                for (let option of destinationSelect.options) {
                    if (option.value === departureValue) {
                        option.style.display = 'none';
                    }
                }
            }

            if (destinationValue) {
                for (let option of departureSelect.options) {
                    if (option.value === destinationValue) {
                        option.style.display = 'none';
                    }
                }
            }
        }

        departureSelect.addEventListener('change', updateOptions);
        destinationSelect.addEventListener('change', updateOptions);
        updateOptions();
    }

    // Logic đặt ngày mặc định
    const departureDateInput = document.getElementById('departure_date');
    if (departureDateInput) {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');

        departureDateInput.value = `${yyyy}-${mm}-${dd}`;
    }

});

    // Logic hiệu ứng thông báo
//    const alerts = document.querySelectorAll('.alert');
//    if (alerts.length > 0) {
//        alerts.forEach(alert => {
//            alert.classList.add('fade-in');
//
//            // Tự động ẩn sau 3 giây
//            setTimeout(() => {
//                alert.classList.remove('fade-in');
//                alert.classList.add('fade-out');
//                setTimeout(() => alert.remove(), 500);
//            }, 3000);
//        });
//    }

    let flightId = document.getElementById('flight_id').value;
    let depAirport = document.getElementById('dep_airport').value;
    let desAirport = document.getElementById('des_airport').value;
    let first_class_seats = document.getElementById('first_class_seats').value;
    let first_class_price = document.getElementById('first_class_price')
    let second_class_seats = document.getElementById('second_class_seats').value;
    let second_class_price = document.getElementById('second_class_price')
    let ai_1 = document.getElementById('imediateairport1').value;
    let note_1 = document.getElementById('note_1').value;
    let ai_2 = document.getElementById('imediateairport2').value;
    let note_2 = document.getElementById('note_2').value;

    function formatDateTime(year, month, day, hour, minute) {
    // Tạo một đối tượng Date từ các tham số
        let date = new Date(year, month - 1, day, hour, minute); // Lưu ý: month bắt đầu từ 0 (tháng 1 là 0)

        // Lấy các thành phần ngày giờ
        let formattedYear = date.getFullYear();
        let formattedMonth = String(date.getMonth() + 1).padStart(2, '0'); // Tháng cần cộng thêm 1 vì tháng bắt đầu từ 0
        let formattedDay = String(date.getDate()).padStart(2, '0');
        let formattedHour = String(date.getHours()).padStart(2, '0');
        let formattedMinute = String(date.getMinutes()).padStart(2, '0');

        // Trả về chuỗi theo định dạng yyyy-mm-dd hh:mm:00
        return `${formattedYear}-${formattedMonth}-${formattedDay} ${formattedHour}:${formattedMinute}:00`;
    }
    function convertToMinutes(hour, minute) {
        // Chuyển giờ thành phút và cộng thêm phút
        return (parseInt(hour) * 60) + parseInt(minute);
    }

    let formattedDateTime = formatDateTime(document.getElementById('year').value,document.getElementById('month').value,document.getElementById('day').value,document.getElementById('hour').value,document.getElementById('minute').value);
    let depTimeInMinutes = convertToMinutes(document.getElementById('flight_hour').value, document.getElementById('flight_minute').value);
    let flightStopTimeOneInMinutes = convertToMinutes(document.getElementById('flight_stop_hour_one').value, document.getElementById('flight_stop_minute_one').value);
    let flightStopTimeTwoInMinutes = convertToMinutes(document.getElementById('flight_stop_hour_two').value, document.getElementById('flight_stop_minute_two').value);

    const data = {
        flight_id: flightId,
        dep_airport: depAirport,
        des_airport: desAirport,
        dep_time:formattedDateTime,
        flight_time:depTimeInMinutes,
        business_class_seat_size: first_class_seats,
        first_class_price:first_class_price,
        economy_class_seat_size: second_class_seats,
        second_class_price:second_class_price
        ai_1: ai_1,
        stop_time_1:flightStopTimeOneInMinutes,
        note_1: note_1,
        ai_2: ai_2,
        stop_time_2:flightStopTimeTwoInMinutes,
        note_2: note_2
    };
    function confirm(){
        fetch('/api/schedule', {
            method: 'POST',  // hoặc 'PUT' nếu bạn đang cập nhật
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {})
    }







