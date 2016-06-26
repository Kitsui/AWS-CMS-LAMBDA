
function test() {
    alert("lol");
}   

function saveBlog(title, content, author) {
    //alert(title+content+author);
    var xhr = new XMLHttpRequest();
    var params = JSON.stringify({
        requestType: "saveNewBlog",
        blog:{ 
            Title: title,
            Content: content,
            Author : author
        }
    });
    xhr.open("POST", "https://nnih0llbtg.execute-api.us-west-2.amazonaws.com/Test/register", true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.setRequestHeader("x-api-key", "EItAcMzuPs7l1kn9NpFUY1BBwT59FVJW1GIM6cxp");
    xhr.onreadystatechange = function(){
        if(xhr.readyState === 4){
            if(xhr.status === 200){
                alert("Post Successful");
            }
            else{
                alert("Could not Post. Please try again later.");
            }
        }
    };
    xhr.send(params);
    return false;
}

function getBlogs() {
    //alert("askdmaskldmnkls");
    var xhr = new XMLHttpRequest();
    var params = JSON.stringify({
       requestType: "getBlogs" 
    });
    xhr.open("POST", "https://nnih0llbtg.execute-api.us-west-2.amazonaws.com/Test/register", true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.setRequestHeader("x-api-key", "EItAcMzuPs7l1kn9NpFUY1BBwT59FVJW1GIM6cxp");
    xhr.onreadystatechange = function(){
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
    };
    xhr.send(params);
    return false;
}

function getSingleBlogData(blogID, author) {
    alert(blogID + author);
    var xhr = new XMLHttpRequest();
    var params = JSON.stringify({
       requestType: "getBlogData",
       Blog: {
           BlogID: blogID,
           Author: author
       }
    });
    xhr.open("POST", "https://nnih0llbtg.execute-api.us-west-2.amazonaws.com/Test/register", true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.setRequestHeader("x-api-key", "EItAcMzuPs7l1kn9NpFUY1BBwT59FVJW1GIM6cxp");
    xhr.onreadystatechange = function(){
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
    };
    xhr.send(params);
    return false;
}

function DeleteSingleBlog(blogID, author) {
    alert(blogID + author);
    var xhr = new XMLHttpRequest();
    var params = JSON.stringify({
       requestType: "deleteSingleBlog",
       Blog: {
           BlogID: blogID,
           Author: author
       }
    });
    xhr.open("POST", "https://nnih0llbtg.execute-api.us-west-2.amazonaws.com/Test/register", true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.setRequestHeader("x-api-key", "EItAcMzuPs7l1kn9NpFUY1BBwT59FVJW1GIM6cxp");
    xhr.onreadystatechange = function(){
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
    xhr.send(params);
    return false;
}