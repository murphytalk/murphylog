var ESC_CODE=27;
var ENTER_CODE=13;
var UP_CODE=38;
var DOWN_CODE=40;

var MIN_WIDTH=150;
var MAX_HEIGHT=200;

function createRequest(){
  try{
    return new XMLHttpRequest();
  } catch(e) {
    return new ActiveXObject("Msxml2.XMLHTTP");
  }//try
}//createRequest

function addEvent(element,event,handler){
  if(element.addEventListener)
    element.addEventListener(event,handler,false);
  else if(element.attachEvent)
    element.attachEvent('on'+event,handler);
  else
    throw 'Can\'t add event';
}//addEvent

function currentTarget(e){
  if(e.currentTarget)
    return e.currentTarget;
  return event.srcElement;
}//currentTarget

function getKeyCode(e){
  if(e && e.keyCode!=undefined)
    return e.keyCode;
  if(e && e.which!=undefined)
    return e.which;
  if(window.event && window.event.charCode!=undefined)
    return window.event.charCode;
  if(window.event && window.event.keyCode!=undefined)
    return window.event.keyCode;
  return null;
}//getKeyCode

function elLeft(el){
  result=0;
  while(el){
    result+=el.offsetLeft;
    el=el.offsetParent;
  }//while
  return result;
}//elLeft

function elTop(el){
  result=0;
  while(el){
    result+=el.offsetTop;
    el=el.offsetParent;
  }//while
  return result;
}//elTop

function hasClass(el,value){
  var class_re=new RegExp('(^|\\s)('+value+')($|\\s)');
  match=el.className.match(class_re);
  if(match)
    return match[2];
  else
    return null;
}//hasClass

function addClass(el,value){
  if(!hasClass(el,value))
    el.className+=' '+value;
}//addClass

function removeClass(el,value){
  var class_re=new RegExp('(^|\\s)'+value+'($|\\s)','g');
  el.className=el.className.replace(class_re,'$2');
}//removeClass

function getElementsByClass(value,scope,tag_name) {
	if(!scope)
		scope=document;
	if(!tag_name)
		tag_name='*';
	var els = scope.getElementsByTagName(tag_name);
  values=value.split(' ');
  class_res=[];
  for(var i=0;i<values.length;i++)
    class_res[class_res.length]=new RegExp('(^|\\s)'+values[i]+'($|\\s)');
  result=[];
  for(var i=0;i<els.length;i++) {
    var found=true;
    for(var j=0;j<class_res.length;j++)
      if(!els[i].className.match(class_res[j])){
        found=false;
        break;
      }//if
    if(found)
      result[result.length]=els[i];
  }//for
	return result;
}//getElementsByClass

function initAutoCompletes(scope) {
  var inputs=getElementsByClass('suggest_[a-zA-Z0-9]+',scope,'input');
  for(var i=0;i<inputs.length;i++){
    initAutoComplete(
      inputs[i],
      scope
    );
  }//for
}//initAutoCompletes

function initAutoComplete(input,init_scope){
  var ul=document.createElement('UL');
  document.body.appendChild(ul);
  if(init_scope){
    var className=hasClass(input,'suggest_[a-zA-Z0-9]+').replace('suggest_','suggest ');
    var uls=getElementsByClass(className,init_scope,'ul');
    if(uls.length){
      init_lis=uls[0].getElementsByTagName('LI');
      for(var i=0;i<init_lis.length;i++)
        ul.appendChild(init_lis[i].cloneNode(true));
    }//if
  }//if
  initSuggestLis(ul,input);
  ul.className='suggest';
  ul.style.position='absolute';
  ul.style.display='none';
  ul.style.width=(input.offsetWidth<MIN_WIDTH?MIN_WIDTH:input.offsetWidth)-2+'px';
  try{
    ul.style.maxHeight=MAX_HEIGHT+'px';
  } catch(e) {
    ul.style.height=MAX_HEIGHT+'px';
  }//try
  ul.style.whiteSpace='nowrap';
  ul.style.overflow='auto';
  try{
    ul.style.overflowX='hidden';
  } catch(e){
    //do nothing
  }//try
  input.onkeyup=function(e){
    var keyCode=getKeyCode(e);
    if(keyCode==ENTER_CODE ||
       keyCode==ESC_CODE ||
       keyCode==DOWN_CODE ||
       keyCode==UP_CODE)
      return;
    filterList(ul,input.value);
    if(hasClass(input,'ajax'))
      reloadList(ul,input,input.value);
    if(input.value){
      showList(ul,input);
    } else {
      hideList(ul,input);
    }//if
  }//keyup
  input.onkeydown=function(e){
    var keyCode=getKeyCode(e);
    if(keyCode==ESC_CODE){
      hideList(ul,input);
    } else if(keyCode==DOWN_CODE || keyCode==UP_CODE){
      showList(ul,input);
      moveListSelection(ul,keyCode==DOWN_CODE?'down':'up');
    } else if(keyCode==ENTER_CODE){
      var li=selectedItem(ul);
      if(li){
        input.value=liValue(li);
        hideList(ul,input);
        if(e && e.preventDefault)
          e.preventDefault();
        return false;
      } else {
        if(hasClass(input,'strict'))
          input.value='';
      }//if
    }//if
  }//keydown
  input.onblur=function(e){
    if(hasClass(input,'strict')){
      var li=selectedItem(ul);
      if(li)
        input.value=liValue(li);
      else
        input.value='';
    }//if
    hideList(ul,input);
  }//blur
  input.onclick=function(e){
    if(ul.offsetHeight)
      hideList(ul,input);
    else
      showList(ul,input);
  }//click
}//initAutoComplete

