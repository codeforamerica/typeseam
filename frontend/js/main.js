$( document ).ready(function() {
  listenToEvents();
});


function listenToEvents(){
  $('.responses').on('click', 'button.load_new_responses', getNewResponses);
  $('.responses').on('click', '.pdf_cell', getPDF);
}

function getNewResponses(e){
  $.ajax({
    url: "/api/new_responses",
    success: handleNewResponses,
    timeout: 10000
  });
}

function getPDF(e){
  var responseId = $(this).parent('.response').attr('id');
  responseId = responseId.split("-")[1]
  $.ajax({
    url: "/api/get_pdf/" + responseId,
    success: handleNewPDF(responseId),
    timeout: 20000
  });
}

function handleNewResponses(html){
  $('.responses').append(html);
}

function handleNewPDF(responseId){
  return function(html){
    console.log("pdf response!", html)
    $('#response-'+responseId).replaceWith(html);
  };
}