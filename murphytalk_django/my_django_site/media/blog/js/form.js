function sumbit_form_by_enter_key(e){
	var characterCode;
	if(e && e.which){
		e = e;
        characterCode = e.which;
	}
	else{
		e = event;
		characterCode = e.keyCode;
	}	 
	if(characterCode == 13){
		document.forms[1].submit();
		return false;
	}
	return true	;
}


