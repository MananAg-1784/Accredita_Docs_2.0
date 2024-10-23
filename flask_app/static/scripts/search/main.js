
const flash_msg = document.getElementById('flash_messages');

const socket = io("/search", {autoConnect:false});
socket.connect();
socket.on('connect', function(){
    console.log("Socket Connected...");
});
socket.on('disconnect', function(){
    console.log("Socket disconnected...");
});

var activity_file_data_list = {};

function check_status_code(code_data){
    var status = 'status' in code_data ? code_data['status'] : null;
    if(status == 400){
        console.log(code_data['error']);
        flash_msg.innerHTML = '';
        alert(code_data['error']);
        socket.disconnect();
        return 0;
    } else {
        return 1;
    }
}

function socket_connect(){
    if( !socket.connected){
        socket.connect();
    }
}


function get_options_for_response(id){
    var options = document.getElementById(id).options;
    _ = [];
    for( var x of options){
        if(x.value !== 'all'){
            _.push(x.value);
        }
    }
    return _;
}


function search(){
   flash_msg.innerHTML = '<div class="loader"></div><div>Searching Files...</div>';
   document.getElementById('stream_update').innerHTML = '';
   var acc_ = document.getElementById('select_accredition').value;
   console.log("Accredition value : ", acc_)
   var category_ = $('#select_category').val();
   var criteria_ = $('#select_criteria').val();
   var acc_year_ = document.getElementById('select_academic_year').value;
   var acc_month_ = document.getElementById('select_academic_month').value;

   if( acc_ == -1 || !acc_year_.length || !acc_month_.length || (!category_.length && !criteria_.length)){
        flash_msg.innerHTML = 'Required filters not selected';
        return
   }

   var json_data = {year: parseInt(acc_year_), month: parseInt(acc_month_), accredition: acc_};
    socket_connect();
    if(category_.length > 0){
        console.log("Search using category");
        if(category_[0] == 'all'){
            json_data.category = get_options_for_response('select_category');
        } else{
            json_data.category = category_;
        }
        console.log(json_data);
        socket.emit('search_using_category', json_data, (response)=>{
            response = JSON.parse(response);
            console.log("Recieved data...", response);
            if(check_status_code(response)){
                if(response.error){
                    flash_msg.innerHTML = response.error;
                } else{
                    flash_msg.innerHTML = "";
                }
                document.getElementById('search_results').innerHTML = response.response.data_list;
                activity_file_data_list = response.response.data_item_list;
                $('#search_files').select2({
                    width: '330px',
                    allowClear: true,
                    placeholder:"Search for specific files",
                    closeOnSelect: true
                });
                $("#search_files").val('').trigger("change");
            }
        });
    } else if(criteria_.length > 0){
        console.log("Search using criteria");
        if(criteria_[0] == 'all'){
            json_data.criteria = get_options_for_response('select_criteria');
        } else{
            json_data.criteria = criteria_;
        }
        console.log(json_data);
        socket.emit('search_using_criteria', json_data, (response)=>{
            response = JSON.parse(response);
            console.log("Recieved data...", response);
            if(check_status_code(response)){
                if(response.error){
                    flash_msg.innerHTML = response.error;
                } else{
                    flash_msg.innerHTML = "";
                }
                document.getElementById('search_results').innerHTML = response.response.data_list;
                activity_file_data_list = response.response.data_item_list;
                $('#search_files').select2({
                    width: '330px',
                    allowClear: true,
                    placeholder:"Search for specific files",
                    closeOnSelect: true
                });
                $("#search_files").val('').trigger("change");
                remove_extra();
                remove_extra();
            }
        });
    } else{
        console.log("No Filter to search for")
    }

    internal_storage = {
        accredition: acc_,
        category: category_,
        criteria: criteria_,
        year: acc_year_,
        month: acc_month_
       };
    // adding the data to the internal storage
    internal_storage = JSON.stringify(internal_storage);
    localStorage.setItem("search_options", internal_storage);
}

