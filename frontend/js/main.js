$( document ).ready(function() {
  addCSRFTokenToRequests()
  listenToEvents();
  getNewResponses();
});

var PDF_LOADING_STATES = [
  ["sending", 2000],
  ["generating", 13000],
  ["retrieving", 5000],
  ];

function addCSRFTokenToRequests(){
  // Taken directly from
  // http://flask-wtf.readthedocs.org/en/latest/csrf.html#ajax
  var csrftoken = $('meta[name=csrf-token]').attr('content');
  $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken)
          }
      }
  });
}

function listenToEvents(){
  $('.responses-header').on('click', '.load_new_responses', getNewResponses);
  $('.container').on('click', '.pdf_button', getPDF);
}

function getNewResponses(e){
  $('button.load_new_responses').addClass('loading');
  $.ajax({
    url: API_ENDPOINTS.new_responses,
    success: handleNewResponses,
    timeout: 10000
  });
}

function stateTransitionChain(target, stateStack, index){
  if( index > 0){
    var prevStateClassName = stateStack[index - 1][0];
    target.removeClass(prevStateClassName);
  }
  if( index == stateStack.length ){
    target.removeClass("loading");
    target.addClass('default');
    return;
  }
  var stateClassName = stateStack[index][0];
  var delay = stateStack[index][1];
  target.addClass(stateClassName);
  setTimeout(function(){
    stateTransitionChain(target, stateStack, index + 1);
  }, delay)
}

function getPDF(e){
  var target = $(this);
  console.log("clicked to get pdf on", target);
  target.removeClass("default");
  target.addClass('loading');
  var responseId = target.parents('.response').attr('id');
  responseId = responseId.split("-")[1]
  stateTransitionChain(target, PDF_LOADING_STATES, 0);
  $.ajax({
    method: "POST",
    url: target.attr("data-apiendpoint"),
    success: handleNewPDF(responseId),
    timeout: 20000
  });
}

function handleNewResponses(html){
  $('.responses').prepend(html);
  $('button.load_new_responses').removeClass('loading');
}

function handleNewPDF(responseId){
  return function(html){
    $('#response-'+responseId).replaceWith(html);
  };
}