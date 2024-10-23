
var cat_list = document.getElementById('category_container');

// removes the parent node and add the categorycode to #delete_cat
function remove_category(childNode){
    cat_list = document.getElementById('category_container');
    cat_list.removeChild(childNode);

    var category_name = childNode.getElementsByClassName('category_name')[0].innerHTML;
    var category_definition = childNode.getElementsByClassName('category_definition')[0].innerHTML;

    delete_cat = document.getElementById('delete_cat');
    cat_ = document.createElement('div');
    cat_.innerHTML = `
        <span class="name">${category_name}</span>
        <span class="definition hide">${category_definition}</span>
        <span style="cursor: pointer;" onclick="add_removed_category(this.parentNode)" style=cursor: pointer; display: flex;">
            <img src="/static?file_name=x-circle-regular-white-24.png" style="height: 20px;">
        </span>
    `;
    delete_cat.appendChild(cat_);
    delete_cat.querySelector('#nothing').classList.add('hide');

    if(document.querySelectorAll('#category_container > div').length == 0){
        cat_list.innerHTML = `<div style="font-size: 18px; height: 58vh; font-style: italic;">No Categories Added to the List</div>`;
    }
}
function display_buffer_changes(value){
    if(value === 'add'){
        document.getElementById('add_cat_').classList.remove('hide');
        document.getElementById('delete_cat_').classList.add('hide');
        document.getElementById('display_buffer_a').classList.add('show_buffer');
        document.getElementById('display_buffer_d').classList.remove('show_buffer');
    } else if(value === 'delete'){
        document.getElementById('delete_cat_').classList.remove('hide');
        document.getElementById('add_cat_').classList.add('hide');
        document.getElementById('display_buffer_d').classList.add('show_buffer');
        document.getElementById('display_buffer_a').classList.remove('show_buffer');
    }
}
function create_category_options(){
    var cat_options = document.getElementById('category_options');
    cat_options.style.display="flex";

    cat_options.innerHTML = `
    <div class="flex column gap-10">
        <div id="more_options_"></div>
        <div class="flex row gap-25" style="justify-content: space-between;">
            <div style="font-size: 19px; font-weight: 600;">
            Add New Category
            </div>
            <div class="flex align-center" onclick="remove_options_for_category()" style="cursor: pointer;">
                <img src="/static?file_name=x-regular-24.png" alt="" style="height: 25px;">
            </div>
        </div>
        <div class="flex column gap-10">
            <div class="flex column gap-5">
                <label for="new_category_name">Name of the Category (4-5 letter only)</label>
                <input type="text" name="new_category_name" id="new_category_name" placeholder="Enter the category code">
            </div>
            <div class='flex column gap-5'>
                <label for="new_category_definition">Definition</label>
                <textarea name="new_category_definition" id="new_category_definition" rows="3"
                placeholder="Enter category definition"></textarea>
            </div>
            <button onclick="add_new_category()" id="add_new_cat">Create</button>
        </div>
    </div>
    `;
    enable_add_cat(1, -1);
}

function modify_category_options(){
    flash_msg.innerHTML = '';
    var cat_options = document.getElementById('category_options');
    cat_options.style.display="flex";

    cat_options.innerHTML = `
    <div class="flex column gap-10">
        <div id="more_options_"></div>
        <div class="flex row gap-25" style="justify-content: space-between;">
            <div style="font-size: 19px; font-weight: 600;">
                Modify Category
            </div>
            <div class="flex align-center" onclick="remove_options_for_category()" style="cursor: pointer;">
                <img src="/static?file_name=x-regular-24.png" alt="" style="height: 25px;">
            </div>
        </div>
        <div class="flex column gap-15" id="modify_category_disp_">
            <div class="flex column gap-5">
                <label for="new_category_name">Select the category to modify</label>
            </div>
        </div>
    </div>
    `;
    var options=[];
    var values=[];
    for(var x of available_cat){
        options.push(x['category'] +" - "+ x['definition']);
        values.push(x['category']);
    }

    var select_t = select_tag(options = options, name='select_category', default_option = 'Select Category', onchange='change_definition(this.value)', value = values);
    select_t.setAttribute('id', 'selectSearch');
    document.getElementById('modify_category_disp_').firstElementChild.appendChild(select_t);
    $('#selectSearch').select2({
        width: '350px'
    });

}

function delete_category_options(){
    flash_msg.innerHTML = '';
    var cat_options = document.getElementById('category_options');
    cat_options.style.display="flex";

    cat_options.innerHTML = `
    <div class="flex column gap-10">
        <div id="more_options_"></div>
        <div class="flex row gap-25" style="justify-content: space-between;">
            <div style="font-size: 19px; font-weight: 600;">
                Delete Category
            </div>
            <div class="flex align-center" onclick="remove_options_for_category()" style="cursor: pointer;">
                <img src="/static?file_name=x-regular-24.png" alt="" style="height: 25px;">
            </div>
        </div>
        <div class="flex column gap-15" id="modify_category_disp_">
            <div class="flex column gap-5">
                <label for="new_category_name">Select the category to Delete</label>
            </div>
        </div>
        <button onclick="delete_category()" id="add_new_cat">
            Delete
        </button>
    </div>
    `;
    var options=[];
    var values=[];
    for(var x of available_cat){
        options.push(x['category'] +" - "+ x['definition']);
        values.push(x['category']);
    }

    var select_t = select_tag(options = options, name='select_category', default_option = 'Select Category', onchange='', value = values);
    select_t.setAttribute('id', 'delete_category_select');
    document.getElementById('modify_category_disp_').firstElementChild.appendChild(select_t);
    $('#delete_category_select').select2({
        width: '350px'
    });
}

