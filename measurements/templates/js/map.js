$.get('/', function (data) {
  $('.result').html(data);
  alert('Load was performed.' + data);
});

console.log('work');
