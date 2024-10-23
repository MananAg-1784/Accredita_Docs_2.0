
var criteria_data = {};
var data_dict = {};
var body = document.getElementById('body');
console.log(body);
var flash_msg = document.getElementById('flash_messages');

socket = io("/update", {autoConnect:false});
socket.connect();
socket.on('connect', function(){
    console.log("Socket Connected...");

    var nav = localStorage.getItem('nav_selection');
    console.log(nav);
    if(nav){
        update_nav(nav);
    } else{
        update_nav('Category');
    }
});

socket.on('disconnect', function(){
    console.log("Socket disconnected...")
});

function refresh_nav_data(){
    var nav = localStorage.getItem('nav_selection');
    console.log("Rerfreshing ....",nav);
    if(nav){
        update_nav(nav);
    } else{
        update_nav('Category');
    }
}

function loader(data = null){
    if(data){
        flash_msg.innerHTML = `
        <div class="loader"></div>
        <div>${data}...</div>
        `;
    } else{
        flash_msg.innerHTML = `
        <div class="loader"></div>
        <div>Loading...</div>
        `;
    }
}

function check_status_code(code_data){
    var status = 'status' in code_data ? code_data['status'] : null;
    if(status == 400){
        console.log(code_data['error']);
        flash_msg.innerHTML = '';
        alert(code_data['error']);
        socket.disconnect();
        return 0
    } else {
        return 1
    }
}

function update_nav(update_type){
    child = document.querySelectorAll('#update-nav > div');
    for(var x of child){
        if(x.innerHTML === update_type){
            x.classList.add('selected');
            console.log(x);
        } else{
            x.classList.remove('selected');
        }
    }
    if( !socket.connected ){
        socket.connect();
    }
    loader();

    e = document.querySelectorAll('#body > div');
    for (var x of e){
        x.classList.add('hide');
    }

    if(update_type == 'Category') {
        flash_msg.innerHTML = "";
        localStorage.setItem('nav_selection', 'Category');
        body.querySelector('#categories').classList.remove('hide');  
        socket.emit('reload-category', 1, (response)=>{
            response = JSON.parse(response);
            console.log(response);
            if(check_status_code(response)){
                if(response.error){
                    display_prog(response.error);
                } else{
                    available_cat = response.response;
                    modify_category_list_display();
                }
            }
        });
    }else if(update_type == 'Criteria') {
        flash_msg.innerHTML = "";
        localStorage.setItem('nav_selection', 'Criteria');
        body.querySelector('#criteria').classList.remove('hide');
    }else{
        flash_msg.innerHTML = "Unknown Request";
    }

}    

function category_selection_text(state){
    if (!state.id) {
        return state.text;
    } else if(state.id == 'all'){
        return state.text;
    } else{
        return state.id;
    }
};

function remove_options_for_criteria(){
    document.getElementById('criteria_options').innerHTML = '';
    document.getElementById('criteria_options').style.display = 'none';
}
function remove_options_for_category(){
    document.getElementById('category_options').innerHTML = '';
    document.getElementById('category_options').style.display = 'none';
}

function select_tag(options, name, default_option, onchange_func = null, value = null ){
    var select_ = document.createElement('select');
    select_.setAttribute('name', name);
    select_.setAttribute('class', name);
    if(onchange_func){
        select_.setAttribute('onchange', onchange_func);
    }
   
    var option_selected = 0;
    for(var x=0; x<options.length; x++){
        let option;
        if( value ){
            option = new Option(options[x], value[x]);
        } else{
            option = new Option(options[x], options[x]);
        }
        if(options[x] === default_option){
            option.selected = true;
            option_selected = 1
        }
        select_.add(option, undefined);
    }
    if(option_selected != 1 && default_option){
        let option = new Option(default_option, '-1');
        option.disabled = true;
        option.selected = true;
        select_.add(option, undefined);
    }
    return select_
}

function socket_connect(){
    if( !socket.connected){
        socket.connect();
    }
}


function display_prog(display_, timeout = true){
    document.getElementById('display_options_response').classList.remove('hide');
    document.getElementById('display_options_response').innerHTML = `
    <div class="flex row gap-10">${display_}</div>
    <div class="flex align-center" onclick="remove_activity_log()"> 
        <img src="/static?file_name=x-regular-white-24.png">
    </div>
    `;
    if(timeout){
        setTimeout(() => {
            document.getElementById('display_options_response').classList.add('hide');
        }, 5000);
    }
}

function remove_activity_log(){
    document.getElementById('display_options_response').classList.add('hide');
}

function modify_category_list_display(){
    removeAllCategories();
    for(x of available_cat){
        addCategory(x.category,x.definition);
    }
}