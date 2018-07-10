
// var all_jobs = $('#id_job').children();
//
// major_job_id = parseInt($('#id_job_category').val());
//
// //Initial Filter
// if (! isNaN(major_job_id)){
//   $('#id_job').children(':not(:first-child)').each(function(){
//     if ((this.value < major_job_id) || (this.value > major_job_id + 9999)){
//       $(this).remove();
//     }
//   });
// }


//Filter jobs when the job category changes
// $('#id_job_category').change(function(){
//   major_job_id = parseInt($('#id_job_category').val());
//   filter_jobs(major_job_id);
// })


//Filter jobs based off of chosen Job Category
// function filter_jobs(major_job_id){
//   $("#id_job").children().remove();
//
//   if (isNaN(major_job_id)){
//     $("#id_job").append(all_jobs);
//
//   } else { //Chose a specific Major job
//
//     for (var i = 0; i < all_jobs.length ; i++) {
//
//       if ((all_jobs[i].value > major_job_id && all_jobs[i].value < major_job_id + 9999) ||
//         (all_jobs[i].value == '')){
//         $('#id_job').append(all_jobs[i]);
//       }
//     }
//   }
//
//   $('#id_job').val('');
//
// }

//initialize tooltips
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

//Initialize data table
$(document).ready( function () {
    $('#result-table').DataTable();
} );