// extract the code and the definition of the category from the select statement

function change_definition(value){
    var cat_options = document.getElementById('modify_category_disp_');
    if(cat_options.childElementCount == 2){
        cat_options.removeChild(cat_options.lastElementChild);
    }
    var category = {};
    for(var x of available_cat){
        if(value == x['category']){
            category = x;
            break;
        }
    }
    var _text = document.createElement('div');
    _text.classList.add("flex" ,"column" ,"gap-5");
    _text.innerHTML = `    
            <div class="flex row gap-5" style="font-weight:600;"> 
               <span>Category code : </span> 
               <span id="category_name">${category.category}</span> 
            </div>
            <div class="flex column gap-5"> 
                <label for="new_category_definition">Definition :</label>
                <textarea name="new_category_definition" id="new_category_definition" rows="3"
                placeholder="Enter category definition" style="width: 340px !important;">${category.definition}</textarea> 
            </div>
            <button id="add_new_cat" onclick="modify_old_category('${category.category}', '${category.definition}')">
                Modify
            </button>
    `;
    cat_options.appendChild(_text);
    enable_add_cat(value, -1);
}

function enable_add_cat(value, match_value){
    button_=  document.getElementById('add_new_cat');
    if(value != match_value){
        button_.disabled = false;
        button_.style.backgroundColor = '#0d6efd';
        button_.style.borderColor = '#0d6efd';
    } else{
        button_.disabled = true;
        button_.style.backgroundColor = 'xzgrey';
        button_.style.borderColor = 'grey';
    }
}


// get the code and defitnition
// check if that code exists if not add new code and refresh the page add that code
function add_new_category(){
    var category_name = document.getElementById('new_category_name').value;
    var category_def = document.getElementById('new_category_definition').value; 
    console.log("Creting category .. ", category_name, category_def);
    if( category_name != '' && category_def != '' ){
        var json = {'name': category_name, 'def': category_def };
        display_prog("<div class='loader'></div><div>Creating...</div>", false);
        socket_connect();
        socket.emit('add-new-category', json, (response)=>{
            response = JSON.parse(response);
            console.log(response);
            flash_msg.innerHTML = '';
            if(check_status_code(response)){
                if(response.error){
                    display_prog(response.error);
                } else {
                    document.getElementById('category_options').style.display = 'none';
                    display_prog("Category Created");
                    available_cat = response.response;
                    modify_category_list_display();
                }
            }
        });
    }
}

// extracts the name and def of the category to be modified
// pass data_dict[user_id] for getting the dept in the socket
function modify_old_category(category_name, category_definition){

    flash_msg.innerHTML = '';
    var new_cat_def = document.getElementById('new_category_definition').value;

    if(new_cat_def != '' && new_cat_def !== category_definition){
        
        display_prog("<div class='loader'></div><div>Updating...</div>", false);
        json = {'category' : category_name, 'definition': new_cat_def};
        socket_connect();
        socket.emit('modify_old_category', json, (response)=>{
            response = JSON.parse(response);
            console.log(response);
            if(check_status_code(response)){
                if(response.error){
                    display_prog(response.error);
                } else {
                    document.getElementById('category_options').style.display = 'none';
                    display_prog("Category Updated");
                    available_cat = response.response;
                    modify_category_list_display();
                }
            }
        })

    }
}

function delete_category(){
    var cat_to_del = document.getElementById('delete_category_select').value;
    console.log(cat_to_del);

    display_prog('<div class="loader"></div><div>Removing Category</div>', false);
    if (cat_to_del){
        socket_connect();
        socket.emit('delete-category', cat_to_del, (response)=>{
            response = JSON.parse(response);
            console.log(response);
            if(check_status_code(response)){
                if(response.error){
                    display_prog(response.error);
                } else{
                    display_prog("Category Removed");
                    console.log("Removed..");
                    document.getElementById('category_options').style.display = 'none';
                    available_cat = response.response;
                    modify_category_list_display();
                }
            }
        });
    } else{
        console.log(cat_to_del, "Criteria not present..");
    }
}


function addCategory(category, definition) {
    // Find the cat_listing container
    const catListing = document.getElementById('cat_listing');
    
    // Create a new div element
    const newDiv = document.createElement('div');
    newDiv.classList.add('flex', 'row', 'gap-10','cat_list_item');
    
    // Set the id for the new div
    newDiv.id = category;

    // Create the span elements for the category and definition
    const categorySpan = document.createElement('span');
    categorySpan.textContent = category;

    const separatorSpan = document.createElement('span');
    separatorSpan.textContent = '-';

    const definitionSpan = document.createElement('span');
    definitionSpan.textContent = definition;

    // Append the spans to the new div
    newDiv.appendChild(categorySpan);
    newDiv.appendChild(separatorSpan);
    newDiv.appendChild(definitionSpan);

    // Append the new div to the cat_listing container
    catListing.appendChild(newDiv);
}

function removeAllCategories() {
    // Find the cat_listing container
    const catListing = document.getElementById('cat_listing');
    
    // Remove all child elements
    while (catListing.firstChild) {
        catListing.removeChild(catListing.firstChild);
    }
}

