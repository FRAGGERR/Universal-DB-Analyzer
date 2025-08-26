const fs = require('fs');
const path = require('path');
const FormData = require('form-data');

// Test the complete upload and analysis flow
async function testUploadFlow() {
  console.log('🧪 Testing complete upload and analysis flow...\n');
  
  // Use the valid token from the test user
  const validToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2OGFhOTVlMDlhY2EzNmMwZmM5ZGUzYWMiLCJpYXQiOjE3NTYwMDk5NTMsImV4cCI6MTc1NjYxNDc1M30.7TUJHppwNweT45cZvUr7ptx6aXJgjwcYhoP8QogWe8o';
  
  try {
    // Step 1: Test health endpoint
    console.log('1️⃣ Testing health endpoint...');
    const healthResponse = await fetch('http://localhost:5001/api/health');
    if (healthResponse.ok) {
      const healthData = await healthResponse.json();
      console.log('✅ Health check passed:', healthData.message);
    } else {
      throw new Error(`Health check failed: ${healthResponse.statusText}`);
    }
    
    // Step 2: Test file upload
    console.log('\n2️⃣ Testing file upload...');
    const testDbPath = path.join(__dirname, '..', '..', 'New_DB', 'superheroes.db');
    
    if (!fs.existsSync(testDbPath)) {
      throw new Error(`Test database not found at: ${testDbPath}`);
    }
    
    console.log('   File path:', testDbPath);
    console.log('   File exists:', fs.existsSync(testDbPath));
    console.log('   File size:', fs.statSync(testDbPath).size, 'bytes');
    
    const formData = new FormData();
    const fileBuffer = fs.readFileSync(testDbPath);
    formData.append('file', fileBuffer, 'superheroes.db');
    formData.append('description', 'Test analysis of superheroes database');
    formData.append('tags', 'test,superheroes,database');
    
    console.log('   FormData created with fields:', formData.getHeaders());
    
    const uploadResponse = await fetch('http://localhost:5001/api/analysis/upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${validToken}`,
      },
      body: formData
    });
    
    if (!uploadResponse.ok) {
      const errorText = await uploadResponse.text();
      throw new Error(`Upload failed: ${uploadResponse.statusText} - ${errorText}`);
    }
    
    const uploadResult = await uploadResponse.json();
    console.log('✅ Upload successful:', uploadResult.message);
    console.log('   Analysis ID:', uploadResult.analysis.id);
    
    // Step 3: Monitor analysis progress
    console.log('\n3️⃣ Monitoring analysis progress...');
    const analysisId = uploadResult.analysis.id;
    let analysisComplete = false;
    let attempts = 0;
    const maxAttempts = 30; // 2.5 minutes max
    
    while (!analysisComplete && attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
      
      try {
        const statusResponse = await fetch(`http://localhost:5001/api/analysis/${analysisId}`, {
          headers: {
            'Authorization': `Bearer ${validToken}`,
          }
        });
        
        if (statusResponse.ok) {
          const statusResult = await statusResponse.json();
          const analysis = statusResult.analysis;
          
          console.log(`   Attempt ${attempts + 1}: Status = ${analysis.status}, Progress = ${analysis.progress || 0}%`);
          
          if (analysis.status === 'completed') {
            analysisComplete = true;
            console.log('✅ Analysis completed successfully!');
            console.log('   Processing time:', analysis.processingTime, 'seconds');
            console.log('   Generated files:', analysis.generatedFiles?.length || 0);
            break;
          } else if (analysis.status === 'failed') {
            throw new Error(`Analysis failed: ${analysis.errorMessage || 'Unknown error'}`);
          }
          // Continue polling if still processing
        }
      } catch (error) {
        console.error('   Status check error:', error.message);
      }
      
      attempts++;
    }
    
    if (!analysisComplete) {
      console.log('⚠️  Analysis timed out after', maxAttempts * 5, 'seconds');
    }
    
    console.log('\n🎉 Test completed!');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error('Stack trace:', error.stack);
  }
}

// Run the test
testUploadFlow();
