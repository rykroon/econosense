
//initialize tooltips
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

//Initialize data table
$(document).ready( function () {
    $('#result-table').DataTable();

    if ($('#id_include_tax').prop('checked')) {
      $('#id_filing_status').prop('disabled',false);
    } else {
      $('#id_filing_status').prop('disabled',true);
    }
} );

$('#id_include_tax').click(function(){

  if ($(this).prop('checked')) {
    $('#id_filing_status').prop('disabled',false);
  } else {
    $('#id_filing_status').prop('disabled',true);
  }
})
