// var states = []
// var areas = []

//Initial filter and creation of arrays
// $('#id_location').children().each(function(){
//   if (this.value == ""){
//     states.push(this);
//     areas.push(this);
//     return;
//   }
//
//   if (this.value < 100){
//     states.push(this);
//   } else {
//     areas.push(this);
//   }
//
//   if ( ($('#id_location_type_0').is(':checked') && this.value > 100) ||
//      ($('#id_location_type_1').is(':checked') && this.value < 100) ){
//     $(this).remove();
//   }
//
// });

//toggle states when radio is clicked
// $('#id_location_type_0').click(function() {
//   toggle_locations('states');
// });

//toggle areas when radio is clicked
// $('#id_location_type_1').click(function() {
//   toggle_locations('areas');
// });


//toggles between states and areas
// function toggle_locations(location_type) {
//   $('#id_location').children().remove();
//
//   if (location_type == 'states'){
//     $('#id_location').append(states);
//
//   } else if(location_type == 'areas'){
//     $('#id_location').append(areas);
//   }
//
//   $('#id_location').val('');
// }


//tooltips
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})


// Data dataTables
$(document).ready( function () {
    $('#result-table').DataTable();
    //$('#tbl_two').DataTable();
} );