socket.on('stream_updated',(response)=>{
    console.log("Stream Updated : ",response);
    response = JSON.parse(response);
    flash_msg.innerHTML = ""; 
    if (response.data === 1){
        document.getElementById('stream_update').innerHTML = `<div class="loader"></div><div>Checking for updates...</div>`;
    } else if(response.data === 2){
        document.getElementById('stream_update').innerHTML = '';
    } else {
        document.getElementById('stream_update').innerHTML = response.data;
    }
});

function redirect_to_file(data_item){
    console.log(data_item);
    var cat = document.querySelectorAll('.data_item');
    console.log(cat);
    if(data_item != '')
    {   
        flag = 0;
        for(var x of cat){
            var files = x.querySelectorAll('.files_data');
            console.log(files);
            for(var _ of files){
                if(_.id === data_item){
                    flag = 1;
                    break;
                }
            }
            if(flag == 1){
                x.classList.remove('hide');
                x.querySelector('.files_list').classList.remove('hide');
                flag = 0;
            } else{
                x.classList.add('hide');
            }
        }
    } else{
        console.log(cat);
        for(var x of cat){
            x.classList.remove('hide');
            try{
                x.querySelector('.files_list').classList.add('hide');
            }
            catch{
                
            }
        }
    }
}

function display_files_list(id){
    var view_ = document.querySelector(`#${id} .files_list`);
    var class_ = view_.classList;
    if(class_.contains('hide')){
        class_.remove('hide');
    } else{
        class_.add('hide');
    }

}

function display_type(value){
    var data_items = document.getElementsByClassName('data_item');
    for(var x of data_items){
        var file_count = x.querySelector('.no-files');
        // Without files
        if(value === '1'){
            if(file_count){
                x.classList.remove('hide');
            } else{
                x.classList.add('hide');
            }
        } else if(value === '2'){  // with files
            if(!file_count){
                x.classList.remove('hide');
            } else{
                x.classList.add('hide');
            }
        } else { // all data
            x.classList.remove('hide');
        }
    }
}

// more options - for file
function rename_file(data_item, name){
    display_ = document.getElementById('overlay');
    display_.style.display = 'flex';
    display_.innerHTML = `
    <div class="flex column gap-10">
        <div class="flex row gap-25" style="justify-content: space-between;">
            <div style="font-size: 19px; font-weight: 600;">
             Renaming the File
            </div>
            <div class="flex align-center" onclick="remove_options_for_overlay()" style="cursor: pointer;">
                <img src="/static?file_name=x-regular-24.png" alt="" style="height: 25px;">
            </div>
        </div>
        <div class="flex column gap-15">
            <div class="flex column gap-5" id="new_file_name_">
                <div>Change or Add File Name</div>
                <input type="text" name="renamed_file" id="renamed_file" placeholder="New File Name" style="width: 350px; font-size:16px;">
            </div>
            <div class="flex column gap-5" id="add_category_disp_options">
            <div>Add Category to the file</div>
            <select id="select_renamed_category" onchange="rename_file_name('${name}')" multiple="multiple" style="width: 250px;">
            </select>
            </div>
            <div class="flex row gap-15">
                <div style="padding: 4.5px 10px;background-color: #0d6efd;color: #fff;align-self: flex-start;border-radius: 5px; cursor:pointer;" onclick="rename_file_submit('${data_item}','${name}')">
                    Rename
                </div>
            </div>
        </div>
    </div>
    `;
    document.getElementById('renamed_file').value = name;
    select_ = document.querySelector("#select_renamed_category");
   
    $(select_).select2({
        width: '340px',
        closeOnSelect: true,
        alowClear: true,
        placeholder: 'Select new file Category',
        templateSelection: category_selection_text
    });
   
    options = [];
    values= [];
    console.log("Adding all categories");
    for(x of category){
        options.push(x.category);
        values.push( x.definition+' - '+x.category );
    }
    if(options.length >=1 ){
        console.log(options.length);
        for (i = 0; i < options.length; i++) {
            let option = new Option(values[i], options[i]);
            select_.add(option, undefined);
        }
    } else{
        flash_msg.innerHTML = 'Reload and Try Again...';
    }

    $(select_).val('').trigger('change');
}

