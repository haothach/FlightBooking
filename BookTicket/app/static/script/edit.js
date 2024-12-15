    document.addEventListener('DOMContentLoaded', function() {
       const oneWayRadio = document.getElementById('one-way');
       const roundTripRadio = document.getElementById('round-trip');
       const returnDateGroup = document.getElementById('return');

       toggleReturnDate();


       oneWayRadio.addEventListener('change', toggleReturnDate);
       roundTripRadio.addEventListener('change', toggleReturnDate);

       function toggleReturnDate() {
           if (oneWayRadio.checked) {
               returnDateGroup.style.display = 'none';
           } else {
               returnDateGroup.style.display = 'block';
           }
       }
   });




const departureSelect = document.getElementById('departure');
const destinationSelect = document.getElementById('destination');
const depAirportSelect = document.getElementById('dep_airport');
const desAirportSelect = document.getElementById('des_airport');

function updateSelectOptions(selectA, selectB) {
    const valueA = selectA.value;
    const valueB = selectB.value;

    // Hiện tất cả các tùy chọn trước khi áp dụng ẩn
    for (let option of selectA.options) {
        option.style.display = 'block';
    }
    for (let option of selectB.options) {
        option.style.display = 'block';
    }

    // Ẩn lựa chọn của selectA ở selectB nếu có giá trị
    if (valueA) {
        for (let option of selectB.options) {
            if (option.value === valueA) {
                option.style.display = 'none';
            }
        }
    }

    // Ẩn lựa chọn của selectB ở selectA nếu có giá trị
    if (valueB) {
        for (let option of selectA.options) {
            if (option.value === valueB) {
                option.style.display = 'none';
            }
        }
    }
}

// Đăng ký sự kiện thay đổi cho các select
departureSelect.addEventListener('change', () => updateSelectOptions(departureSelect, destinationSelect));
destinationSelect.addEventListener('change', () => updateSelectOptions(departureSelect, destinationSelect));
depAirportSelect.addEventListener('change', () => updateSelectOptions(depAirportSelect, desAirportSelect));
desAirportSelect.addEventListener('change', () => updateSelectOptions(depAirportSelect, desAirportSelect));

// Đảm bảo rằng các sự kiện sẽ chỉ chạy khi DOM đã sẵn sàng
document.addEventListener('DOMContentLoaded', () => {
    updateSelectOptions(departureSelect, destinationSelect);
    updateSelectOptions(depAirportSelect, desAirportSelect);
});





    const departureDateInput = document.getElementById('departure-date');

    // Tạo ngày hiện tại theo định dạng YYYY-MM-DD
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0'); // tháng bắt đầu từ 0 nên phải +1
    const dd = String(today.getDate()).padStart(2, '0');

    // Đặt giá trị mặc định cho input là ngày hiện tại
    departureDateInput.value = `${yyyy}-${mm}-${dd}`;

    document.addEventListener('DOMContentLoaded', () => {
        const alerts = document.querySelectorAll('.alert');

        // Hiệu ứng xuất hiện
        alerts.forEach(alert => {
            alert.classList.add('fade-in'); // Thêm hiệu ứng xuất hiện

            // Tự động ẩn sau 3 giây
            setTimeout(() => {
                alert.classList.remove('fade-in'); // Loại bỏ hiệu ứng xuất hiện
                alert.classList.add('fade-out');  // Thêm hiệu ứng biến mất
                setTimeout(() => alert.remove(), 500); // Xóa khỏi DOM sau khi hiệu ứng kết thúc
            }, 3000); // 3000ms = 3 giây
        });
    });

    //Nút tick hiển thị sân bay trung gian
    function toggleTransitFields() {
        var checkbox = document.getElementById('enableTransit');
        var transitTable = document.getElementById('transitTable');

        // Hiển thị hoặc ẩn bảng sân bay trung gian khi checkbox được tick
        if (checkbox.checked) {
            transitTable.style.display = 'table';
        } else {
            transitTable.style.display = 'none';
        }
    }