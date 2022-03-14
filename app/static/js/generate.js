errorText = document.getElementById('unsuccessful_generate')
if (window.sessionStorage['generation_error'] == true){
    errorText.style.visibility = 'visible'
}
function generate(that) {
    $.post( 
		"/generate_configuration", {
		configuration_name: that.configuration_name.value
	}).done(
		function(response){
			console.log(response)
			if (response == "successful"){
                window.sessionStorage['generation_error'] = false
                Location.reload();
			}
			else {
                window.sessionStorage['generation_error'] = true
			}
		}
	).fail(
		function(xhr, status, error){
			console.log(error)
			console.log('fail')
		}
	);

}