
### Database Schema : 
You can access it via [DrawSQL](https://drawsql.app/teams/safi-2/diagrams/junction)

![App Screenshot](https://i.ibb.co/0Kmp0CQ/junction-schema.png)

## Tech Used

- **Back-End**: Django, Django REST framework
- **Database**: Sqlite3 for simplicity, you can use any another relational database (MySQL , PostgreSQL)
- **Authentication**: JWT (JSON Web Tokens)

## End Points

- **api/register/** :
  let the user sign up , add him to the selected group of users . returns a response of the **{access token & the refresh token}**
- **api/signin/** :
  let the user signin , . returns a response of the **{access token & the refresh token}**

- **api/token/refresh** :
  returns a new access token by submitting the refresh token if its not expired .

- **api/getUser/** :
  returns the info of the user making the request

- **api/dashboard/** :
  based on the type of the user making the request , this endpoint returns the appropriate data for the dashboard

- **api/dashboard/parent/** :
  returns the info the childs of the parent makeing the request . also offers the possibility of POST request for adding more childs

- **api/task/<int: task_id >/** :

  GET : return the task with task_id
  PUT : update the status of completing of the task

- **api/task/<int: task_id >/** :

  GET : return all the chat of the course (
  all the messages , the videos , and tasks
  )

  POST : offers the instructor to post a new course material to the course with id= course_id
  the material may differ between a task for all the students in the course or a video

++ Others ( i am too lazy to list them )
