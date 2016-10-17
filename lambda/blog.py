"""
# blog.py
# Author: Adam Campbell
# Date: 23/06/2016
# Edited: N/D        | Miguel Saavedra
#         29/07/2016 | Christopher Treadgold
#         07/08/2016 | Christopher Treadgold
#         12/09/2016 | Christopher Treadgold
"""

import datetime
import json
import uuid

import boto3
import botocore

class Blog(object):
    """ Provides functions for handling blog related requests """
    
    @staticmethod
    def get_all_blogs(blog_table):
        """ Fetches all entries from the blog table """
        try:
            dynamodb = boto3.client("dynamodb")
            blogs = dynamodb.scan(
                TableName=blog_table, ConsistentRead=True, 
                ProjectionExpression="ID, Author, Description, Keywords, SavedDate, Title"
            )
        except botocore.exceptions.ClientError as e:
            action = "Fetching blogs from the blog table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the blog id has a blog associated with it
        if not "Items" in blogs:
            action = "Fetching blogs from the blog table"
            return {"error": "noBlogs", "data": {"action": action}}
        
        return {"message": "Successfully fetched blogs", "data": blogs["Items"]}
    
    @staticmethod
    def get_blog(blog_id, blog_table):
        """ Fetches a blog entry from the blog table """
        try:
            dynamodb = boto3.client("dynamodb")
            blog = dynamodb.get_item(
                TableName=blog_table, Key={"ID": {"S": blog_id}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Fetching blog from the blog table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the blog id has a blog associated with it
        if not "Item" in blog:
            action = "Fetching blog from the blog table"
            return {"error": "InvalidBlogID",
                    "data": {"id": blog_id, "action": action}}

        return {"message": "Successfully fetched blog", "data": blog["Item"]}
    
    @staticmethod
    def edit_blog(blog_id, title, content, description, keywords, blog_table,
                  bucket):
        """ Edits a blog """
        # Create the blog entry
        current_blog = Blog.get_blog(blog_id, blog_table)
        if "error" in current_blog:
            return current_blog
            
        blog = current_blog["data"]
        blog["Title"]["S"] = title
        blog["Content"]["S"] = content
        blog["Description"]["S"] = description
        blog["Keywords"]["L"] = []
        for keyword in keywords:
            blog["Keywords"]["L"].append({"S": keyword})
        blog_for_s3 = {
            "ID": blog["ID"]["S"],
            "Title": title,
            "Author": blog["Author"]["S"],
            "SavedDate": blog["SavedDate"]["S"],
            "Content": content,
            "Description": description,
            "Keywords": keywords
        }
        
        # Put the blog in the blog table
        try:
            dynamodb = boto3.client("dynamodb")
            put_response = dynamodb.put_item(
                TableName=blog_table, Item=blog, ReturnConsumedCapacity="TOTAL"
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting blog in the blog table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # TODO: Add paging table
        Blog.update_blog_list(blog_id, bucket)
        
        # Add blog as json to bucket
        try:
            s3 = boto3.client("s3")
            s3.put_object(
                Bucket=bucket, ACL="public-read", Body=json.dumps(blog_for_s3),
                Key=("Content/Post/%s.json" % blog_for_s3["ID"]),
                ContentType="application/json"
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting blog in the bucket"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        return {"message": "Successfully put blog", "data": blog}
    
    @staticmethod
    def put_blog(author, title, content, description, keywords, blog_table,
                 bucket):
        """ Puts a blog in the blog table """
        # Create the blog entry
        saved_date = datetime.datetime.utcnow()
        saved_date = saved_date.strftime("%d-%b-%Y %H:%M UTC")
        blog_uuid = str(uuid.uuid4())
        blog = {
            "ID": {"S": blog_uuid},
            "SavedDate": {"S": saved_date},
            "Author": {"S": author},
            "Title": {"S": title},
            "Content": {"S": content},
            "Description": {"S": description},
            "Keywords": {"L": []}
        }
        for keyword in keywords:
            blog["Keywords"]["L"].append({"S": keyword})
        blog_for_s3 = {
            "ID": blog_uuid,
            "SavedDate": saved_date,
            "Author": author,
            "Title": title,
            "Content": content,
            "Description": description,
            "Keywords": keywords
        }
        
        # Put the blog in the blog table
        try:
            dynamodb = boto3.client("dynamodb")
            put_response = dynamodb.put_item(
                TableName=blog_table, Item=blog, ReturnConsumedCapacity="TOTAL"
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting blog in the blog table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # TODO: Add paging table
        Blog.update_blog_list(blog_uuid, bucket)
        
        # Add blog as json to bucket
        try:
            s3 = boto3.client("s3")
            s3.put_object(
                Bucket=bucket, ACL="public-read", Body=json.dumps(blog_for_s3),
                Key=("Content/Post/%s.json" % blog_for_s3["ID"]),
                ContentType="application/json"
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting blog in the bucket"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        return {"message": "Successfully put blog", "data": blog}

    @staticmethod
    def generate_new_blog_list(blog_table, bucket):
        """ Generates data to override the post list in s3 """
        # Get existing blogs in blog table
        items = Blog.get_all_blogs(blog_table)["data"]
        
        # Order by datetime
        items.sort(key=lambda x: datetime.datetime.strptime(x['SavedDate']['S'], 
            '%d-%b-%Y %H:%M UTC'))
        items.reverse()
        # Extract ID's amd put into list
        blogList = []
        subBlogList = []
        # Create package and fill it with list of lists
        package = {}
        for item in items:
            blogList.append(item["ID"]["S"])
        
        
        # Counters
        index = 0
        packageIndex = 0

        for item in blogList:
            index+=1
            # Append new Item to sub list
            subBlogList.append(item)
            # If counter equals 10 then add sublist to BlogList
            # Chunk list into lists of 10 in length
            if index%10==0 and index != 0:
                # increment package index
                packageIndex += 1
                package[packageIndex] = subBlogList
                # Reset List
                subBlogList = []
            # If Last element and not the 10th element then add to BlogList
            elif index==len(blogList):
                packageIndex += 1
                package[packageIndex] = subBlogList
        
        fileName= "Content/post_list.json"
        Blog.put_blog_list(bucket, fileName, package)

    @staticmethod
    def update_blog_list(blogID, bucket):
        """ Puts a blog in the blog list file """
        # Init Dict size
        dictSize = 0
        # Init set amount per array
        maxSize = 10;
        # file name of post list
        fileName= "Content/post_list.json"
        # Read in post list and put into json variable
        try:
            s3 = boto3.client('s3')
            get_kwargs = {
                'Bucket': bucket,
                'Key': fileName
            }
            result =  s3.get_object(**get_kwargs)
        except botocore.exceptions.ClientError as e:
            action = "Putting blog id in the post list file"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        # Json variable
        object_body = json.loads(result['Body'].read());
        # set dict size
        dictSize = len(object_body)
        # If size is not 0
        if object_body:
            # Check size of each array
            for key in object_body:
                # Decrement Counter
                dictSize-=1
                print dictSize
                # If check if space in array
                if len(object_body[key]) < maxSize:
                    object_body[key].append(blogID)
                else:
                    if dictSize == 0:
                        # Else create new item with a value of key index + 1
                        object_body[len(object_body)+1] = [blogID]
                        break

        # Else create the first item in dictionary
        else:
            object_body[1] = [blogID]
        # Add blog id as json to json file
        Blog.put_blog_list(bucket, fileName, object_body)

    @staticmethod
    def put_blog_list(bucket, fileName, object_body):
        """ Overrides post list in s3 """
        try:
            s3 = boto3.client("s3")
            s3.put_object(
                Bucket=bucket, ACL="public-read", Body=json.dumps(object_body),
                Key=(fileName),
                ContentType="application/json"
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting blog id in the post list file"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
 
    @staticmethod
    def delete_blog(blog_id, blog_table, bucket):
        """ Deletes a blog from the blog table """
        # Generate new post list in S3
        Blog.generate_new_blog_list(blog_table, bucket)
        try:
            dynamodb = boto3.client("dynamodb")
            delete_response = dynamodb.delete_item(
                TableName=blog_table,
                Key={"ID": {"S": blog_id}},
                ConditionExpression="attribute_exists(ID)"
            )
        except botocore.exceptions.ClientError as e:
            action = "Deleting blog from the blog table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # TODO: Modify once pagination is implemented
        
        # Deletes the blog from the bucket
        try:
            s3 = boto3.client("s3")
            delete_response = s3.delete_object(
                Bucket=bucket,
                Key=("Content/Post/%s.json" % blog_id)
            )
        except botocore.exceptions.ClientError as e:
            action = "Deleting blog from the blog table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        return {"message": "Successfully deleted blog"}
        return  {"message" : Blog.generate_new_blog_list(blog_table, bucket)}