function rename_file_name(name){
    name_ = document.getElementById('renamed_file').value;
    let parts = name_.split(/_/);
    console.log(parts);
    categories = $(`#select_renamed_category`).val();
    console.log(categories);
    if(categories == null || categories.length == 0){
        document.getElementById('renamed_file').value = name;
        return
    }

    var cat_  = '';
    for(var x of categories){
        cat_ += x +',';
    }
    name_ = parts[0]+'_'+ cat_.slice(0,cat_.length-1);
    for(var _ = 2; _ < parts.length; _++){
        name_ += '_'+parts[_]
    }
    console.log(name_)

    document.getElementById('renamed_file').value = name_;
}

function rename_file_submit(data_item,name){
    console.log("item_no : ", data_item);
    var drive_id = activity_file_data_list[data_item];
    console.log(drive_id);

    new_name = document.getElementById('renamed_file').value;
    categories = $(`#select_renamed_category`).val();

    console.log(new_name);
    console.log(categories);
    json = {'drive_id': drive_id, 'name':name,'new_name': new_name, 'categories': categories};
    document.getElementById('display_options_response').classList.remove('hide');
    document.getElementById('display_options_response').innerHTML = `
    <div class="flex row gap-10" style="padding-right: 10px">
    <div class="loader"></div><div>Renaming File</div>
    </div>
    `;
    socket.emit('rename_file',(json), (response)=>{
        response = JSON.parse(response);
        console.log(response);
        if(check_status_code(response)){
            var display_ = "";
            if(response.error){
                display_ = response.error;
            } else {
                display_ = response.response;
                document.getElementById('overlay').style.display = 'none';
            }
            document.getElementById('display_options_response').innerHTML = `
            <div>${display_}</div>
            <div class="flex align-center" onclick="remove_activity_log()"> 
                <img src="/static?file_name=x-regular-white-24.png">
            </div>
            `;
           
            setTimeout(() => {
                document.getElementById('display_options_response').classList.add('hide');
            }, 5000);
        }
    })
}

function remove_activity_log(){
    document.getElementById('display_options_response').innerHTML = '';
    document.getElementById('display_options_response').classList.add('hide');
}


function delete_file(data_item){
    var drive_id = activity_file_data_list[data_item];
    console.log(drive_id);
    // move the file to trash 
    action = 'trash';   
    document.getElementById('display_options_response').innerHTML = `
    <div class="flex row gap-10" style="padding-right: 10px">
    <div class="loader"></div><div>Trashing File</div>
    </div>
    `;
    
    json = {'drive_id': drive_id, 'action': action};
    document.getElementById('display_options_response').classList.remove('hide');
    socket.emit('delete_file',(json), (response)=>{
        response = JSON.parse(response);
        console.log(response);
        if(check_status_code(response)){
            var display_ = "";
            if(response.error){
                display_ = response.error;
            } else {
                display_ = response.response;
            }
            document.getElementById('display_options_response').innerHTML = `
            <div>${display_}</div>
            <div class="flex align-center" onclick="remove_activity_log()">
                <img src="/static?file_name=x-regular-white-24.png">
            </div>
            `;
           
            setTimeout(() => {
                document.getElementById('display_options_response').classList.add('hide');
            }, 5000);
        }
    })
}

function remove_options_for_overlay(){
    document.getElementById("overlay").style.display = 'none';
}

function remove_extra(){
    a = document.querySelectorAll("#data_container > div");
    f = []
    for(let i of a){
        d = i.getElementsByClassName("files_data");
        f = []
        for(let x of d){
            file_name = x.getElementsByClassName("file_name")[0].innerHTML.trim();
            file_time = x.getElementsByClassName("file_time")[0].innerHTML.trim();
            exists = false;
            for(xx of f){
                if(xx.name == file_name && xx.time == file_time){
                exists = true;
                break;
                }
            }
            if(exists){
                x.remove();
                console.log("Present");
            }else{
                f.push({name:file_name, time: file_time})
            }
        }
        i.getElementsByClassName('files_count')[0].innerHTML = f.length;
        console.log("Final length : ", f.length);

    }
}