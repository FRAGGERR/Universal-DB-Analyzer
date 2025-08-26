async function createTestUser() {
  console.log('👤 Creating test user...\n');
  
  try {
    // Register a test user
    const registerResponse = await fetch('http://localhost:5001/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: 'testuser',
        email: 'test@example.com',
        password: 'testpass123',
        firstName: 'Test',
        lastName: 'User'
      })
    });
    
    if (registerResponse.ok) {
      const result = await registerResponse.json();
      console.log('✅ Test user created successfully!');
      console.log('   Username:', result.user.username);
      console.log('   Token:', result.token);
      console.log('\n🔑 Use this token for testing:');
      console.log(result.token);
      return result.token;
    } else {
      // User might already exist, try to login
      console.log('⚠️  User might already exist, trying to login...');
      
      const loginResponse = await fetch('http://localhost:5001/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'testpass123'
        })
      });
      
      if (loginResponse.ok) {
        const result = await loginResponse.json();
        console.log('✅ Login successful!');
        console.log('   Username:', result.user.username);
        console.log('   Token:', result.token);
        console.log('\n🔑 Use this token for testing:');
        console.log(result.token);
        return result.token;
      } else {
        const errorText = await loginResponse.text();
        throw new Error(`Login failed: ${loginResponse.statusText} - ${errorText}`);
      }
    }
    
  } catch (error) {
    console.error('❌ Error creating test user:', error.message);
    return null;
  }
}

// Run the function
createTestUser();
