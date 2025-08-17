# Flask User Management Application

This is a Flask-based user management system that demonstrates common web application bugs and their fixes.

## Bugs Found and Fixed

### Bug 1: SQL Injection Vulnerability (CRITICAL - Security)

**Location**: `get_user()` function in `app.py` (lines 35-50)

**Problem**: 
```python
# VULNERABLE CODE (BEFORE FIX)
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)
```

**Risk**: An attacker could inject malicious SQL code through the username parameter, potentially:
- Accessing unauthorized data
- Modifying database structure
- Executing arbitrary SQL commands

**Example Attack**: 
```
GET /user/admin' OR '1'='1
```

**Fix**: 
```python
# SECURE CODE (AFTER FIX)
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
```

**Why This Fixes It**: Parameterized queries ensure that user input is treated as data, not executable code, preventing SQL injection attacks.

### Bug 2: N+1 Query Problem (Performance Issue)

**Location**: `get_all_users()` function in `app.py` (lines 52-75)

**Problem**: 
```python
# INEFFICIENT CODE (BEFORE FIX)
cursor.execute("SELECT id FROM users")
user_ids = cursor.fetchall()

for user_id in user_ids:
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id[0],))
    # ... process user
```

**Risk**: 
- For N users, this executes N+1 database queries
- Performance degrades linearly with user count
- Database connection overhead increases
- Scalability issues in production

**Fix**: 
```python
# EFFICIENT CODE (AFTER FIX)
cursor.execute("SELECT id, username, email, created_at FROM users")
users_data = cursor.fetchall()

for user in users_data:
    # ... process user data
```

**Why This Fixes It**: Single database query fetches all required data at once, reducing database round trips from N+1 to 1.

### Bug 3: Password Validation Logic Error (Authentication Issue)

**Location**: `login()` function in `app.py` (lines 77-95)

**Problem**: 
```python
# LOGIC ERROR (BEFORE FIX)
if password == stored_password:  # Comparing plain text with hash
```

**Risk**: 
- Login will always fail (password never matches hash)
- Users cannot authenticate
- Application becomes unusable
- Security through obscurity (appears secure but isn't functional)

**Fix**: 
```python
# FIXED CODE (AFTER FIX)
input_password_hash = hashlib.md5(password.encode()).hexdigest()
if input_password_hash == stored_password:
```

**Why This Fixes It**: Both passwords are now hashed using the same algorithm before comparison, enabling proper authentication.

## Additional Security Considerations

While the main bugs are fixed, consider these additional improvements:

1. **Use stronger hashing**: Replace MD5 with bcrypt or Argon2
2. **Environment variables**: Move secret key to environment variables
3. **Input validation**: Add comprehensive input validation
4. **Rate limiting**: Implement rate limiting for login attempts
5. **HTTPS**: Use HTTPS in production
6. **Session security**: Implement proper session invalidation

## Running the Application

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. The application will be available at `http://localhost:5000`

## API Endpoints

- `POST /register` - User registration
- `POST /login` - User authentication  
- `GET /user/<username>` - Get user by username
- `GET /users` - Get all users
- `POST /logout` - User logout

## Testing the Fixes

You can test the fixes by:

1. **SQL Injection**: Try accessing `/user/admin' OR '1'='1` - it should now return an error instead of executing malicious SQL
2. **Performance**: Monitor database queries when calling `/users` endpoint
3. **Authentication**: Register a user and verify you can log in successfully