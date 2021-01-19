// $(document).ready(function () {
//   var info = $('iframe').contents();
//   var popUp =
//     info['0']['body']['firstElementChild']['firstChild']['children']['5'];
//   console.log(popUp);

//   $('#pop-btn').click(function () {
//     console.log(popUp);
//     if (popUp['firstChild'] !== null) {
//       var name =
//         popUp['firstChild']['firstChild']['firstChild']['firstChild'][
//           'firstChild'
//         ];
//       castle_id = name['id'];
//       $('#castle-id').text(castle_id);
//       console.log(castle_id);
//       $.ajax({
//         method: 'POST',
//         headers: { 'X-CSRFToken': '{{ csrf_token }}' },
//         data: { name: castle_id },
//       });
//       /*.fail(function(message) {
//         alert('error');
//     })
//     .done(function(data) {
//         alert('data');
//     });*/
//     }
//   });
// });

// $(document).ready(function () {
//   $('#show-btn').click(function () {
//     var requested_id = $('#castle-id').text();
//     $.ajax({
//       method: 'GET',
//       data: { castle_id: requested_id },
//       success: function (resp) {
//         $('#castle-name').text(resp.requested_id);
//       },
//     });
//   });
// });
