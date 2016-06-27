
window.onload = function() {
    // init function
    bindClickEvents();
}

function bindClickEvents() {
    // bind events

    // bind register button 
    document.getElementById("email_form").onsubmit = function() {
            registerUser(document.getElementById("usernameInput").value, 
                document.getElementById("emailInput").value, 
                document.getElementById("passwordInput").value);
            return false;
    }

    

}



/***
* posts to the server using the arguments given from the Web Page
*
***/
function postToServer(params, stateChangeFunc) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "https://mvmc85y3c0.execute-api.us-east-1.amazonaws.com/prod", true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.setRequestHeader("x-api-key", "I1Q7GanG5U68KTNFIIqsZ7TL2k90z3s76ulEXsS8");
    xhr.onreadystatechange = stateChangeFunc(xhr);
    xhr.send(params);
    return false;
}





function saveBlog(title, content, author) {
    var params = JSON.stringify({
        request: "saveNewBlog",
        blog:{ 
            title: title,
            content: content,
            author : author
        }
    });

    postToServer(params, saveBlogStateChange);
}
function saveBlogStateChange(xhr) {
    if(xhr.readyState === 4){
        if(xhr.status === 200){
            alert("Save New Post Successful");
        }
        else{
            alert("Could not save new Post. Please try again later.");
        }
    }
}





function registerUser(username, email, password) {
    alert(username + email + password)
    var params = JSON.stringify({
        request: "registerUser",
        user:{ 
            username: username, 
            email: email,
            password: password
        }
    });

    postToServer(params, registerUserStateChange);
}
function registerUserStateChange(xhr){
    if(xhr.readyState === 4){
        if(xhr.status === 200){
            alert("You are registered!");
        }
        else{
            alert("Could not register. Please try again later.");
        }
    }
}





function editBlog(id, title, content, author) {
    alert("edit called");
    var params = JSON.stringify({
        request: "editBlog",
        blog:{
            blogID: id,
            title: title,
            content: content,
            author : author
        }
    });

    postToServer(params, editBlogStateChange);
    
}
function editBlogStateChange(xhr) {
    if(xhr.readyState === 4){
        if(xhr.status === 200){
            alert("Edit Post Successful");
        }
        else{
            alert("Could not Edit Post. Please try again later.");
        }
    }
}






function getBlogs() {
    var params = JSON.stringify({
       request: "getBlogs" 
    });

    postToServer(params, getBlogsStateChange);
}
function getBlogsStateChange(xhr){
    if(xhr.readyState === 4){
        if(xhr.status === 200){
            alert("Get Blogs Successful");
            var data=xhr.responseText;
            var jsonResponse = JSON.parse(data);
            // apply data to div blog-list
            $( ".blog-list" ).text( jsonResponse );
        }
        else{
            alert("Could not get Blogs. Please try again later.");
        }
    }
}



function getSingleBlogData(blogID, author) {
    alert(blogID + author);
    var params = JSON.stringify({
       request: "getBlogData",
       blog: {
           blogID: blogID,
           author: author
       }
    });

    postToServer(params, getSingleBlogDataStateChange);
}
function getSingleBlogDataStateChange(xhr){
    if(xhr.readyState === 4){
        if(xhr.status === 200){
            alert("Get single Blog Successful");
            var data=xhr.responseText;
            var jsonResponse = JSON.parse(data);
            // apply data to div blog-list
            $( ".blog-list" ).text( jsonResponse );
        }
        else{
            alert("Could not get single Blog. Please try again later.");
        }
    }
}




function deleteSingleBlog(blogID, author) {
    alert(blogID + author);
    var params = JSON.stringify({
       request: "deleteSingleBlog",
       blog: {
           blogID: blogID,
           author: author
       }
    });

    postToServer(params, deleteSingleBlogStateChange);
}
function deleteSingleBlogStateChange(xhr){
        if(xhr.readyState === 4){
            if(xhr.status === 200){
                alert("Delete single Blog Successful");
                var data=xhr.responseText;
                var jsonResponse = JSON.parse(data);
                // apply data to div blog-list
                $( ".blog-list" ).text( jsonResponse );
                //refresh list of blogs
            }
            else{
                alert("Could not delete single Blog. Please try again later.");
            }
        }
    };
