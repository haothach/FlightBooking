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

   document.addEventListener('DOMContentLoaded', updateOptions);