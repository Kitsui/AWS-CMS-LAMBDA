
function test() {
    alert("lol");
}   

function saveBlog(title, content, author) {
    //alert(title+content+author);
    var xhr = new XMLHttpRequest();
    var params = JSON.stringify({
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
    alert("askdmaskldmnkls");
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "https://nnih0llbtg.execute-api.us-west-2.amazonaws.com/Test/register", true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.setRequestHeader("x-api-key", "EItAcMzuPs7l1kn9NpFUY1BBwT59FVJW1GIM6cxp");
    xhr.onreadystatechange = function(){
        if(xhr.readyState === 4){
            if(xhr.status === 200){
                alert("GetPosts Successful");
                var data=xhr.responseText;
                var jsonResponse = JSON.parse(data);
                // apply data to div blog-list
                $( ".blog-list" ).text( jsonResponse );
            }
            else{
                alert("Could not get Posts. Please try again later.");
            }
        }
    };
    xhr.send(params);
    return false;
}