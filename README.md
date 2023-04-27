# Plants shop

## How to launch web service 
```git clone```

```cd plants_shop```

```docker-compose up```

## Sample data
### Plant:
```
{   
    "id": 10,
    "name": "Jasmine",
    "type": "Flower",
    "sellers": []
}
```
### Seller:
```
{
    "id": 200,
    "name": "Name200",
    "surname": "Surname200"
}
```

Use Postman to test HTTP methods:
```https://www.postman.com/```

## RESTful api

### CREATE:
Create plant:
```curl http://localhost:5000/plants -X POST -d '{"name": "Jasmine", "type": "Flower", "sellers": []}' -H "Content-Type: application/json"```

Create seller:
```curl http://localhost:5000/sellers -X POST -d '{"name": "Name200", "surname": "Surname200"}' -H "Content-Type: application/json"```

Add seller to plant's sellers list:
```curl http://localhost:5000/plants/{id}/sellers -X POST -d '{"id": {seller_id}, "name": "Name200", "surname": "Surname200"}' -H "Content-Type: application/json"```

### READ:
Read plants:
```curl -X GET http://localhost:5000/plants```

Read specific plant:
```curl -X GET http://localhost:5000/plants/{id}```

Read sellers:
```curl -X GET http://localhost:5000/sellers```

Read specific seller:
```curl -X GET http://localhost:5000/sellers/{id}```

Read plant's sellers:
```curl -X GET http://localhost:5000/plants/{id}/sellers```

Read plant's specific seller:
```curl -X GET http://localhost:5000/plants/{id}/sellers/{id}```

### UPDATE:
Update plant:
```curl -X PUT http://localhost:5000/plants/1 -d '{"name": "Red rose", "type": "Summer Flower", "sellers": []}' -H "Content-Type: application/json"```

Update seller:
```curl -X PUT http://localhost:5000/sellers/1 -d '{"name": "Nameful", "surname": "Known"}' -H "Content-Type: application/json"```

Update plant's seller:
```curl -X PUT http://localhost:5000/plants/2/sellers/2 -d '{"name": "NameName", "surname": "SurSurNameName"}' -H "Content-Type: application/json"```

### DELETE:
Delete plant:
```curl -X DELETE http://localhost:5000/plants/{id}```

Delete seller:
```curl -X DELETE http://localhost:5000/sellers/{id}```

Delete plant's seller:
```curl -X DELETE http://localhost:5000/plants/{id}/sellers/{id}```