function normalizeTitle(title){
  title=title.toLowerCase();
  title=title.replace('ё','е');
  safe_title=title // safe_title can't be empty since nothing has been removed yet
  title=title.replace(/\bthe\b/,'');
  title=title.replace(/[\,\.\(\)\-\!\'\"\`\?\_\:\;\$\]\[\#\/]/,'');
  title=title.replace(/\s+/,'');
  return title!=''?title:safe_title;
}//normalizeTitle

function liValue(li){
  if(li.firstChild)
    return li.firstChild.nodeValue.replace(/[\n\s]+$/,'');
  else
    return '';
}//liValue

function showList(ul,input){
  ul.style.display='block';
  ul.style.left=elLeft(input)+'px';
  ul.style.top=elTop(input)+input.offsetHeight+'px';
}//showList

function hideList(ul,input){
  ul.style.display='none';
}//hideList

function filterList(ul,value){
  lis=ul.getElementsByTagName('LI');
  for(var i=0;i<lis.length;i++){
    if(normalizeTitle(liValue(lis[i])).indexOf(normalizeTitle(value))==0)
      lis[i].style.display='';
    else {
      lis[i].style.display='none';
    }//if
  }//for
  if(hasClass(ul,'strict')){
    if(!selectedItem(ul))
      moveListSelection(ul,'down');
  }//if
}//filterList

function selectedItem(ul){
  var lis=getElementsByClass('selected',ul,'LI');
  if(lis.length)
    return lis[0];
  else
    return null;
}//selectedItem

function clearListSelection(ul){
  var li=selectedItem(ul);
  if(li)
    removeClass(li,'selected');
}//clearListSelection

function moveListSelection(ul,direction){
  var all_lis=ul.getElementsByTagName('LI');
  var lis=[];
  for(var i=0;i<all_lis.length;i++)
    if(all_lis[i].offsetHeight)
      lis[lis.length]=all_lis[i];
  if(lis.length==0)
    return;
  var index=removeSelection(lis);
  index+=(direction=='down'?1:-1);
  if(index<0)
    index=lis.length-1;
  if(index>=lis.length)
    index=0;
  addClass(lis[index],'selected');
}//moveListSelection

function removeSelection(lis){
  var index=-1;
  for(var i=0;i<lis.length;i++)
    if(hasClass(lis[i],'selected')){
      index=i;
      break;
    }//if
  if(index>=0)
    removeClass(lis[index],'selected');
  return index;
}//removeSelection

var request=null;
var requestTimeout=null;

function reloadList(ul,input,value){
  clearTimeout(requestTimeout);
  requestTimeout=setTimeout(function(){
    if(request){
      request.abort();
      request=null;
    }//if
    addClass(ul,'loading');
    request=createRequest();
    request.onreadystatechange=function(){
      if(request.readyState!=4)
        return;
      removeClass(ul,'loading');
      if(request.status!=200)
        return;
      selected=selectedItem(ul);
      if(selected)
        var old_value=liValue(selected);
      else
        var old_value='';
      ul.innerHTML=request.responseText;
      lis=ul.getElementsByTagName('LI');
      if(lis.length){
        var i=0;
        while(i<lis.length && liValue(lis[i])!=old_value)
          i++;
        if(i<lis.length)
          addClass(lis[i],'selected');
        else {
          if(hasClass(input,'strict'))
            addClass(lis[0],'selected');
        }//if
      }//if
      initSuggestLis(ul,input);
      request=null;
    }//onreadystatechange
    field=hasClass(input,'suggest_[a-zA-Z0-9]+').replace('suggest_','');
    request.open('GET',encodeURI('/suggest/'+field+'/?value='+input.value));
    request.send(null);
  },500);
}//reloadList

function initSuggestLis(ul,input){
  var lis=ul.getElementsByTagName('LI');
  for(var i=0;i<lis.length;i++){
    lis[i].onmousedown=function(){
      input.value=liValue(this);
    }//onmousedown
    lis[i].onmouseover=function(){
      addClass(this,'selected');
    }//onmouseover
    lis[i].onmouseout=function(){
      removeClass(this,'selected');
    }//onmouseout
  }//for
}//initSuggestLis

addClass(document.body,'js');
