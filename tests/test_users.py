# TODO: Uncomment when database and server are available
# async def test_get_user(user):
#     async with client() as c:
#         r = await c.get(f"/users/user/{user['id']}")
#         assert r.status_code == 200

#         r = await c.get(f"/users/user/{user['email']}")
#         assert r.status_code == 200

#         email = "notanemail"
#         r = await c.get(f"/users/user/{email}")
#         assert r.status_code == 422

#         r = await c.get("/users/user/doesnotexist%40example.com")
#         assert r.status_code == 404

#         id = str(uuid4())
#         r = await c.get(f"/users/user/{id[:-1]}")
#         assert r.status_code == 422

#         r = await c.get(f"/users/user/{id}")
#         assert r.status_code == 404
