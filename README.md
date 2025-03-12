# Chat Application
### Installation
 - docker-compose up --build
### API Doc link (need to run application)

-  http://127.0.0.1:8000/api/docs/#/
-  http://127.0.0.1:8000/api/redoc/#/
- Providing postman collection as well except ws:// endpoints (no getting export option of GRPC and websockets in postman)

### User Journey in short for single user 

- User signs up
- User logs in
- User can call users list api to get list of other users or can search  by email address

### One to One conversation
- Expecting frontend to call create conversation api with only one participant before starting conversation
- If conversation exists for given pair of user it will be reused 
- Using conversation id participants will be added to same channels group

### Group Conversation
- Expecting api call to create group with at least one participants(current_user + one participant = 2 members initially)
- can add up to total 10 members in group (including the group owner/current user)
- Using conversation id participants will be added to same channels group



